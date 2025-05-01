"""
This module defines the StorageFactory class, responsible for creating
instances of different storage backends (e.g., CSV, PostgreSQL)
based on the application's configuration.
"""
from core.abstractions import Storage
from storage.csv_storage import CSVStorage
from storage.postgres_storage import PostgresStorage
from core.config_loader import ConfigLoader
from loguru import logger
from typing import Type

class StorageFactory:
    """
    A factory class to create instances of storage backends.

    The type of storage to instantiate is determined by the 'storage_type'
    setting in the scraper configuration.
    """
    @staticmethod
    def get_storage(config_loader: ConfigLoader) -> Storage:
        """
        Creates and returns an instance of the configured storage backend.

        Args:
            config_loader (ConfigLoader): An instance of ConfigLoader providing
                access to the application's configuration.

        Returns:
            Storage: An instance of either CSVStorage or PostgresStorage,
                     depending on the 'storage_type' configuration.

        Raises:
            ValueError: If the 'storage_type' in the configuration is unknown.
        """
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
