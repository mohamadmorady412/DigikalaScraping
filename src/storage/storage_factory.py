from core.abstractions import Storage
from storage.csv_storage import CSVStorage
from storage.postgres_storage import PostgresStorage
from core.config_loader import ConfigLoader
from loguru import logger


class StorageFactory:
    @staticmethod
    def get_storage(config_loader: ConfigLoader) -> Storage:
        storage_type = config_loader.get_scraper_config()["storage_type"]
        if storage_type == "csv":
            logger.info("Using CSV storage")
            return CSVStorage(config_loader)
        elif storage_type == "postgres":
            logger.info("Using PostgreSQL storage")
            return PostgresStorage(config_loader)
        else:
            logger.error(f"Unknown storage type: {storage_type}")
            raise ValueError(f"Unknown storage type: {storage_type}")
