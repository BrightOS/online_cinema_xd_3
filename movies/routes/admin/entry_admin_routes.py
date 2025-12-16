from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.entry import EntryResponse, EntryCreateRequest, EntryUpdateRequest
from routes.utils.entry import load_entry_details

router = APIRouter(prefix="/admin/entries", tags=["Entries (Admin)"])


async def _validate_franchise_exists(db: AsyncSession, franchise_id: int) -> None:
    db_franchise = await queries.get_franchise(db, franchise_id)
    if not db_franchise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Franchise with ID {franchise_id} not found"
        )


async def _add_genres_to_entry(db: AsyncSession, entry_id: int, genre_ids: List[int]) -> None:
    if not genre_ids:
        return

    valid_genres = []
    for genre_id in genre_ids:
        db_genre = await queries.get_genre(db, genre_id)
        if not db_genre:
            print(f"Warning: Genre ID {genre_id} not found for entry {entry_id}. Skipping.")
            continue
        valid_genres.append(genre_id)

    if valid_genres:
        await queries.add_entry_genres(db, entry_id, valid_genres)


async def _add_staff_to_entry(db: AsyncSession, entry_id: int, staff_list: List) -> None:
    if not staff_list:
        return

    valid_staff = []
    for staff_member in staff_list:
        person_id = staff_member.person_id
        role = staff_member.role
        character_name = staff_member.character_name

        db_person = await queries.get_person(db, person_id)
        if not db_person:
            print(f"Warning: Person ID {person_id} not found for entry {entry_id}. Skipping.")
            continue

        valid_staff.append({
            'person_id': person_id,
            'role': role,
            'character_name': character_name
        })

    if valid_staff:
        await queries.add_entry_staff(db, entry_id, valid_staff)


@router.post(
    "/",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new entry (movie/season)"
)
async def create_entry(
    entry_data: EntryCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    await _validate_franchise_exists(db, entry_data.franchise_id)
    db_entry = await queries.create_entry(db, entry_data)
    await _add_genres_to_entry(db, db_entry.id, entry_data.genres)
    await _add_staff_to_entry(db, db_entry.id, entry_data.staff)
    return await load_entry_details(db, db_entry.id)


@router.put(
    "/{entry_id}/",
    response_model=EntryResponse,
    summary="Update an entry (movie/season)"
)
async def update_entry(
    entry_id: int,
    entry_update: EntryUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_entry = await queries.get_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    update_data = entry_update.model_dump(exclude={'genres', 'staff'}, exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(db_entry, key, value)
        db_entry.updated_at = datetime.now()
        await db.commit()
        await db.refresh(db_entry)

    if entry_update.genres is not None:
        valid_genres = []
        for genre_id in entry_update.genres:
            db_genre = await queries.get_genre(db, genre_id)
            if not db_genre:
                print(f"Warning: Genre ID {genre_id} not found for entry {entry_id}. Skipping.")
                continue
            valid_genres.append(genre_id)

        await queries.replace_entry_genres(db, entry_id, valid_genres)

    if entry_update.staff is not None:
        valid_staff = []
        for staff_member in entry_update.staff:
            db_person = await queries.get_person(db, staff_member.person_id)
            if not db_person:
                print(f"Warning: Person ID {staff_member.person_id} not found for entry {entry_id}. Skipping.")
                continue

            valid_staff.append({
                'person_id': staff_member.person_id,
                'role': staff_member.role,
                'character_name': staff_member.character_name
            })

        await queries.replace_entry_staff(db, entry_id, valid_staff)

    return await load_entry_details(db, entry_id)


@router.delete(
    "/{entry_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an entry and all its associated data"
)
async def delete_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_entry(db, entry_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    return
