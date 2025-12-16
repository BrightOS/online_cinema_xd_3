import os
import tempfile
import subprocess
import json
import requests

import boto3
from config import hls_settings, settings, celery_settings
from utils.logger import logger


s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
bucket_name: str = settings.S3_BUCKET


@celery_settings.app.task(bind=True)
def process_video_task(self, id: str, s3_key: str, webhook_url: str = None):
    try:
        self.update_state(state="PROGRESS", meta={"status": "Загрузка файла из S3"})

        with tempfile.TemporaryDirectory() as tmp_dir:
            mp4_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)[
                "Body"
            ].read()
            mp4_path = os.path.join(tmp_dir, f"{id}.mp4")
            with open(mp4_path, "wb") as f:
                f.write(mp4_obj)

            self.update_state(
                state="PROGRESS", meta={"status": "Конвертация видео в HLS"}
            )

            ffmpeg_command: list[str] = [
                "ffmpeg",
                "-i", mp4_path,
                "-f", "hls",
                # "-c:v", hls_settings.video_codec,
                # "-c:a", hls_settings.audio_codec,
                "-codec", "copy",
                "-start_number", "0",
                "-hls_time", hls_settings.hls_time,
                "-hls_list_size", "0",
                "-hls_segment_filename", os.path.join(tmp_dir, f"{id}-segment_%04d.ts"),
                os.path.join(tmp_dir, f"{id}-playlist.m3u8"),
            ]

            result = subprocess.run(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr.decode()}"
                logger.error(f"{id}: {error_msg}")

                if webhook_url:
                    send_webhook_sync(
                        webhook_url,
                        {
                            "task_id": str(self.request.id),
                            "status": "failed",
                            "id": id,
                            "error": result.stderr.decode().strip(),
                        },
                    )

                raise Exception(error_msg)

            self.update_state(state="PROGRESS", meta={"status": "Загрузка файлов в S3"})

            for root, _, files in os.walk(tmp_dir):
                for file in files:
                    if file.endswith((".ts", ".m3u8")):
                        local_path: str = os.path.join(root, file)
                        with open(local_path, "rb") as f:
                            content = f.read()

                        file_key: str = f"{id}/{file}"
                        s3_client.put_object(
                            Bucket=bucket_name, Key=file_key, Body=content
                        )

            logger.debug(f"{id}: все файлы загружены")

            if webhook_url:
                send_webhook_sync(
                    webhook_url,
                    {
                        "task_id": str(self.request.id),
                        "status": "completed",
                        "id": id,
                        "message": "Video processing completed successfully",
                    },
                )

            return {"status": "success", "id": id}

    except Exception as e:
        if webhook_url:
            send_webhook_sync(
                webhook_url,
                {
                    "task_id": str(self.request.id),
                    "status": "failed",
                    "id": id,
                    "error": str(e),
                },
            )

        logger.error(f"{id}: ошибка при обработке видео: {str(e)}")
        raise


def send_webhook_sync(url: str, payload: dict):
    try:
        response = requests.post(url, json=payload)
        if response.status_code >= 400:
            logger.error(f"Ошибка при отправке webhook: {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка отправки webhook: {str(e)}")
