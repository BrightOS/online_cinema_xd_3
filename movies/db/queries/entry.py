from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import Entry, Episode
from schemas import EntryCreateRequest, EntryUpdateRequest


async def get_entry(session: AsyncSession, entry_id: int) -> Optional[Entry]:
    result = await session.execute(
        select(Entry)
        .options(
            selectinload(Entry.locales),
            selectinload(Entry.episodes).selectinload(Episode.locales),
            selectinload(Entry.genres),
            selectinload(Entry.staff)
        )
        .where(Entry.id == entry_id)
    )
    return result.scalar_one_or_none()


async def get_entries(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Entry]:
    result = await session.execute(
        select(Entry)
        .options(
            selectinload(Entry.locales),
            selectinload(Entry.episodes).selectinload(Episode.locales),
            selectinload(Entry.genres),
            selectinload(Entry.staff)
        )
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_entries_by_franchise(session: AsyncSession, franchise_id: int) -> List[Entry]:
    """Получить все entries для конкретной франшизы с eager loading локалей"""
    result = await session.execute(
        select(Entry)
        .options(selectinload(Entry.locales))
        .where(Entry.franchise_id == franchise_id)
        .order_by(Entry.entry_number)
    )
    return list(result.scalars().all())


async def create_entry(session: AsyncSession, entry: EntryCreateRequest) -> Entry:
    db_entry = Entry(**entry.model_dump(exclude={'genres', 'staff'}))
    session.add(db_entry)
    await session.commit()
    await session.refresh(db_entry)
    return db_entry


async def update_entry(session: AsyncSession, entry_id: int, entry: EntryUpdateRequest) -> Optional[Entry]:
    db_entry = await get_entry(session, entry_id)
    if db_entry:
        for key, value in entry.model_dump(exclude_unset=True).items():
            setattr(db_entry, key, value)
        await session.commit()
        await session.refresh(db_entry)
        return db_entry
    return None


async def delete_entry(session: AsyncSession, entry_id: int) -> bool:
    db_entry = await get_entry(session, entry_id)
    if db_entry:
        await session.delete(db_entry)
        await session.commit()
        return True
    return False
