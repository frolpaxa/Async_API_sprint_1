from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.models import Genre
from redis.asyncio import Redis

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def es_pagination(page_number: int, page_count: int) -> tuple[int, int]:
    number = min((page_number - 1) * page_count, 10000)
    count = min(page_count, 10000 - number)
    return number, count


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index="genres", id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.id, genre.json(), GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def get_list(
        self,
        name: str,
        page_number: int,
        page_count: int,
    ) -> list[Genre]:
        """
        Получаем данные жанров с возможностью фильтрации и сортировки
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

        if name:
            query["bool"]["must"].append({"match": {"name": name}})

        body = {
            "_source": list(Genre.__fields__.keys()),
            "from": search_from,
            "size": search_size,
        }

        if query:
            body["query"] = query

        genre_search = await self.elastic.search(
            body=body,
            index="genres",
        )

        return [Genre(**doc["_source"]) for doc in genre_search["hits"]["hits"]]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
