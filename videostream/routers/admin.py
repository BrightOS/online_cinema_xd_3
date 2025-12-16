import boto3
from config import settings
from fastapi import APIRouter, File, Query, UploadFile
from schemas.admin import UploadResponse
from utils.process import process_video_task

api_router = APIRouter(tags=["admin"], prefix="/admin")

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
bucket_name: str = settings.S3_BUCKET


@api_router.post("/upload/{id}", responses={200: {"model": UploadResponse}})
async def upload(
    id: str,
    file: UploadFile = File(...),
    webhook_url: str = Query(None),
) -> UploadResponse:
    s3_key: str = f"uploads/{id}.mp4"
    s3_client.upload_fileobj(
        file.file, bucket_name, s3_key, ExtraArgs={"ContentType": "video/mp4"}
    )

    task = process_video_task.delay(id, s3_key, webhook_url)

    return UploadResponse(task_id=task.id, status="processing", id=id)
