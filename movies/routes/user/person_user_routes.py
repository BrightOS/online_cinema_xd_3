from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.person import PersonResponse

from metrics import PERSON_VIEW_TOTAL

router = APIRouter(prefix="/persons", tags=["User"])


@router.get(
    "/",
    response_model=List[PersonResponse],
    summary="Get all persons"
)
async def get_persons(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    persons = await queries.get_persons(db, skip=skip, limit=limit)
    return persons


@router.get(
    "/{person_id}/",
    response_model=PersonResponse,
    summary="Get a specific person by ID"
)
async def get_person(
    person_id: int,
    db: AsyncSession = Depends(get_session)
):
    PERSON_VIEW_TOTAL.labels(person_id=str(person_id)).inc()
    db_person = await queries.get_person(db, person_id)
    if not db_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return db_person
