from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from .mixins import ExampleMixin


class PersonBase(BaseModel):
    name: str = Field(..., example="Иван Иванов")
    en_name: Optional[str] = Field(None, example="Ivan Ivanov")
    birth_date: Optional[date] = Field(None, example="1980-05-20")


class PersonCreateRequest(PersonBase, ExampleMixin):
    pass


class PersonUpdateRequest(PersonBase, ExampleMixin):
    name: str = Field(..., example="Иван Иванов")
    en_name: Optional[str] = Field(None, example="Ivan Ivanov")
    birth_date: Optional[date] = Field(None, example="1980-05-20")


class PersonResponse(PersonBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True
