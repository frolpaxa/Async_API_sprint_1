from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(id=genre.id, name=genre.name)


@router.get(
    "/",
    response_model=list[Genre],
    summary="Список жанров",
    description="Список жанров с возможностью фильтрации и сортировки",
)
async def genre_list(
    name: str | None = Query(default=None),
    page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    page_count: Annotated[int, Query(description="Pagination page size", ge=1)] = 100,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:

    genre = await genre_service.get_list(
        name,
        page_number,
        page_count,
    )

    return genre
