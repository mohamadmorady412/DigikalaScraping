from collections import Counter
import re
from typing import List, AsyncGenerator, Set
from playwright.async_api import Page
from ngram import extract_ngrams
from config import ScraperConfig

class LinkProcessor:
    @staticmethod
    async def extract_hrefs(page: Page) -> List[str]:
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
    async def extract_product_links(page: Page, min_len: int, max_len: int) -> AsyncGenerator[str, None]:
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