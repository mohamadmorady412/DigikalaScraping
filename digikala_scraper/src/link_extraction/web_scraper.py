import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from typing import Dict, List
import logging
from src.interfaces.scraper import AbstractScraper
from src.link_extraction.link_processor import LinkProcessor

class WebScraper(AbstractScraper):
    """Scraper for extracting product links from Digikala."""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config['scraper']
        self.logger = logger

    async def scrape(self) -> None:
        """Scrape product links from multiple pages."""
        self.logger.info("Starting link extraction")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=self.config['user_agent'])
                page = await context.new_page()

                all_links: List[Dict] = []
                for page_num in range(1, self.config['max_pages'] + 1):
                    url = f"{self.config['base_url']}?page={page_num}"
                    self.logger.info(f"Processing page {page_num}: {url}")
                    await page.goto(url, wait_until="networkidle", timeout=40000)

                    async for link in LinkProcessor.extract_product_links(
                        page,
                        self.config['min_ngram_len'],
                        self.config['max_ngram_len'],
                        self.config['min_token_freq'],
                        self.logger
                    ):
                        all_links.append({'url': link, 'page': page_num})

                await page.close()
                await context.close()
                await browser.close()

                self._save_to_csv(all_links)
                self.logger.info("Link extraction completed")

        except Exception as e:
            self.logger.error(f"Error during link extraction: {e}")
            raise

    def _save_to_csv(self, data: List[Dict]) -> None:
        """Save extracted links to CSV."""
        if not data:
            self.logger.warning("No product links found")
            return
        df = pd.DataFrame(data)
        df.to_csv(self.config['product_csv'], index=False, encoding="utf-8-sig")
        self.logger.info(f"Saved {len(df)} product links to {self.config['product_csv']}")