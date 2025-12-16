from sqlalchemy.ext.asyncio import AsyncSession

from db import queries
from schemas.episode import EpisodeResponse
from schemas.episode_locale import EpisodeLocaleResponse


async def load_episode_with_locales(db: AsyncSession, episode_id: int) -> EpisodeResponse | None:
    db_episode = await queries.get_episode(db, episode_id)
    if not db_episode:
        return None

    episode_schema = EpisodeResponse.model_validate(db_episode)
    locales = await queries.get_episode_locales_by_episode(db, episode_id)
    episode_schema.locales = [EpisodeLocaleResponse.model_validate(loc) for loc in locales]

    return episode_schema
