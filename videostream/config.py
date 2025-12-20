import configparser

from celery import Celery
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = "30"
    S3_BUCKET: str
    S3_ENDPOINT_URL: str
    aws_access_key_id: str
    aws_secret_access_key: str
    REDIS_URL: str

    class Config:
        env_file: str = ".env"


class HLSSettings:
    video_codec: str
    audio_codec: str
    hls_time: str

    def __init__(self, configname="hls_settings.conf") -> None:
        self.configname: str = configname
        self.config = configparser.ConfigParser()
        self.config.read(self.configname)

        self.video_codec = self.config["HLS"]["video_codec"]
        self.audio_codec = self.config["HLS"]["audio_codec"]
        self.hls_time = self.config["HLS"]["hls_time"]


class CelerySettings:
    def __init__(self) -> None:
        self.app = Celery("videostream")
        self.app.conf.broker_url = settings.REDIS_URL
        self.app.conf.result_backend = settings.REDIS_URL

        self.app.conf.include = ["utils.process"]
        self.app.conf.task_serializer = "json"
        self.app.conf.accept_content = ["json"]
        self.app.conf.result_serializer = "json"
        self.app.conf.timezone = "UTC"


settings = Settings()
hls_settings = HLSSettings()
celery_settings = CelerySettings()
