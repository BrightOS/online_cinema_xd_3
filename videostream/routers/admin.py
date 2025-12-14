import boto3
from fastapi import APIRouter, UploadFile, File, HTTPException

from config import settings
from utils.process import file_process


api_router = APIRouter(tags=["admin"])

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)
bucket_name = settings.S3_BUCKET


@api_router.post("/upload/{id}")
async def upload(
    id: str,
    file: UploadFile = File(...),
):
    s3_key = f"uploads/{id}.mp4"
    s3_client.upload_fileobj(file.file, bucket_name, s3_key, ExtraArgs={"ContentType": "video/mp4"})

    res = await file_process(id, s3_key)

    if res is not None:
        raise HTTPException(status_code=500, detail=res)

    return {
        'status': 'OK'
    }
