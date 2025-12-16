from config import celery_settings
from utils.process import process_video_task  # noqa

if __name__ == "__main__":
    app = celery_settings.app
    app.start(argv=["worker", "--loglevel=info"])
