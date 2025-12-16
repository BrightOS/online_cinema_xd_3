from pydantic import BaseModel, Field
from typing import Optional
from .mixins import ExampleMixin


class EntryLocaleBase(BaseModel):
    language: str = Field(..., example="ru", description="Код языка (ru, en, etc.)")
    title: str = Field(..., example="Мстители: Финал")
    description: Optional[str] = Field(
        None,
        example="Эпическое завершение саги о Мстителях"
    )


class EntryLocaleCreateRequest(EntryLocaleBase, ExampleMixin):
    pass


class EntryLocaleUpdateRequest(BaseModel, ExampleMixin):
    language: Optional[str] = Field(None, example="en")
    title: Optional[str] = Field(None, example="Avengers: Endgame")
    description: Optional[str] = Field(
        None,
        example="Epic conclusion to the Avengers saga"
    )


class EntryLocaleResponse(EntryLocaleBase):
    id: int = Field(..., example=1)
    entry_id: int = Field(..., example=1)

    class Config:
        from_attributes = True
