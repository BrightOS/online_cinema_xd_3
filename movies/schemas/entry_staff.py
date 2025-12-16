from pydantic import BaseModel, Field
from typing import Optional
from .mixins import ExampleMixin


class EntryStaffBase(BaseModel):
    role: str = Field(
        ...,
        example="actor",
        description="Role: actor, director, producer, writer, composer, other",
    )
    character_name: Optional[str] = Field(
        None,
        example="Иван Царевич",
        description="Character name (for actors)",
    )


class EntryStaffCreateRequest(EntryStaffBase, ExampleMixin):
    entry_id: int = Field(..., example=1)
    person_id: int = Field(..., example=1)


class EntryStaffUpdateRequest(BaseModel, ExampleMixin):
    role: Optional[str] = Field(None, example="director")
    character_name: Optional[str] = Field(None, example="Василиса Прекрасная")


class EntryStaffResponse(EntryStaffBase):
    entry_id: int = Field(..., example=1)
    person_id: int = Field(..., example=1)
    role: str

    class Config:
        from_attributes = True


class EntryStaffInput(BaseModel, ExampleMixin):
    person_id: int = Field(..., example=1, description="ID персоны из базы данных")
    role: str = Field(
        ...,
        example="actor",
        description="Роль: actor, director, producer, writer, composer, other"
    )
    character_name: Optional[str] = Field(
        None,
        example="Железный человек",
        description="Имя персонажа (только для актеров)"
    )
