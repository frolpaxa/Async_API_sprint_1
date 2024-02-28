from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import Person, GenreType, MultiParams, Sort
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return Person(id=person.id, full_name=person.full_name)


@router.get(
    "/",
    response_model=list[Person],
    summary="Список персон",
    description="Список персон с возможностью фильтрации и сортировки",
)
async def person_list(
    full_name: Optional[str] = Query(default=None),
    page_number: int = Query(default=1),
    page_count: int = Query(default=100),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:

    person = await person_service.get_list(
        full_name,
        page_number,
        page_count,
    )

    return person
