from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import EpisodeLocale
from schemas import EpisodeLocaleCreateRequest, EpisodeLocaleUpdateRequest


async def get_episode_locale(session: AsyncSession, episode_locale_id: int) -> Optional[EpisodeLocale]:
    result = await session.execute(
        select(EpisodeLocale)
        .options(selectinload(EpisodeLocale.episode))
        .where(EpisodeLocale.id == episode_locale_id)
    )
    return result.scalar_one_or_none()


async def get_episode_locales(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[EpisodeLocale]:
    result = await session.execute(
        select(EpisodeLocale)
        .options(selectinload(EpisodeLocale.episode))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_episode_locales_by_episode(session: AsyncSession, episode_id: int) -> List[EpisodeLocale]:
    result = await session.execute(
        select(EpisodeLocale)
        .where(EpisodeLocale.episode_id == episode_id)
    )
    return list(result.scalars().all())


async def create_episode_locale(session: AsyncSession, episode_locale: EpisodeLocaleCreateRequest, episode_id: int) -> EpisodeLocale:
    db_episode_locale = EpisodeLocale(**episode_locale.model_dump(), episode_id=episode_id)
    session.add(db_episode_locale)
    await session.commit()
    await session.refresh(db_episode_locale)
    return db_episode_locale


async def update_episode_locale(session: AsyncSession, episode_locale_id: int, episode_locale: EpisodeLocaleUpdateRequest) -> Optional[EpisodeLocale]:
    db_episode_locale = await get_episode_locale(session, episode_locale_id)
    if db_episode_locale:
        for key, value in episode_locale.model_dump(exclude_unset=True).items():
            setattr(db_episode_locale, key, value)
        await session.commit()
        await session.refresh(db_episode_locale)
        return db_episode_locale
    return None


async def delete_episode_locale(session: AsyncSession, episode_locale_id: int) -> bool:
    db_episode_locale = await get_episode_locale(session, episode_locale_id)
    if db_episode_locale:
        await session.delete(db_episode_locale)
        await session.commit()
        return True
    return False
