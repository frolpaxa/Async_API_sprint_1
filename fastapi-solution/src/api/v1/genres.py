from typing import Annotated

from fastapi import APIRouter, Depends, Query
from models.models import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


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
