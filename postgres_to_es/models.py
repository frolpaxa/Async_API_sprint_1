from pydantic import BaseModel, Field

ROLES = {
    "actors": "actor",
    "actors_names": "actor",
    "director": "director",
    "writers": "writer",
    "writers_names": "writer",
}


class PersonShort(BaseModel):
    id: str = Field(alias="person_id", default=None)
    name: str = Field(alias="person_name", default=None)


class Movie(BaseModel):
    id: str
    imdb_rating: float | None = Field(alias="rating", default=None)
    title: str
    description: str | None = None
    genre: list[str] | None = Field(alias="genres", default=None)
    director: str | None = None
    actors_names: str | None = None
    writers_names: list[str] | None = None
    actors: list[PersonShort] | None = None
    writers: list[PersonShort] | None = None


class Genre(BaseModel):
    id: str
    name: str
    description: str | None = None


class FilmPerson(BaseModel):
    id: str
    roles: list[str]


class Person(BaseModel):
    id: str
    full_name: str
    films: list[FilmPerson] | None
