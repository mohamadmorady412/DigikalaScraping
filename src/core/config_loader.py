#Copyright (C) 2025 MohammadjavadMorady

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.


"""
This module defines the ConfigLoader class, responsible for loading
configuration settings from a YAML file and environment variables.
It handles loading scraper, headers, and database configurations.
"""
import yaml
from dotenv import load_dotenv
import os
from loguru import logger
from typing import Dict, Any

class ConfigLoader:
    """
    Loads configuration from a YAML file and environment variables.

    Attributes:
        config (Dict[str, Any]): The loaded configuration data from the YAML file.
    """
    def __init__(self, config_path: str = "config/config.yaml", env_path: str = "config/.env"):
        """
        Initializes the ConfigLoader by loading environment variables
        and the configuration from the specified YAML file.

        Args:
            config_path (str, optional): The path to the YAML configuration file.
                                         Defaults to "config/config.yaml".
            env_path (str, optional): The path to the .env file containing
                                      environment variables. Defaults to "config/.env".
        """
        load_dotenv(env_path)
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully")

    def get_scraper_config(self) -> Dict[str, Any]:
        """
        Retrieves the scraper configuration section.

        Returns:
            Dict[str, Any]: A dictionary containing the scraper configuration.
        """
        return self.config["scraper"]

    def get_headers(self) -> Dict[str, str]:
        """
        Retrieves the HTTP headers configuration.

        Returns:
            Dict[str, str]: A dictionary containing HTTP headers.
        """
        return self.config["headers"]

    def get_database_config(self) -> Dict[str, Any]:
        """
        Retrieves the database configuration, merging settings from
        the YAML file with environment variables.

        Returns:
            Dict[str, Any]: A dictionary containing the complete database configuration,
                             with sensitive information loaded from environment variables.
        """
        db_config = self.config["database"]
        db_config.update({
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "name": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        })
        return db_config
