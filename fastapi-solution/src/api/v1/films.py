from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import FilmShort, Film, GenreType, MultiParams, Sort
from services.film import FilmService, get_film_service

from models.models import QueryParams

router = APIRouter()


@router.get(
    "/search",
    response_model=list[Film],
    summary="Поиск фильмов",
)
async def film_search(
    query: Annotated[str, Query(..., description="Query params")],
    page: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    size: Annotated[int, Query(description="Pagination page size", ge=1)] = 100,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    film = await film_service.search_films(
        QueryParams(**{"query": query, "page": page, "size": size})
    )

    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="movie not found")

    return film


@router.get(
    "/",
    response_model=list[Film],
    summary="Список фильмов",
    description="Список фильмов с возможностью фильтрации и сортировки",
)
async def film_list(
    multi_params: MultiParams = Depends(),
    title: str | None = Query(default=None),
    imdb_rating: Sort | None = None,
    genre: list[GenreType] = Query(default=None),
    director: str = Query(default=None),
    page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    page_count: Annotated[int, Query(description="Pagination page size", ge=1)] = 100,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:

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
