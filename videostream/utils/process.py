import io
import subprocess
import boto3
import tempfile
import os
import asyncio

from config import settings, hls_settings
from utils.logger import logger


s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)
bucket_name = settings.S3_BUCKET


async def file_process(id, s3_key):
    with tempfile.TemporaryDirectory() as tmp_dir:
        mp4_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)["Body"].read()
        mp4_path = os.path.join(tmp_dir, f"{id}.mp4")
        with open(mp4_path, 'wb') as f:
            f.write(mp4_obj)

        ffmpeg_command = [
            "ffmpeg",
            "-i", mp4_path,
            "-f", "hls",
            "-c:v", hls_settings.video_codec,
            "-c:a", hls_settings.audio_codec,
            "-start_number", "0",
            "-hls_time", hls_settings.hls_time,
            "-hls_list_size", "0",
            "-hls_segment_filename", os.path.join(tmp_dir, f"{id}-segment_%04d.ts"),
            os.path.join(tmp_dir, f"{id}-playlist.m3u8")
        ]

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        logger.debug(f"{id}: subprocess created")

        await process.wait()

        logger.debug(f"{id}: subprocess finished")

        if process.returncode != 0:
            error = await process.stderr.read()
            logger.error(f"{id}: FFmpeg error: {error.decode()}")
            return f"FFmpeg error: {error.decode()}"

        for root, _, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(('.ts', '.m3u8')):
                    local_path = os.path.join(root, file)
                    with open(local_path, 'rb') as f:
                        content = f.read()

                    file_key = f"{id}/{file}"
                    s3_client.put_object(
                        Bucket=bucket_name, 
                        Key=file_key, 
                        Body=content
                    )
        logger.debug(f"{id}: all files sended")
