#Copyright (C) 2025 MohammadjavadMorady

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.


"""
This is the main entry point of the web scraping application.

It orchestrates the process of scraping product links from Digikala,
extracting product specifications from those links, and then saving
the collected data using a configured storage backend.
"""
import asyncio
from core.config_loader import ConfigLoader
from core.logger import setup_logger
from scrapers.link_scraper import DigikalaLinkScraper
from scrapers.specs_scraper import DigikalaSpecsScraper
from storage.storage_factory import StorageFactory
from loguru import logger

async def main():
    """
    The main asynchronous function that orchestrates the scraping process.

    It performs the following steps:
    1. Initializes the logger.
    2. Loads the application configuration.
    3. Scrapes product links using DigikalaLinkScraper.
    4. Scrapes product specifications using DigikalaSpecsScraper.
    5. Saves the scraped data using a storage backend from StorageFactory.
    6. Closes the storage connection if it has a 'close' method (e.g., for databases).
    """
    setup_logger()
    config_loader = ConfigLoader()

    # Step 1: Scrape links
    logger.info("Starting link scraping...")
    link_scraper = DigikalaLinkScraper(config_loader)
    urls = link_scraper.scrape_links()
    logger.info(f"Found {len(urls)} product links.")

    # Step 2: Scrape specs
    logger.info("Starting specifications scraping...")
    specs_scraper = DigikalaSpecsScraper(config_loader)
    data = await specs_scraper.scrape_specs(list(urls))
    logger.info(f"Scraped specifications for {len(data)} products.")

    # Step 3: Save data
    logger.info("Starting data saving...")
    storage = StorageFactory.get_storage(config_loader)
    await storage.save(data)
    logger.info("Data saving complete.")

    # Close database connection if using Postgres
    if hasattr(storage, "close"):
        logger.info("Closing storage connection.")
        await storage.close()
        logger.info("Storage connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
