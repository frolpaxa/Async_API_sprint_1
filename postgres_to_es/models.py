from typing import Optional

from pydantic import BaseModel, Field

ROLES = {
    "actors": "actor",
    "actors_names": "actor",
    "director": "director",
    "writers": "writer",
    "writers_names": "writer",
}


class PersonM(BaseModel):
    id: str = Field(alias="person_id", default=None)
    name: str = Field(alias="person_name", default=None)


class Movie(BaseModel):
    id: str
    imdb_rating: Optional[float] = Field(alias="rating", default=None)
    title: str
    description: Optional[str] = None
    genre: Optional[list[str]] = Field(alias="genres", default=None)
    director: Optional[str] = None
    actors_names: Optional[str] = None
    writers_names: Optional[list[str]] = None
    actors: Optional[list[PersonM]] = None
    writers: Optional[list[PersonM]] = None


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class Person(BaseModel):
    id: str
    full_name: str
