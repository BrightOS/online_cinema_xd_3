from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.franchise_locale import FranchiseLocaleResponse, FranchiseLocaleCreateRequest, FranchiseLocaleUpdateRequest

router = APIRouter(prefix="/admin/franchises", tags=["Franchise Locales (Admin)"])


@router.post(
    "/{franchise_id}/locales/",
    response_model=FranchiseLocaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new locale for a franchise"
)
async def create_franchise_locale(
        franchise_id: int,
        locale: FranchiseLocaleCreateRequest,
        db: AsyncSession = Depends(get_session)
):
    db_franchise = await queries.get_franchise(db, franchise_id)
    if not db_franchise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise not found"
        )

    existing_locales = await queries.get_franchise_locales_by_franchise(db, franchise_id)
    for loc in existing_locales:
        if loc.language == locale.language:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Locale for language '{locale.language}' already exists for this franchise"
            )

    db_locale = await queries.create_franchise_locale(db, locale, franchise_id)
    return db_locale


@router.put(
    "/locales/{locale_id}/",
    response_model=FranchiseLocaleResponse,
    summary="Update a specific franchise locale"
)
async def update_franchise_locale(
        locale_id: int,
        locale_update: FranchiseLocaleUpdateRequest,
        db: AsyncSession = Depends(get_session)
):
    db_locale = await queries.get_franchise_locale(db, locale_id)
    if not db_locale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise locale not found"
        )

    if locale_update.language and locale_update.language != db_locale.language:
        existing_locales = await queries.get_franchise_locales_by_franchise(db, db_locale.franchise_id)
        for loc in existing_locales:
            if loc.id != locale_id and loc.language == locale_update.language:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another locale with language '{locale_update.language}' already exists for this franchise"
                )

    updated_locale = await queries.update_franchise_locale(db, locale_id, locale_update)
    return updated_locale


@router.delete(
    "/locales/{locale_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific franchise locale"
)
async def delete_franchise_locale(
        locale_id: int,
        db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_franchise_locale(db, locale_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise locale not found"
        )
    return
