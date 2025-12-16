from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from db import queries
from schemas.episode_locale import EpisodeLocaleResponse, EpisodeLocaleCreateRequest, EpisodeLocaleUpdateRequest

router = APIRouter(prefix="/admin/episodes", tags=["Episode Locales (Admin)"])


@router.post(
    "/{episode_id}/locales/",
    response_model=EpisodeLocaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new locale for an episode"
)
async def create_episode_locale(
    episode_id: int,
    locale: EpisodeLocaleCreateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_episode = await queries.get_episode(db, episode_id)
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )

    existing_locales = await queries.get_episode_locales_by_episode(db, episode_id)
    for loc in existing_locales:
        if loc.language == locale.language:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Locale for language '{locale.language}' already exists for this episode"
            )

    db_locale = await queries.create_episode_locale(db, locale, episode_id)
    return db_locale


@router.put(
    "/locales/{locale_id}/",
    response_model=EpisodeLocaleResponse,
    summary="Update a specific episode locale"
)
async def update_episode_locale(
    locale_id: int,
    locale_update: EpisodeLocaleUpdateRequest,
    db: AsyncSession = Depends(get_session)
):
    db_locale = await queries.get_episode_locale(db, locale_id)
    if not db_locale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode locale not found"
        )

    if locale_update.language and locale_update.language != db_locale.language:
        existing_locales = await queries.get_episode_locales_by_episode(db, db_locale.episode_id)
        for loc in existing_locales:
            if loc.id != locale_id and loc.language == locale_update.language:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Another locale with language '{locale_update.language}' already exists for this episode"
                )

    updated_locale = await queries.update_episode_locale(db, locale_id, locale_update)
    return updated_locale


@router.delete(
    "/locales/{locale_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific episode locale"
)
async def delete_episode_locale(
    locale_id: int,
    db: AsyncSession = Depends(get_session)
):
    success = await queries.delete_episode_locale(db, locale_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode locale not found"
        )
    return
