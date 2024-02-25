from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import UUID

import orjson
from fastapi import Query
# Используем pydantic для упрощения работы
# при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes,
    # а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    id: UUID

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: Optional[float] = None
    title: str
    description: Optional[str] = None
    genre: Optional[list[str]]
    director: Optional[str] = None
    actors_names: Optional[str] = None
    writers_names: Optional[list[str]] = None
    actors: Optional[list[Person]] = None
    writers: Optional[list[Person]] = None


class GenreType(Enum):
    Action = "Action"
    Adventure = "Adventure"
    Animation = "Animation"
    Biography = "Biography"
    Comedy = "Comedy"
    Crime = "Crime"
    Documentary = "Documentary"
    Drama = "Drama"
    Family = "Family"
    Fantasy = "Fantasy"
    Game_Show = "Game-Show"
    History = "History"
    Horror = "Horror"
    Music = "Music"
    Musical = "Musical"
    Mystery = "Mystery"
    News = "News"
    Reality_TV = "Reality-TV"
    Romance = "Romance"
    Sci_Fi = "Sci-Fi"
    Short = "Short"
    Sport = "Sport"
    Talk_Show = "Talk-Show"
    Thriller = "Thriller"
    War = "War"
    Western = "Western"


class Sort(Enum):
    asc = "asc"
    desc = "desc"


@dataclass
class MultiParams:
    writers: list[str] = Query(None)
    actors: list[str] = Query(None)
