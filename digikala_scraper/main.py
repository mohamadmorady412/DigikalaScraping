import asyncio
import logging
from src.config_loader import load_config
from src.logging_setup import setup_logging
from src.link_extraction.web_scraper import WebScraper
from src.html_cleaning.html_cleaner import HTMLCleaner
from src.product_scraping.product_scraper import ProductScraper
from src.interfaces.scraper import AbstractScraper

class ScraperFactory:
    """Factory for creating scraper instances."""
    @staticmethod
    def create_scraper(scraper_type: str, config: dict, logger: logging.Logger) -> AbstractScraper:
        if scraper_type == "link_extraction":
            return WebScraper(config, logger)
        elif scraper_type == "html_cleaning":
            return HTMLCleaner(config, logger)
        elif scraper_type == "product_scraping":
            return ProductScraper(config, logger)
        raise ValueError(f"Unknown scraper type: {scraper_type}")

async def main():
    """Main entry point for the Digikala scraper."""
    logger = setup_logging()
    logger.info("Starting Digikala scraper")

    try:
        config = load_config(r"C:\Users\moham\Documents\GitHub\DigikalaScraping\digikala_scraper\config\config.yaml")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    factory = ScraperFactory()
    
    link_scraper = factory.create_scraper("link_extraction", config, logger)
    try:
        await link_scraper.scrape()
    except Exception as e:
        logger.error(f"Link extraction failed: {e}")
        return

    html_cleaner = factory.create_scraper("html_cleaning", config, logger)
    try:
        html_cleaner.scrape()
    except Exception as e:
        logger.error(f"HTML cleaning failed: {e}")
        return

    product_scraper = factory.create_scraper("product_scraping", config, logger)
    try:
        product_scraper.scrape()
    except Exception as e:
        logger.error(f"Product scraping failed: {e}")
        return

    logger.info("Scraping completed successfully")

if __name__ == "__main__":
    asyncio.run(main())