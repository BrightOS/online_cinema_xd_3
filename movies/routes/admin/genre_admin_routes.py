from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.genre import GenreResponse, GenreCreateRequest, GenreUpdateRequest

router = APIRouter(prefix="/admin/genres", tags=["Genres (Admin)"])


async def _check_genre_name_exists(
    db: AsyncSession,
    name: str,
    exclude_id: int = None
) -> None:
    all_genres = await queries.get_genres(db)
    for g in all_genres:
        if exclude_id and g.id == exclude_id:
            continue
        if g.name.lower() == name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Genre with name '{name}' already exists."
            )


@router.post(
    "/",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new genre"
)
async def create_genre(
    genre_data: GenreCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    await _check_genre_name_exists(db, genre_data.name)

    db_genre = await queries.create_genre(db, genre_data)
    return db_genre


@router.put(
    "/{genre_id}/",
    response_model=GenreResponse,
    summary="Update a genre"
)
async def update_genre(
    genre_id: int,
    genre_update: GenreUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_genre = await queries.get_genre(db, genre_id)
    if not db_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    if genre_update.name and genre_update.name.lower() != db_genre.name.lower():
        await _check_genre_name_exists(db, genre_update.name, exclude_id=genre_id)

    updated_genre = await queries.update_genre(db, genre_id, genre_update)
    return updated_genre


@router.delete(
    "/{genre_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a genre"
)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_genre(db, genre_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return
