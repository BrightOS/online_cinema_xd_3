from pydantic import BaseModel, Field
from typing import Optional
from .mixins import ExampleMixin


class EpisodeLocaleBase(BaseModel):
    language: str = Field(..., example="ru")
    title: str = Field(..., example="Пилот")
    description: Optional[str] = Field(None, example="Первый эпизод сериала")


class EpisodeLocaleCreateRequest(EpisodeLocaleBase, ExampleMixin):
    pass


class EpisodeLocaleUpdateRequest(BaseModel, ExampleMixin):
    language: Optional[str] = Field(None, example="en")
    title: Optional[str] = Field(None, example="Pilot")
    description: Optional[str] = Field(None, example="First episode of the series")


class EpisodeLocaleResponse(EpisodeLocaleBase):
    id: int = Field(..., example=1)
    episode_id: int = Field(..., example=1)

    class Config:
        from_attributes = True
