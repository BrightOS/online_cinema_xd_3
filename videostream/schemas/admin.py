from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    task_id: str
    status: str
    id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    meta: Optional[dict] = None
