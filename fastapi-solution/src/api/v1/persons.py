from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import Person
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
    full_name: str | None = Query(default=None),
    page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    page_count: Annotated[int, Query(description="Pagination page size", ge=1)] = 100,
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:

    person = await person_service.get_list(
        full_name,
        page_number,
        page_count,
    )

    return person
