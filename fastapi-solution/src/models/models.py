from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from fastapi import Query

# Используем pydantic для упрощения работы
# при перегонке данных из json в объекты
from pydantic import BaseModel


class Base(BaseModel):
    id: UUID


class PersonM(BaseModel):
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
    actors: list[PersonM] | None = None
    writers: list[PersonM] | None = None


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


class Person(BaseModel):
    id: str
    full_name: str


class Genre(BaseModel):
    id: str
    name: str
