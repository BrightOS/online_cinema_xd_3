from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.person import PersonResponse, PersonCreateRequest, PersonUpdateRequest

router = APIRouter(prefix="/admin/persons", tags=["Persons (Admin)"])


async def _check_person_name_exists(
    db: AsyncSession,
    name: str,
    exclude_id: int = None
) -> None:
    all_persons = await queries.get_persons(db)
    for p in all_persons:
        if exclude_id and p.id == exclude_id:
            continue
        if p.name.lower() == name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Person with name '{name}' already exists."
            )


@router.post(
    "/",
    response_model=PersonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new person"
)
async def create_person(
    person_data: PersonCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    await _check_person_name_exists(db, person_data.name)

    db_person = await queries.create_person(db, person_data)
    return db_person


@router.put(
    "/{person_id}/",
    response_model=PersonResponse,
    summary="Update a person"
)
async def update_person(
    person_id: int,
    person_update: PersonUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_person = await queries.get_person(db, person_id)
    if not db_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )

    if person_update.name and person_update.name.lower() != db_person.name.lower():
        await _check_person_name_exists(db, person_update.name, exclude_id=person_id)

    updated_person = await queries.update_person(db, person_id, person_update)
    return updated_person


@router.delete(
    "/{person_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a person and all associated staff entries"
)
async def delete_person(
    person_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_person(db, person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return
