from pydantic import BaseModel, Field
from .mixins import ExampleMixin


class GenreBase(BaseModel):
    name: str = Field(..., example="Романтика", description="Название жанра")


class GenreCreateRequest(GenreBase, ExampleMixin):
    pass


class GenreUpdateRequest(GenreBase, ExampleMixin):
    pass


class GenreResponse(GenreBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True
