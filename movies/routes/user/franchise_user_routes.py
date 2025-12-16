from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.franchise import FranchiseResponse, FranchiseBriefResponse
from routes.utils.franchise import load_franchise_with_locales, load_franchise_full

router = APIRouter(prefix="/franchises", tags=["User"])


@router.get(
    "/",
    response_model=List[FranchiseBriefResponse],
    summary="Get all franchises"
)
async def get_franchises(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    db_franchises = await queries.get_franchises(db, skip=skip, limit=limit)

    franchises_with_locales = []
    for db_franchise in db_franchises:
        franchise_schema = await load_franchise_with_locales(db, db_franchise)
        franchises_with_locales.append(franchise_schema)

    return franchises_with_locales


@router.get(
    "/{franchise_id}/",
    response_model=FranchiseResponse,
    summary="Get a specific franchise by ID"
)
async def get_franchise(
    franchise_id: int,
    db: AsyncSession = Depends(get_session)
):
    franchise = await load_franchise_full(db, franchise_id)
    if not franchise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise not found"
        )
    return franchise
