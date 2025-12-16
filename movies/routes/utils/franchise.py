from sqlalchemy.ext.asyncio import AsyncSession

from schemas import EntryLocaleResponse
from schemas.entry import EntryBriefResponse
from db import queries
from schemas.franchise import FranchiseResponse, FranchiseBriefResponse
from schemas.franchise_locale import FranchiseLocaleResponse


async def load_franchise_with_locales(
        db: AsyncSession,
        db_franchise
) -> FranchiseBriefResponse:
    franchise_schema = FranchiseBriefResponse.model_validate(db_franchise)

    locales = await queries.get_franchise_locales_by_franchise(db, db_franchise.id)
    franchise_schema.locales = [
        FranchiseLocaleResponse.model_validate(loc) for loc in locales
    ]

    return franchise_schema


async def load_franchise_full(db: AsyncSession, franchise_id: int) -> FranchiseResponse | None:
    db_franchise = await queries.get_franchise(db, franchise_id)
    if not db_franchise:
        return None

    franchise_schema = FranchiseResponse(
        id=db_franchise.id,
        created_at=db_franchise.created_at,
        updated_at=db_franchise.updated_at,
        locales=[],
        entries=[]
    )

    franchise_schema.locales = [
        FranchiseLocaleResponse.model_validate(loc)
        for loc in db_franchise.locales
    ]

    db_entries = await queries.get_entries_by_franchise(db, franchise_id)
    for db_entry in db_entries:
        entry_brief = EntryBriefResponse(
            id=db_entry.id,
            franchise_id=db_entry.franchise_id,
            type=db_entry.type,
            status=db_entry.status,
            rating_mpaa=db_entry.rating_mpaa,
            age_rating=db_entry.age_rating,
            entry_number=db_entry.entry_number,
            duration=db_entry.duration,
            premiere_world=db_entry.premiere_world,
            premiere_digital=db_entry.premiere_digital,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at,
            locales=[
                EntryLocaleResponse.model_validate(loc)
                for loc in db_entry.locales
            ]
        )
        franchise_schema.entries.append(entry_brief)

    return franchise_schema
