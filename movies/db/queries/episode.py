from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import Episode
from schemas import EpisodeCreateRequest, EpisodeUpdateRequest


async def get_episode(session: AsyncSession, episode_id: int) -> Optional[Episode]:
    result = await session.execute(
        select(Episode)
        .options(
            selectinload(Episode.locales),
            selectinload(Episode.entry)
        )
        .where(Episode.id == episode_id)
    )
    return result.scalar_one_or_none()


async def get_episodes(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Episode]:
    result = await session.execute(
        select(Episode)
        .options(
            selectinload(Episode.locales),
            selectinload(Episode.entry)
        )
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_episodes_by_entry(session: AsyncSession, entry_id: int) -> List[Episode]:
    """Получить все episodes для конкретного entry с eager loading локалей"""
    result = await session.execute(
        select(Episode)
        .options(selectinload(Episode.locales))
        .where(Episode.entry_id == entry_id)
        .order_by(Episode.episode_number)
    )
    return list(result.scalars().all())


async def create_episode(session: AsyncSession, episode: EpisodeCreateRequest) -> Episode:
    db_episode = Episode(**episode.model_dump())
    session.add(db_episode)
    await session.commit()
    await session.refresh(db_episode, attribute_names=['locales'])
    return db_episode


async def update_episode(session: AsyncSession, episode_id: int, episode: EpisodeUpdateRequest) -> Optional[Episode]:
    db_episode = await get_episode(session, episode_id)
    if db_episode:
        for key, value in episode.model_dump(exclude_unset=True).items():
            setattr(db_episode, key, value)
        await session.commit()
        await session.refresh(db_episode, attribute_names=['locales'])
        return db_episode
    return None


async def delete_episode(session: AsyncSession, episode_id: int) -> bool:
    db_episode = await get_episode(session, episode_id)
    if db_episode:
        await session.delete(db_episode)
        await session.commit()
        return True
    return False
