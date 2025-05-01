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

Base = declarative_base()

class ScrapeMetadata(Base):
    __tablename__ = "scrape_metadata"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    record_count = Column(Integer)
    status = Column(String)

class PostgresStorage(Storage):
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.db_config = config_loader.get_database_config()
        self.scraper_config = config_loader.get_scraper_config()
        self.table_name = self.db_config["table_name"]
        self.fieldnames = self.scraper_config["csv_fieldnames"] + \
                         [key for key in self.scraper_config["spec_keys"]]
        self.category = self.scraper_config["category"]
        
        # Create database URL
        self.db_url = (
            f"postgresql+asyncpg://{self.db_config['user']}:{self.db_config['password']}"
            f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['name']}"
        )
        self.engine = create_async_engine(self.db_url, echo=False)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.metadata = MetaData()

        # Sanitize column names to avoid invalid characters
        def sanitize_column_name(name: str) -> str:
            # Replace spaces and special characters with underscores, preserve Persian characters
            name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF_]', '_', name)
            # Ensure the name doesn't start with a number
            if name and name[0].isdigit():
                name = f"col_{name}"
            # Remove multiple consecutive underscores
            name = re.sub(r'_+', '_', name).strip('_')
            return name

        # Define dynamic table for products
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

    async def _create_tables(self):
        try:
            # Drop the table if it exists to ensure fresh creation
            async with self.engine.begin() as conn:
                await conn.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
                logger.info(f"Dropped existing table {self.table_name} if it existed")
                await conn.run_sync(self.metadata.create_all)
            logger.info(f"Table {self.table_name} created or verified")
            
            # Verify table existence
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
        start_time = datetime.utcnow()
        status = "SUCCESS"
        try:
            # Create tables
            await self._create_tables()

            # Save products
            async with self.async_session() as session:
                async with session.begin():
                    for item in data:
                        # Filter data to include only defined columns
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

            # Save metadata
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
            # Save metadata even on failure
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
        # Same logic as in __init__ for consistency
        name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF_]', '_', name)
        if name and name[0].isdigit():
            name = f"col_{name}"
        name = re.sub(r'_+', '_', name).strip('_')
        return name

    async def close(self):
        await self.engine.dispose()
        logger.info("Database connection closed")
