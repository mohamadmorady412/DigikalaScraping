from loguru import logger
import sys

def setup_logger():
    logger.remove()
    logger.add("logs/scraper.log", rotation="10 MB", level="INFO")
    logger.add(sys.stderr, level="INFO")
    logger.info("Logger initialized")
