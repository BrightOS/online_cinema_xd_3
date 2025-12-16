from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import FranchiseLocale
from schemas import FranchiseLocaleCreateRequest, FranchiseLocaleUpdateRequest


async def get_franchise_locale(session: AsyncSession, franchise_locale_id: int) -> Optional[FranchiseLocale]:
    result = await session.execute(
        select(FranchiseLocale)
        .options(selectinload(FranchiseLocale.franchise))
        .where(FranchiseLocale.id == franchise_locale_id)
    )
    return result.scalar_one_or_none()


async def get_franchise_locales(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[FranchiseLocale]:
    result = await session.execute(
        select(FranchiseLocale)
        .options(selectinload(FranchiseLocale.franchise))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_franchise_locales_by_franchise(session: AsyncSession, franchise_id: int) -> List[FranchiseLocale]:
    result = await session.execute(
        select(FranchiseLocale)
        .where(FranchiseLocale.franchise_id == franchise_id)
    )
    return list(result.scalars().all())


async def create_franchise_locale(session: AsyncSession, franchise_locale: FranchiseLocaleCreateRequest, franchise_id: int) -> FranchiseLocale:
    db_franchise_locale = FranchiseLocale(**franchise_locale.model_dump(), franchise_id=franchise_id)
    session.add(db_franchise_locale)
    await session.commit()
    await session.refresh(db_franchise_locale)
    return db_franchise_locale


async def update_franchise_locale(session: AsyncSession, franchise_locale_id: int, franchise_locale: FranchiseLocaleUpdateRequest) -> Optional[FranchiseLocale]:
    db_franchise_locale = await get_franchise_locale(session, franchise_locale_id)
    if db_franchise_locale:
        for key, value in franchise_locale.model_dump(exclude_unset=True).items():
            setattr(db_franchise_locale, key, value)
        await session.commit()
        await session.refresh(db_franchise_locale)
        return db_franchise_locale
    return None


async def delete_franchise_locale(session: AsyncSession, franchise_locale_id: int) -> bool:
    db_franchise_locale = await get_franchise_locale(session, franchise_locale_id)
    if db_franchise_locale:
        await session.delete(db_franchise_locale)
        await session.commit()
        return True
    return False
