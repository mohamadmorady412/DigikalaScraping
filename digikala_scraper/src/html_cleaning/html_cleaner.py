import pandas as pd
import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging
from typing import Dict
from src.interfaces.scraper import AbstractScraper

class HTMLCleaner(AbstractScraper):
    """Cleans HTML content from product pages."""

    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config['scraper']
        self.logger = logger

    async def scrape(self) -> None:
        """Clean HTML pages and save to output directory."""
        self.logger.info("Starting HTML cleaning")
        try:
            df = pd.read_csv(self.config['product_csv'])
            urls = df['url'].dropna().tolist()
            if not urls:
                self.logger.warning("No URLs found in CSV")
                return

            os.makedirs(self.config['output_dir'], exist_ok=True)
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                for idx, url in enumerate(urls):
                    try:
                        self.logger.info(f"Processing URL: {url}")
                        await page.goto(url, timeout=30000)
                        await page.wait_for_load_state("networkidle")
                        raw_html = await page.content()
                        cleaned_html = self._clean_html(raw_html)
                        self._save_html(cleaned_html, idx + 1)
                        await asyncio.sleep(1)
                    except Exception as e:
                        self.logger.error(f"Error processing {url}: {e}")

                await browser.close()
            self.logger.info("HTML cleaning completed")

        except Exception as e:
            self.logger.error(f"Error during HTML cleaning: {e}")
            raise

    def _clean_html(self, raw_html: str) -> str:
        """Clean raw HTML by removing unwanted tags."""
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "symbol", "link"]):
            tag.decompose()
        for a in soup.find_all("a"):
            a.unwrap()
        return str(soup)

    def _save_html(self, html: str, index: int) -> None:
        """Save cleaned HTML to file."""
        filename = f"page_{index}.html"
        filepath = os.path.join(self.config['output_dir'], filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        self.logger.info(f"Saved cleaned HTML to {filepath}")
