""" import asyncio
from core.config_loader import ConfigLoader
from core.logger import setup_logger
from scrapers.link_scraper import DigikalaLinkScraper
from scrapers.specs_scraper import DigikalaSpecsScraper
from storage.storage_factory import StorageFactory
from loguru import logger

async def main():
    setup_logger()
    config_loader = ConfigLoader()

    # Step 1: Scrape links
    link_scraper = DigikalaLinkScraper(config_loader)
    urls = link_scraper.scrape_links()

    # Step 2: Scrape specs
    specs_scraper = DigikalaSpecsScraper(config_loader)
    data = await specs_scraper.scrape_specs(list(urls))

    # Step 3: Save data
    storage = StorageFactory.get_storage(config_loader)
    await storage.save(data)

    # Close database connection if using Postgres
    if hasattr(storage, "close"):
        await storage.close()

if __name__ == "__main__":
    asyncio.run(main())
     """

import asyncio
from core.config_loader import ConfigLoader
from core.logger import setup_logger
from scrapers.link_scraper import DigikalaLinkScraper
from scrapers.specs_scraper import DigikalaSpecsScraper
from storage.storage_factory import StorageFactory
from loguru import logger

async def main():
    setup_logger()
    config_loader = ConfigLoader()

    # Step 1: Scrape links
    link_scraper = DigikalaLinkScraper(config_loader)
    urls = link_scraper.scrape_links()

    # Step 2: Scrape specs
    specs_scraper = DigikalaSpecsScraper(config_loader)
    data = await specs_scraper.scrape_specs(list(urls))

    # Step 3: Save data
    storage = StorageFactory.get_storage(config_loader)
    await storage.save(data)

    # Close database connection if using Postgres
    if hasattr(storage, "close"):
        await storage.close()

if __name__ == "__main__":
    asyncio.run(main())