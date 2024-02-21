from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

import orjson

# Используем pydantic для упрощения работы
# при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes,
    # а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class UuidMixin(BaseModel):
    id: UUID


class DateMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Config(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(UuidMixin, DateMixin, Config):
    full_name: str


class Genre(UuidMixin, DateMixin, Config):
    name: str
    description: Optional[str] = None


class Film(UuidMixin, DateMixin, Config):
    title: str
    description: Optional[str] = None
    creation_date: Optional[date] = None
    rating: Optional[float] = None
    type: str
    # связанные параметры
    genre: Optional[list[str]] = None
    director: Optional[str] = None
    actors: Optional[list[Person]] = None
    writers: Optional[list[Person]] = None
