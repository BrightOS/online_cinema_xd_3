import logging
import sys

from config import settings

logging.basicConfig(
    stream=sys.stdout,
    level=int(settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
