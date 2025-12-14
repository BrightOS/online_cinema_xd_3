import boto3
from config import settings
from fastapi import APIRouter, File, HTTPException, UploadFile
from utils.process import file_process

api_router = APIRouter(tags=["admin"], prefix="/admin")

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
bucket_name: str = settings.S3_BUCKET


@api_router.post("/upload/{id}")
async def upload(
    id: str,
    file: UploadFile = File(...),
) -> dict[str, str]:
    s3_key: str = f"uploads/{id}.mp4"
    s3_client.upload_fileobj(
        file.file, bucket_name, s3_key, ExtraArgs={"ContentType": "video/mp4"}
    )

    res: str | None = await file_process(id, s3_key)

    if res is not None:
        raise HTTPException(status_code=500, detail=res)

    return {"status": "OK"}
