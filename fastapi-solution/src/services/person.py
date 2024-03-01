from functools import lru_cache

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.models import Person
from redis.asyncio import Redis

from models.models import QueryParams

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def es_pagination(page_number: int, page_count: int) -> tuple[int, int]:
    number = min((page_number - 1) * page_count, 10000)
    count = min(page_count, 10000 - number)
    return number, count


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Person | None:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> Person | None:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Person | None:
        data = await self.redis.get(f"person-{person_id}")
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            f"person-{person.id}",
            person.model_dump_json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_list(
        self,
        full_name: str,
        page_number: int,
        page_count: int,
    ) -> list[Person]:
        """
        Получаем данные персон с возможностью фильтрации и сортировки
        """

        search_from, search_size = es_pagination(page_number, page_count)
        if not search_size:
            return []

        query = {
            "bool": {
                "must": [],
                "filter": [],
            },
        }

        if full_name:
            query["bool"]["must"].append({"match": {"full_name": full_name}})

        body = {
            "_source": list(Person.model_fields.keys()),
            "from": search_from,
            "size": search_size,
        }

        if query:
            body["query"] = query

        films_search = await self.elastic.search(
            body=body,
            index="persons",
        )

        return [Person(**doc["_source"]) for doc in films_search["hits"]["hits"]]

    async def search_persons(self, query: QueryParams) -> list[Person] | None:
        """
        Полнотекстовый поиск персон по query
        """

        body = {
            "size": query.size,
            "from": (query.page - 1) * query.size,
            "query": {"match_all": {}},
        }

        if query.query:
            body["query"] = {
                "simple_query_string": {
                    "query": query.query,
                    "fields": ["id", "full_name", "role"],
                    "default_operator": "or",
                }
            }

        try:

            data = await self.elastic.search(index="persons", body=body)
            return [item["_source"] for item in data["hits"]["hits"]]

        except NotFoundError:
            return None


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
