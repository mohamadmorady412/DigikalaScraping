from playwright.async_api import async_playwright
from typing import List, Dict
from config import ScraperConfig
from link_processor import LinkProcessor
from file_handler import FileHandler

class WebScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config

    async def scrape(self) -> None:
        """Main scraping logic."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=self.config.USER_AGENT)
                page = await context.new_page()

                all_links: List[Dict] = []
                for page_num in range(1, self.config.MAX_PAGES + 1):
                    url = f"{self.config.BASE_URL}?page={page_num}"
                    print(f"\n--- Processing page {page_num} ---")
                    await page.goto(url, wait_until="networkidle", timeout=40000)

                    async for link in LinkProcessor.extract_product_links(
                        page, 
                        self.config.MIN_NGRAM_LEN, 
                        self.config.MAX_NGRAM_LEN
                    ):
                        all_links.append({'url': link, 'page': page_num})

                await page.close()
                await context.close()
                await browser.close()

                FileHandler.save_to_csv(all_links, self.config.OUTPUT_FILE)

        except Exception as e:
            print(f"Error in scraper: {str(e)}")