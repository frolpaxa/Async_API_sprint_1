from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Film as FilmItem
from models.film import GenreType, MultiParams, Sort
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(id=film.id, title=film.title)


@router.get(
    "/",
    response_model=list[FilmItem],
    summary="Список фильмов",
    description="Список фильмов с возможностью фильтрации и сортировки",
)
async def film_list(
    multi_params: MultiParams = Depends(),
    title: Optional[str] = Query(default=None),
    imdb_rating: Optional[Sort] = None,
    genre: list[GenreType] = Query(default=None),
    director: str = Query(default=None),
    page_number: int = Query(default=1),
    page_count: int = Query(default=100),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmItem]:

    films = await film_service.get_list(
        title,
        imdb_rating,
        genre,
        director,
        multi_params,
        page_number,
        page_count,
    )

    return films
