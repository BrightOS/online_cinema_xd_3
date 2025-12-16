from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.entry_locale import EntryLocaleResponse, EntryLocaleCreateRequest, EntryLocaleUpdateRequest

router = APIRouter(prefix="/admin/entries", tags=["Entry Locales (Admin)"])


@router.post(
    "/{entry_id}/locales/",
    response_model=EntryLocaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new locale for an entry"
)
async def create_entry_locale(
    entry_id: int,
    locale: EntryLocaleCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_entry = await queries.get_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    existing_locales = await queries.get_entry_locales_by_entry(db, entry_id)
    for loc in existing_locales:
        if loc.language == locale.language:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Locale for language '{locale.language}' already exists for this entry"
            )

    db_locale = await queries.create_entry_locale(db, locale, entry_id)
    return db_locale


@router.put(
    "/locales/{locale_id}/",
    response_model=EntryLocaleResponse,
    summary="Update a specific entry locale"
)
async def update_entry_locale(
    locale_id: int,
    locale_update: EntryLocaleUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_locale = await queries.get_entry_locale(db, locale_id)
    if not db_locale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry locale not found"
        )

    if locale_update.language and locale_update.language != db_locale.language:
        existing_locales = await queries.get_entry_locales_by_entry(db, db_locale.entry_id)
        for loc in existing_locales:
            if loc.id != locale_id and loc.language == locale_update.language:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another locale with language '{locale_update.language}' already exists for this entry"
                )

    updated_locale = await queries.update_entry_locale(db, locale_id, locale_update)
    return updated_locale


@router.delete(
    "/locales/{locale_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific entry locale"
)
async def delete_entry_locale(
    locale_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_entry_locale(db, locale_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry locale not found"
        )
    return
