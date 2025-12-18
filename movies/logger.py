import logging
import sys
import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

logger = logging.getLogger("movies")
