from pydantic import BaseModel, Field
from typing import Optional
from .mixins import ExampleMixin


class FranchiseLocaleBase(BaseModel):
    language: str = Field(..., example="ru")
    title: str = Field(..., example="Кинематографическая вселенная Marvel")
    description: Optional[str] = Field(
        None,
        example="Серия фильмов о супергероях Marvel"
    )


class FranchiseLocaleCreateRequest(FranchiseLocaleBase, ExampleMixin):
    pass


class FranchiseLocaleUpdateRequest(BaseModel, ExampleMixin):
    language: Optional[str] = Field(None, example="en")
    title: Optional[str] = Field(None, example="Marvel Cinematic Universe")
    description: Optional[str] = Field(
        None,
        example="Series of superhero films based on Marvel Comics"
    )


class FranchiseLocaleResponse(FranchiseLocaleBase):
    id: int = Field(..., example=1)
    franchise_id: int = Field(..., example=1)

    class Config:
        from_attributes = True
