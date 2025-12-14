import boto3
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import boto3
from botocore.exceptions import ClientError

from config import settings


api_router = APIRouter(tags=[""])

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)
bucket_name = settings.S3_BUCKET


@api_router.get("/file/{id}/{filename}")
async def stream_audio_hls(id: str, filename: str):
    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=f'{id}/{filename}')
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    if filename.endswith(".m3u8"):
        media_type = "application/vnd.apple.mpegurl"
    elif filename.endswith(".ts"):
        media_type = "video/mp2t"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(
        content=s3_response['Body'].iter_chunks(),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*"
        }
    )
