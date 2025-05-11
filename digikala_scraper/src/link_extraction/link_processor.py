from collections import Counter
import re
from typing import List, Set, AsyncGenerator
from playwright.async_api import Page

class LinkProcessor:
    """Processes and extracts product links from a webpage."""
    
    @staticmethod
    async def extract_hrefs(page: Page, logger: 'logging.Logger') -> List[str]:
        """Extract all href attributes from anchor tags."""
        logger.debug("Extracting hrefs from page")
        anchors = await page.locator("a").all()
        hrefs = [await anchor.get_attribute("href") for anchor in anchors if await anchor.get_attribute("href")]
        logger.info(f"Found {len(hrefs)} hrefs")
        return hrefs

    @staticmethod
    def clean_hrefs(hrefs: List[str], logger: 'logging.Logger') -> List[str]:
        """Filter out invalid or irrelevant hrefs."""
        logger.debug("Cleaning hrefs")
        cleaned = [href for href in hrefs if not href.startswith("javascript") and len(href) > 10]
        logger.info(f"Cleaned to {len(cleaned)} hrefs")
        return cleaned

    @staticmethod
    def extract_ngrams(text: str, min_len: int, max_len: int) -> List[str]:
        """Extract n-grams from a string."""
        return [
            text[i:i+n]
            for n in range(min_len, max_len+1)
            for i in range(len(text)-n+1)
        ]

    @staticmethod
    def identify_product_tokens(hrefs: List[str], min_len: int, max_len: int, min_freq: int, logger: 'logging.Logger') -> List[str]:
        """Identify product tokens based on n-gram frequency."""
        logger.debug("Identifying product tokens")
        ngram_counter = Counter()
        for href in hrefs:
            ngram_counter.update(LinkProcessor.extract_ngrams(href, min_len, max_len))
        tokens = [
            token for token, freq in ngram_counter.items()
            if re.search(r'[a-z]{2,}-\d+', token) and freq >= min_freq
        ]
        logger.info(f"Identified {len(tokens)} product tokens")
        return tokens

    @staticmethod
    async def extract_product_links(page: Page, min_len: int, max_len: int, min_freq: int, logger: 'logging.Logger') -> AsyncGenerator[str, None]:
        """Extract product links based on identified tokens."""
        hrefs = await LinkProcessor.extract_hrefs(page, logger)
        clean_hrefs = LinkProcessor.clean_hrefs(hrefs, logger)
        product_tokens = LinkProcessor.identify_product_tokens(clean_hrefs, min_len, max_len, min_freq, logger)
        logger.debug(f"Product tokens: {product_tokens}")

        seen: Set[str] = set()
        for href in clean_hrefs:
            for token in product_tokens:
                if token in href:
                    full_url = f"https://www.digikala.com{href}" if href.startswith('/') else href
                    if full_url not in seen:
                        seen.add(full_url)
                        yield full_url