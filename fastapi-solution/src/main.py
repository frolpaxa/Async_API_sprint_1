import sys
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

sys.path.append("/opt/app/src")

from api.v1 import films, genres, persons
from core.config import Settings
from db import elastic, redis

config = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=config.redis_host, port=config.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.elastic_host}:{config.elastic_port}"]
    )
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=config.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
