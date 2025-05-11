import logging
import os
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Configure logging for the scraper."""
    logger = logging.getLogger("DigikalaScraper")
    logger.setLevel(logging.INFO)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler("logs/scraper.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger