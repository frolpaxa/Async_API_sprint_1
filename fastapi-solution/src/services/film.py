from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.models import Film, MultiParams
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def es_pagination(page_number: int, page_count: int) -> tuple[int, int]:
    number = min((page_number - 1) * page_count, 10000)
    count = min(page_count, 10000 - number)
    return number, count


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_list(
        self,
        title: str,
        imdb_rating: str,
        genre: Optional[list[str]],
        director: Optional[str],
        multi_params: Optional[MultiParams],
        page_number: int,
        page_count: int,
    ) -> list[Film]:
        """
        Получаем данные фильмов с возможностью фильтрации и сортировки
        """

        search_from, search_size = es_pagination(page_number, page_count)
        if not search_size:
            return []

        sort = []

        if imdb_rating:
            sort.append(
                {
                    "imdb_rating": {"order": imdb_rating.value},
                },
            )

        query = {
            "bool": {
                "must": [],
                "filter": [],
            },
        }

        if title:
            query["bool"]["must"].append({"match": {"title": title}})

        if genre:
            for g in genre:
                query["bool"]["filter"].append({"term": {"genre": g.value}})

        if multi_params:
            if multi_params.writers:
                for writer in multi_params.writers:
                    query["bool"]["must"].append(
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": writer}},
                            }
                        }
                    )

            if multi_params.actors:
                for actor in multi_params.actors:
                    query["bool"]["must"].append(
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": actor}},
                            }
                        }
                    )

        if director:
            query["bool"]["must"].append({"match": {"director": director}})

        body = {
            "sort": sort,
            "_source": list(Film.__fields__.keys()),
            "from": search_from,
            "size": search_size,
        }

        if query:
            body["query"] = query

        films_search = await self.elastic.search(
            body=body,
            index="movies",
        )

        return [Film(**doc["_source"]) for doc in films_search["hits"]["hits"]]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
