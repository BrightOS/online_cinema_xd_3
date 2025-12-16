from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import EntryLocale
from schemas import EntryLocaleCreateRequest, EntryLocaleUpdateRequest


async def get_entry_locale(session: AsyncSession, entry_locale_id: int) -> Optional[EntryLocale]:
    result = await session.execute(
        select(EntryLocale)
        .options(selectinload(EntryLocale.entry))
        .where(EntryLocale.id == entry_locale_id)
    )
    return result.scalar_one_or_none()


async def get_entry_locales(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[EntryLocale]:
    result = await session.execute(
        select(EntryLocale)
        .options(selectinload(EntryLocale.entry))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_entry_locales_by_entry(session: AsyncSession, entry_id: int) -> List[EntryLocale]:
    result = await session.execute(
        select(EntryLocale)
        .where(EntryLocale.entry_id == entry_id)
    )
    return list(result.scalars().all())


async def create_entry_locale(session: AsyncSession, entry_locale: EntryLocaleCreateRequest, entry_id: int) -> EntryLocale:
    db_entry_locale = EntryLocale(**entry_locale.model_dump(), entry_id=entry_id)
    session.add(db_entry_locale)
    await session.commit()
    await session.refresh(db_entry_locale)
    return db_entry_locale


async def update_entry_locale(session: AsyncSession, entry_locale_id: int, entry_locale: EntryLocaleUpdateRequest) -> Optional[EntryLocale]:
    db_entry_locale = await get_entry_locale(session, entry_locale_id)
    if db_entry_locale:
        for key, value in entry_locale.model_dump(exclude_unset=True).items():
            setattr(db_entry_locale, key, value)
        await session.commit()
        await session.refresh(db_entry_locale)
        return db_entry_locale
    return None


async def delete_entry_locale(session: AsyncSession, entry_locale_id: int) -> bool:
    db_entry_locale = await get_entry_locale(session, entry_locale_id)
    if db_entry_locale:
        await session.delete(db_entry_locale)
        await session.commit()
        return True
    return False
