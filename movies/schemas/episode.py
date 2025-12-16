from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional
from .mixins import ExampleMixin
from .episode_locale import EpisodeLocaleResponse


class EpisodeBase(BaseModel):
    episode_number: Optional[int] = Field(None, example=1, description="Номер эпизода")
    duration: Optional[int] = Field(None, example=45, description="Длительность в минутах")
    premiere_world: Optional[date] = Field(None, example="2023-01-15")
    premiere_digital: Optional[date] = Field(None, example="2023-02-01")


class EpisodeCreateRequest(EpisodeBase, ExampleMixin):
    entry_id: int = Field(..., example=1, description="ID сезона")


class EpisodeUpdateRequest(EpisodeBase, ExampleMixin):
    pass


class EpisodeResponse(EpisodeBase):
    id: int = Field(..., example=1)
    entry_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-15T10:30:00")
    locales: List[EpisodeLocaleResponse] = []

    class Config:
        from_attributes = True
