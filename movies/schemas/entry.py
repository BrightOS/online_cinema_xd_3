from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from .mixins import ExampleMixin
from .episode import EpisodeResponse
from .entry_locale import EntryLocaleResponse
from .entry_staff import EntryStaffResponse, EntryStaffInput
from .genre import GenreResponse


class EntryBase(BaseModel):
    entry_number: Optional[int] = Field(None, example=1, description="Номер части (для франшиз)")
    duration: Optional[int] = Field(None, example=120, description="Продолжительность в минутах")
    premiere_world: Optional[date] = Field(None, example="2023-01-15", description="Дата мировой премьеры")
    premiere_digital: Optional[date] = Field(None, example="2023-02-01", description="Дата цифровой премьеры")


class EntryCreateRequest(EntryBase, ExampleMixin):
    franchise_id: int = Field(..., example=1, description="ID франшизы")
    type: str = Field(..., example="film", description="Тип: film или season")
    status: str = Field(..., example="finished", description="Статус: announced, ongoing, finished, cancelled")
    rating_mpaa: Optional[str] = Field(None, example="pg13", description="Рейтинг MPAA: g, pg, pg13, r, nc17")
    age_rating: Optional[int] = Field(None, example=13, description="Возрастной рейтинг")
    genres: List[int] = Field(
        example=[1, 2, 3],
        description="Список ID жанров из базы данных"
    )
    staff: List[EntryStaffInput] = Field(
        example=[
            {"person_id": 1, "role": "director", "character_name": None},
            {"person_id": 2, "role": "actor", "character_name": "Главный герой"}
        ],
        description="Список участников съемочной группы"
    )


class EntryUpdateRequest(EntryBase, ExampleMixin):
    type: Optional[str] = Field(None, example="film", description="Тип: film или season")
    status: Optional[str] = Field(None, example="finished", description="Статус")
    rating_mpaa: Optional[str] = Field(None, example="pg13", description="Рейтинг MPAA")
    age_rating: Optional[int] = Field(None, example=16, description="Возрастной рейтинг")
    genres: Optional[List[int]] = Field(
        None,
        example=[1, 3, 7],
        description="Список ID жанров (заменит существующие)"
    )
    staff: Optional[List[EntryStaffInput]] = Field(
        None,
        example=[
            {"person_id": 1, "role": "director", "character_name": None},
            {"person_id": 5, "role": "producer", "character_name": None}
        ],
        description="Список участников съемочной группы (заменит существующих)"
    )


class EntryResponse(EntryBase):
    id: int = Field(..., example=1)
    franchise_id: int = Field(..., example=1)
    type: str = Field(..., example="film")
    status: str = Field(..., example="finished")
    rating_mpaa: Optional[str] = None
    age_rating: Optional[int] = None
    created_at: datetime = Field(..., example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., example="2024-01-20T15:45:00")
    locales: List[EntryLocaleResponse] = []
    genres: List[GenreResponse] = []
    staff: List[EntryStaffResponse] = []
    episodes: List[EpisodeResponse] = []

    class Config:
        from_attributes = True


class EntryBriefResponse(EntryBase):
    id: int = Field(..., example=1)
    franchise_id: int = Field(..., example=1)
    type: str = Field(..., example="film")
    status: str = Field(..., example="finished")
    rating_mpaa: Optional[str] = None
    age_rating: Optional[int] = None
    created_at: datetime = Field(..., example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., example="2024-01-20T15:45:00")
    locales: List[EntryLocaleResponse] = []

    class Config:
        from_attributes = True
