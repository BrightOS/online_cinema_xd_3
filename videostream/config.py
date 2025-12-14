import configparser
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LOG_LEVEL: str = "30"
    S3_BUCKET: str
    S3_ENDPOINT_URL: str
    aws_access_key_id: str
    aws_secret_access_key: str

    class Config:
        env_file = ".env"


class HLSSettings:
    video_codec: str
    audio_codec: str
    hls_time: str

    def __init__(self, configname = 'hls_settings.conf'):
        self.configname = configname
        self.config = configparser.ConfigParser()
        self.config.read(self.configname)

        self.video_codec = self.config['HLS']['video_codec']
        self.audio_codec = self.config['HLS']['audio_codec']
        self.hls_time = self.config['HLS']['hls_time']


settings = Settings()
hls_settings = HLSSettings()
