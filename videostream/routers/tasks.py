from celery.result import AsyncResult
from config import celery_settings
from fastapi import APIRouter
from schemas.admin import TaskStatusResponse

api_router = APIRouter(tags=["tasks"], prefix="/tasks")


@api_router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    task_result = AsyncResult(str(task_id), app=celery_settings.app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }

    if task_result.status == "PROGRESS":
        response["meta"] = task_result.info

    return response
