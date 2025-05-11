import asyncio
from config import ScraperConfig
from scraper import WebScraper

async def main():
    """Entry point for the scraper."""
    config = ScraperConfig()
    scraper = WebScraper(config)
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())