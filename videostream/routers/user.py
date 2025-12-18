import boto3
from botocore.exceptions import ClientError
from config import settings
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas.error import ErrorResponse
from utils.logger import logger

from utils.metrics import VIDEO_STREAMING_REQUESTS_TOTAL, VIDEO_PLAYBACK_ERRORS_TOTAL

api_router = APIRouter(tags=["user"])

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
bucket_name: str = settings.S3_BUCKET


@api_router.get(
    "/file/{id}/{filename}",
    responses={
        200: {
            "content": {
                "application/vnd.apple.mpegurl": {},
                "video/mp2t": {},
                "application/octet-stream": {}
            }
        },
        404: {"model": ErrorResponse}
    }
)
async def stream_audio_hls(id: str, filename: str) -> StreamingResponse:
    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=f"{id}/{filename}")
    except ClientError as e:
        VIDEO_PLAYBACK_ERRORS_TOTAL.labels(error_type="s3_client_error", movie_id=id).inc()
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    if filename.endswith(".m3u8"):
        media_type = "application/vnd.apple.mpegurl"
        VIDEO_STREAMING_REQUESTS_TOTAL.labels(type="playlist", movie_id=id).inc()
    elif filename.endswith(".ts"):
        media_type = "video/mp2t"
        VIDEO_STREAMING_REQUESTS_TOTAL.labels(type="segment", movie_id=id).inc()
    else:
        media_type = "application/octet-stream"
        VIDEO_STREAMING_REQUESTS_TOTAL.labels(type="other", movie_id=id).inc()

    logger.debug(f"{id}/{filename}: file streaming")

    return StreamingResponse(
        content=s3_response["Body"].iter_chunks(),
        media_type=media_type,
        headers={"Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*"},
    )
