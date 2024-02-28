from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.models import Person
from redis.asyncio import Redis

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def es_pagination(page_number: int, page_count: int) -> tuple[int, int]:
    number = min((page_number - 1) * page_count, 10000)
    count = min(page_count, 10000 - number)
    return number, count


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)

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
            "_source": list(Person.__fields__.keys()),
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


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
