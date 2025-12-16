from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import Franchise
from schemas import FranchiseCreateRequest


async def get_franchise(session: AsyncSession, franchise_id: int) -> Optional[Franchise]:
    result = await session.execute(
        select(Franchise)
        .options(selectinload(Franchise.locales))
        .where(Franchise.id == franchise_id)
    )
    return result.scalar_one_or_none()


async def get_franchises(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Franchise]:
    result = await session.execute(
        select(Franchise)
        .options(selectinload(Franchise.locales))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_franchise(session: AsyncSession, franchise: FranchiseCreateRequest) -> Franchise:
    db_franchise = Franchise(**franchise.model_dump())
    session.add(db_franchise)
    await session.commit()
    await session.refresh(db_franchise, attribute_names=['locales'])
    return db_franchise


async def delete_franchise(session: AsyncSession, franchise_id: int) -> bool:
    db_franchise = await get_franchise(session, franchise_id)
    if db_franchise:
        await session.delete(db_franchise)
        await session.commit()
        return True
    return False
