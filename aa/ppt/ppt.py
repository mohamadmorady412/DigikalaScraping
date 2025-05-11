import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from collections import Counter
import re
from typing import List, Set, Dict, AsyncGenerator

# Configuration Module
class ScraperConfig:
    BASE_URL = "https://www.digikala.com/search/category-women-perfume/"
    MAX_PAGES = 3
    OUTPUT_FILE = "auto_detected_products.csv"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    MIN_NGRAM_LEN = 4
    MAX_NGRAM_LEN = 12
    MIN_TOKEN_FREQ = 3

# Ngram Extraction Module
def extract_ngrams(text: str, min_len: int, max_len: int) -> List[str]:
    """Extract n-grams from a string within specified length range."""
    return [
        text[i:i+n] 
        for n in range(min_len, max_len+1) 
        for i in range(len(text)-n+1)
    ]

# Link Processing Module
class LinkProcessor:
    @staticmethod
    async def extract_hrefs(page) -> List[str]:
        """Extract all href attributes from anchor tags on the page."""
        anchors = await page.locator("a").all()
        hrefs = []
        for anchor in anchors:
            href = await anchor.get_attribute("href")
            if href:
                hrefs.append(href)
        print(f"Total <a> hrefs found: {len(hrefs)}")
        return hrefs

    @staticmethod
    def clean_hrefs(hrefs: List[str]) -> List[str]:
        """Filter out invalid or irrelevant hrefs."""
        return [
            href for href in hrefs
            if not href.startswith("javascript") and len(href) > 10
        ]

    @staticmethod
    def identify_product_tokens(hrefs: List[str], min_len: int, max_len: int) -> List[str]:
        """Identify product tokens based on n-gram frequency and pattern."""
        ngram_counter = Counter()
        for href in hrefs:
            tokens = extract_ngrams(href, min_len, max_len)
            ngram_counter.update(tokens)
        
        return [
            token for token, freq in ngram_counter.items()
            if re.search(r'[a-z]{2,}-\d+', token) and freq >= ScraperConfig.MIN_TOKEN_FREQ
        ]

    @staticmethod
    async def extract_product_links(page, min_len: int, max_len: int) -> AsyncGenerator[str, None]:
        """Extract product links based on identified tokens."""
        hrefs = await LinkProcessor.extract_hrefs(page)
        clean_hrefs = LinkProcessor.clean_hrefs(hrefs)
        product_tokens = LinkProcessor.identify_product_tokens(clean_hrefs, min_len, max_len)
        print(f"Detected candidate product tokens: {product_tokens}")

        seen: Set[str] = set()
        for href in clean_hrefs:
            for token in product_tokens:
                if token in href:
                    full_url = (
                        f"https://www.digikala.com{href}" 
                        if href.startswith('/') else href
                    )
                    if full_url not in seen:
                        seen.add(full_url)
                        yield full_url

# File Handling Module
class FileHandler:
    @staticmethod
    def save_to_csv(data: List[Dict], filename: str) -> None:
        """Save extracted links to a CSV file."""
        if not data:
            print("No product links found.")
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n✅ Done! Extracted {len(df)} product links to '{filename}'.")

# Web Scraper Module
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

# Main Execution
async def main():
    """Entry point for the scraper."""
    config = ScraperConfig()
    scraper = WebScraper(config)
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())