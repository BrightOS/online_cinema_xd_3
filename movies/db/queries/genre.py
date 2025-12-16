from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import Genre
from schemas import GenreCreateRequest, GenreUpdateRequest


async def get_genre(session: AsyncSession, genre_id: int) -> Optional[Genre]:
    result = await session.execute(
        select(Genre)
        .options(selectinload(Genre.entries))
        .where(Genre.id == genre_id)
    )
    return result.scalar_one_or_none()


async def get_genres(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Genre]:
    result = await session.execute(
        select(Genre)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_genre(session: AsyncSession, genre: GenreCreateRequest) -> Genre:
    db_genre = Genre(**genre.model_dump())
    session.add(db_genre)
    await session.commit()
    await session.refresh(db_genre)
    return db_genre


async def update_genre(session: AsyncSession, genre_id: int, genre: GenreUpdateRequest) -> Optional[Genre]:
    db_genre = await get_genre(session, genre_id)
    if db_genre:
        for key, value in genre.model_dump(exclude_unset=True).items():
            setattr(db_genre, key, value)
        await session.commit()
        await session.refresh(db_genre)
        return db_genre
    return None


async def delete_genre(session: AsyncSession, genre_id: int) -> bool:
    db_genre = await get_genre(session, genre_id)
    if db_genre:
        await session.delete(db_genre)
        await session.commit()
        return True
    return False
