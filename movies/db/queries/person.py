from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.models import Person
from schemas import PersonCreateRequest, PersonUpdateRequest


async def get_person(session: AsyncSession, person_id: int) -> Optional[Person]:
    result = await session.execute(
        select(Person)
        .options(selectinload(Person.staff_entries))
        .where(Person.id == person_id)
    )
    return result.scalar_one_or_none()


async def get_persons(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Person]:
    result = await session.execute(
        select(Person)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_person(session: AsyncSession, person: PersonCreateRequest) -> Person:
    db_person = Person(**person.model_dump())
    session.add(db_person)
    await session.commit()
    await session.refresh(db_person)
    return db_person


async def update_person(session: AsyncSession, person_id: int, person: PersonUpdateRequest) -> Optional[Person]:
    db_person = await get_person(session, person_id)
    if db_person:
        for key, value in person.model_dump(exclude_unset=True).items():
            setattr(db_person, key, value)
        await session.commit()
        await session.refresh(db_person)
        return db_person
    return None


async def delete_person(session: AsyncSession, person_id: int) -> bool:
    db_person = await get_person(session, person_id)
    if db_person:
        await session.delete(db_person)
        await session.commit()
        return True
    return False
