from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.episode import EpisodeResponse
from schemas.episode_locale import EpisodeLocaleResponse
from routes.utils.episode import load_episode_with_locales

from metrics import EPISODE_VIEW_TOTAL

router = APIRouter(prefix="/episodes", tags=["User"])


@router.get(
    "/",
    response_model=List[EpisodeResponse],
    summary="Get all episodes"
)
async def get_episodes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    db_episodes = await queries.get_episodes(db, skip=skip, limit=limit)

    episodes_response = []
    for db_episode in db_episodes:
        episode_schema = EpisodeResponse.model_validate(db_episode)
        locales = await queries.get_episode_locales_by_episode(db, db_episode.id)
        episode_schema.locales = [EpisodeLocaleResponse.model_validate(loc) for loc in locales]
        episodes_response.append(episode_schema)

    return episodes_response


@router.get(
    "/{episode_id}/",
    response_model=EpisodeResponse,
    summary="Get a specific episode by ID"
)
async def get_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_session)
):
    EPISODE_VIEW_TOTAL.labels(episode_id=str(episode_id)).inc()
    episode = await load_episode_with_locales(db, episode_id)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return episode
