from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from db.models import EntryGenre, EntryStaff, Genre, Person


async def get_entry_genres(session: AsyncSession, entry_id: int) -> List[Genre]:
    result = await session.execute(
        select(EntryGenre).where(EntryGenre.entry_id == entry_id)
    )
    entry_genres = result.scalars().all()
    genre_ids = [eg.genre_id for eg in entry_genres]

    if not genre_ids:
        return []

    result = await session.execute(
        select(Genre).where(Genre.id.in_(genre_ids))
    )
    return list(result.scalars().all())


async def get_entry_staff(session: AsyncSession, entry_id: int) -> List[tuple]:
    result = await session.execute(
        select(EntryStaff).where(EntryStaff.entry_id == entry_id)
    )
    entry_staff_relations = result.scalars().all()
    person_ids = [es.person_id for es in entry_staff_relations]

    if not person_ids:
        return []

    result = await session.execute(
        select(Person).where(Person.id.in_(person_ids))
    )
    persons = result.scalars().all()
    person_map = {p.id: p for p in persons}

    staff_with_persons = []
    for es in entry_staff_relations:
        if es.person_id in person_map:
            staff_with_persons.append((es, person_map[es.person_id]))

    return staff_with_persons


async def add_entry_genres(
        session: AsyncSession,
        entry_id: int,
        genre_ids: List[int]
) -> None:
    for genre_id in genre_ids:
        entry_genre = EntryGenre(entry_id=entry_id, genre_id=genre_id)
        session.add(entry_genre)
    await session.commit()


async def replace_entry_genres(
        session: AsyncSession,
        entry_id: int,
        genre_ids: List[int]
) -> None:
    await session.execute(
        delete(EntryGenre).where(EntryGenre.entry_id == entry_id)
    )
    await session.commit()

    if genre_ids:
        await add_entry_genres(session, entry_id, genre_ids)


async def add_entry_staff(
        session: AsyncSession,
        entry_id: int,
        staff_data: List[dict]
) -> None:
    for staff_member in staff_data:
        entry_staff = EntryStaff(
            entry_id=entry_id,
            person_id=staff_member['person_id'],
            role=staff_member['role'],
            character_name=staff_member.get('character_name')
        )
        session.add(entry_staff)
    await session.commit()


async def replace_entry_staff(
        session: AsyncSession,
        entry_id: int,
        staff_data: List[dict]
) -> None:
    await session.execute(
        delete(EntryStaff).where(EntryStaff.entry_id == entry_id)
    )
    await session.commit()

    if staff_data:
        await add_entry_staff(session, entry_id, staff_data)


async def clear_entry_genres(session: AsyncSession, entry_id: int) -> None:
    await session.execute(
        delete(EntryGenre).where(EntryGenre.entry_id == entry_id)
    )
    await session.commit()


async def clear_entry_staff(session: AsyncSession, entry_id: int) -> None:
    await session.execute(
        delete(EntryStaff).where(EntryStaff.entry_id == entry_id)
    )
    await session.commit()
