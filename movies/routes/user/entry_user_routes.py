from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.entry import EntryResponse
from routes.utils.entry import load_entry_details

router = APIRouter(prefix="/entries", tags=["User"])


@router.get(
    "/",
    response_model=List[EntryResponse],
    summary="Get all entries (movies/seasons)"
)
async def get_entries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    db_entries = await queries.get_entries(db, skip=skip, limit=limit)

    entries_response = []
    for db_entry in db_entries:
        entry_detail = await load_entry_details(db, db_entry.id)
        if entry_detail:
            entries_response.append(entry_detail)

    return entries_response


@router.get(
    "/{entry_id}/",
    response_model=EntryResponse,
    summary="Get a specific entry by ID",
    responses={404: {"description": "Entry not found"}}
)
async def get_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_session)
):
    entry = await load_entry_details(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    return entry
