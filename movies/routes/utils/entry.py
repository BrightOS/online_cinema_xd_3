from sqlalchemy.ext.asyncio import AsyncSession

from schemas import EpisodeLocaleResponse, EpisodeResponse
from db import queries
from schemas.entry import EntryResponse
from schemas.entry_locale import EntryLocaleResponse
from schemas.entry_staff import EntryStaffResponse
from schemas.genre import GenreResponse


async def load_entry_details(db: AsyncSession, entry_id: int) -> EntryResponse | None:
    db_entry = await queries.get_entry(db, entry_id)
    if not db_entry:
        return None

    entry_schema = EntryResponse.model_validate(db_entry)

    locales = await queries.get_entry_locales_by_entry(db, entry_id)
    entry_schema.locales = [EntryLocaleResponse.model_validate(loc) for loc in locales]

    genres = await queries.get_entry_genres(db, entry_id)
    entry_schema.genres = [GenreResponse.model_validate(g) for g in genres]

    staff_with_persons = await queries.get_entry_staff(db, entry_id)
    entry_schema.staff = []
    for es, person in staff_with_persons:
        staff_member_schema = EntryStaffResponse(
            entry_id=es.entry_id,
            person_id=es.person_id,
            role=es.role,
            character_name=es.character_name,
        )
        entry_schema.staff.append(staff_member_schema)

    db_episodes = await queries.get_episodes_by_entry(db, entry_id)
    entry_schema.episodes = []
    for db_episode in db_episodes:
        episode_brief = EpisodeResponse(
            id=db_episode.id,
            entry_id=db_episode.entry_id,
            episode_number=db_episode.episode_number,
            duration=db_episode.duration,
            premiere_world=db_episode.premiere_world,
            premiere_digital=db_episode.premiere_digital,
            created_at=db_episode.created_at,
            locales=[
                EpisodeLocaleResponse.model_validate(loc)
                for loc in db_episode.locales
            ]
        )
        entry_schema.episodes.append(episode_brief)

    return entry_schema
