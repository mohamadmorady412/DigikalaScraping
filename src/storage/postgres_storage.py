#Copyright (C) 2025 MohammadjavadMorady

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

import asyncio
from datetime import datetime
from typing import List, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Table, MetaData
from sqlalchemy.sql import text
from core.abstractions import Storage
from core.config_loader import ConfigLoader
from loguru import logger
import re

# Define the base for declarative models
Base = declarative_base()

class ScrapeMetadata(Base):
    """
    Represents metadata about a scraping session in the database.
    """
    __tablename__ = "scrape_metadata"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    record_count = Column(Integer)
    status = Column(String)

class PostgresStorage(Storage):
    """
    Implements the Storage interface to save scraped data into a PostgreSQL database.

    This class dynamically creates a table based on the scraped fields
    and stores the data along with metadata about the scraping process.
    """
    def __init__(self, config_loader: ConfigLoader):
        """
        Initializes the PostgresStorage with configurations and sets up the database connection.

        Args:
            config_loader (ConfigLoader): An instance of ConfigLoader to access
                database and scraper configurations.
        """
        self.config_loader = config_loader
        self.db_config = config_loader.get_database_config()
        self.scraper_config = config_loader.get_scraper_config()
        self.table_name = self.db_config["table_name"]
        self.fieldnames = self.scraper_config["csv_fieldnames"] + \
                          [key for key in self.scraper_config["spec_keys"]]
        self.category = self.scraper_config["category"]

        # Create database URL for async connection
        self.db_url = (
            f"postgresql+asyncpg://{self.db_config['user']}:{self.db_config['password']}"
            f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['name']}"
        )
        # Create an async engine
        self.engine = create_async_engine(self.db_url, echo=False)
        # Create an async session factory
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        # Metadata object for table definitions
        self.metadata = MetaData()

        # Define a helper function to sanitize column names
        def sanitize_column_name(name: str) -> str:
            """
            Sanitizes a string to be a valid PostgreSQL column name.

            Replaces spaces and special characters with underscores,
            ensures it doesn't start with a digit, and removes
            multiple consecutive underscores. Preserves Persian characters.

            Args:
                name (str): The string to sanitize.

            Returns:
                str: A sanitized string suitable for use as a column name.
            """
            name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF_]', '_', name)
            if name and name[0].isdigit():
                name = f"col_{name}"
            name = re.sub(r'_+', '_', name).strip('_')
            return name

        # Define the dynamic table for product data
        self.column_names = []
        columns = [Column("id", Integer, primary_key=True)]
        for field in self.fieldnames:
            column_name = sanitize_column_name(field)
            columns.append(Column(column_name, Text))
            self.column_names.append(column_name)

        logger.info(f"Defining table {self.table_name} with columns: {[col.name for col in columns]}")
        self.product_table = Table(
            self.table_name, self.metadata,
            *columns
        )
        self.sanitize_column_name = sanitize_column_name # Make the function accessible via self

    async def _create_tables(self):
        """
        Asynchronously creates the product data table in the PostgreSQL database.

        It first attempts to drop the table if it exists to ensure a fresh
        schema based on the current configuration.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
                logger.info(f"Dropped existing table {self.table_name} if it existed")
                await conn.run_sync(self.metadata.create_all)
            logger.info(f"Table {self.table_name} created or verified")

            # Verify table existence after creation
            async with self.async_session() as session:
                result = await session.execute(
                    text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"),
                    {"table_name": self.table_name}
                )
                table_exists = result.scalar()
                if table_exists:
                    logger.info(f"Table {self.table_name} exists in the database")
                else:
                    logger.error(f"Table {self.table_name} was not created")
                    raise RuntimeError(f"Failed to create table {self.table_name}")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    async def save(self, data: List[Dict]):
        """
        Asynchronously saves a list of dictionaries (scraped product data)
        into the PostgreSQL database.

        It also records metadata about the scraping session, including
        start and end times, the number of records saved, and the status.

        Args:
            data (List[Dict]): A list of dictionaries, where each dictionary
                               represents the data for a single product.
        """
        start_time = datetime.utcnow()
        status = "SUCCESS"
        try:
            # Ensure the product table exists
            await self._create_tables()

            # Save the scraped product data
            async with self.async_session() as session:
                async with session.begin():
                    for item in data:
                        # Filter data to include only columns defined for the table
                        sanitized_item = {
                            self.sanitize_column_name(key): value
                            for key, value in item.items()
                            if self.sanitize_column_name(key) in self.column_names
                        }
                        logger.debug(f"Inserting data: {sanitized_item}")
                        insert_query = self.product_table.insert().values(**sanitized_item)
                        await session.execute(insert_query)
                await session.commit()
            logger.info(f"Saved {len(data)} products to PostgreSQL table {self.table_name}")

            # Save scraping metadata on success
            async with self.async_session() as session:
                async with session.begin():
                    metadata = ScrapeMetadata(
                        category=self.category,
                        start_time=start_time,
                        end_time=datetime.utcnow(),
                        record_count=len(data),
                        status=status
                    )
                    session.add(metadata)
                    await session.commit()
                logger.info(f"Saved metadata for category {self.category}")

        except Exception as e:
            status = "FAILED"
            logger.error(f"Error saving to PostgreSQL: {e}")
            # Save scraping metadata even on failure
            async with self.async_session() as session:
                async with session.begin():
                    metadata = ScrapeMetadata(
                        category=self.category,
                        start_time=start_time,
                        end_time=datetime.utcnow(),
                        record_count=len(data),
                        status=status
                    )
                    session.add(metadata)
                    await session.commit()
                logger.info(f"Saved failure metadata for category {self.category}")
            raise

    def sanitize_column_name(self, name: str) -> str:
        """
        Sanitizes a string to be a valid PostgreSQL column name.

        This method is the instance version of the static helper function
        defined in __init__.

        Args:
            name (str): The string to sanitize.

        Returns:
            str: A sanitized string suitable for use as a column name.
        """
        name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF_]', '_', name)
        if name and name[0].isdigit():
            name = f"col_{name}"
        name = re.sub(r'_+', '_', name).strip('_')
        return name

    async def close(self):
        """
        Closes the asynchronous database engine.
        """
        await self.engine.dispose()
        logger.info("Database connection closed")
