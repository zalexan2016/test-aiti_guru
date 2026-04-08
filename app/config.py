import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
except KeyError:
    logger.error("DATABASE_URL environment variable is not set. Application cannot start.")
    sys.exit(1)
