from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.episode import EpisodeResponse, EpisodeCreateRequest, EpisodeUpdateRequest
from schemas.episode_locale import EpisodeLocaleResponse
from routes.utils.episode import load_episode_with_locales

router = APIRouter(prefix="/admin/episodes", tags=["Episodes (Admin)"])


async def _validate_entry_exists(db: AsyncSession, entry_id: int) -> None:
    db_entry = await queries.get_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with ID {entry_id} not found"
        )


@router.post(
    "/",
    response_model=EpisodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new episode"
)
async def create_episode(
    episode_data: EpisodeCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    await _validate_entry_exists(db, episode_data.entry_id)
    db_episode = await queries.create_episode(db, episode_data)
    locales = await queries.get_episode_locales_by_episode(db, db_episode.id)
    response = EpisodeResponse.model_validate(db_episode)
    response.locales = [EpisodeLocaleResponse.model_validate(loc) for loc in locales]

    return response


@router.put(
    "/{episode_id}/",
    response_model=EpisodeResponse,
    summary="Update an episode"
)
async def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_episode = await queries.update_episode(db, episode_id, episode_update)
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )

    return await load_episode_with_locales(db, episode_id)


@router.delete(
    "/{episode_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an episode and all its associated locales"
)
async def delete_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_episode(db, episode_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return
