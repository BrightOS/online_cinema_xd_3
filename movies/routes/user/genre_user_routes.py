from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.genre import GenreResponse

from metrics import GENRE_VIEW_TOTAL

router = APIRouter(prefix="/genres", tags=["User"])


@router.get(
    "/",
    response_model=List[GenreResponse],
    summary="Get all genres"
)
async def get_genres(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    genres = await queries.get_genres(db, skip=skip, limit=limit)
    return genres


@router.get(
    "/{genre_id}/",
    response_model=GenreResponse,
    summary="Get a specific genre by ID"
)
async def get_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_session)
):
    GENRE_VIEW_TOTAL.labels(genre_id=str(genre_id)).inc()
    db_genre = await queries.get_genre(db, genre_id)
    if not db_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return db_genre
