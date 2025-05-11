import yaml
from typing import Dict
import logging

def load_config(file_path: str) -> Dict:
    """Load configuration from a YAML file."""
    logger = logging.getLogger("DigikalaScraper")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if not config or 'scraper' not in config or 'patterns' not in config:
            raise ValueError("Invalid configuration file structure")
        logger.info(f"Configuration loaded from {file_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config from {file_path}: {e}")
        raise