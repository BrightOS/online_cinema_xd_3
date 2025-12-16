from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .mixins import ExampleMixin
from .entry import EntryBriefResponse
from .franchise_locale import FranchiseLocaleResponse


class FranchiseBase(BaseModel):
    pass


# да, реквест пустой. тут нам нечего передавать, когда мы создаём новую франшизу
class FranchiseCreateRequest(FranchiseBase, ExampleMixin):
    pass


class FranchiseResponse(FranchiseBase, ExampleMixin):
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., example="2024-01-20T15:45:00")
    locales: List[FranchiseLocaleResponse] = []
    entries: List[EntryBriefResponse] = []

    class Config:
        from_attributes = True


class FranchiseBriefResponse(FranchiseBase):
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., example="2024-01-20T15:45:00")
    locales: List[FranchiseLocaleResponse] = []

    class Config:
        from_attributes = True
