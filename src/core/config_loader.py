import yaml
from dotenv import load_dotenv
import os
from loguru import logger

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml", env_path: str = "config/.env"):
        load_dotenv(env_path)
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully")

    def get_scraper_config(self):
        return self.config["scraper"]

    def get_headers(self):
        return self.config["headers"]

    def get_database_config(self):
        db_config = self.config["database"]
        db_config.update({
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "name": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        })
        return db_config
