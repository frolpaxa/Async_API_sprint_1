from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from fastapi import Query

# Используем pydantic для упрощения работы
# при перегонке данных из json в объекты
from pydantic import BaseModel


class Base(BaseModel):
    id: UUID


class PersonShort(BaseModel):
    id: str
    name: str


class FilmShort(BaseModel):
    id: str
    title: str


class Film(BaseModel):
    id: str
    imdb_rating: float | None = None
    title: str
    description: str | None = None
    genre: list[str] | None = None
    director: str | None = None
    actors_names: str | None = None
    writers_names: list[str] | None = None
    actors: list[PersonShort] | None = None
    writers: list[PersonShort] | None = None


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


class FilmPerson(BaseModel):
    id: str
    roles: list[str]


class Person(BaseModel):
    id: str
    full_name: str
    films: list[FilmPerson] | None


class Genre(BaseModel):
    id: str
    name: str


@dataclass
class QueryParams:
    query: str | None = Query(..., alias="query")
    page: int = Query(default=1, alias="page_number", ge=1)
    size: int = Query(default=25, alias="page_size", ge=1, le=100)
