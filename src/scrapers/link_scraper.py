import requests
import time
from typing import Set
from core.abstractions import LinkScraper
from core.config_loader import ConfigLoader
from loguru import logger

class DigikalaLinkScraper(LinkScraper):
    """
    Scrapes product links from the Digikala website for a specific category.

    This class implements the LinkScraper interface to extract product URLs
    from Digikala's paginated category pages. It handles HTTP requests,
    JSON parsing, and error handling.
    """
    def __init__(self, config_loader: ConfigLoader):
        """
        Initializes the DigikalaLinkScraper with configurations from ConfigLoader.

        Args:
            config_loader (ConfigLoader): An instance of ConfigLoader that provides
                the necessary configurations (scraper settings, headers).
        """
        self.config = config_loader.get_scraper_config()
        self.headers = config_loader.get_headers()
        self.category = self.config["category"]
        self.base_url = self.config["base_url_template"].format(category=self.category)
        self.domain = self.config["domain"]
        self.start_page = self.config["start_page"]
        self.max_pages = self.config["max_pages"]
        self.sleep_duration = self.config["sleep_duration"]
        self.output_file = self.config["link_output_file"].format(category=self.category)

    def scrape_links(self) -> Set[str]:
        """
        Scrapes product links from Digikala category pages.

        This method iterates through paginated category pages, extracts product
        URLs from the JSON response, and saves them to a file.  It handles
        HTTP requests, JSON parsing, error handling, and logging.

        Returns:
            Set[str]: A set of unique product URLs.
        """
        product_urls = set()
        page = self.start_page

        while page <= self.max_pages:
            logger.info(f"Requesting page {page} for category {self.category}")
            params = {"page": page}
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch page {page}, status code: {response.status_code}")
                    break

                data = response.json()
                products = data["data"]["products"]

                if not products:
                    logger.info("No more products found")
                    break

                for item in products:
                    url_data = item.get("url", {})
                    uri = url_data.get("uri")
                    if uri:
                        full_url = f"{self.domain}{uri}"
                        product_urls.add(full_url)

                page += 1
                time.sleep(self.sleep_duration)
            except Exception as e:
                logger.error(f"Error parsing page {page}: {e}")
                break

        with open(self.output_file, "w", encoding="utf-8") as f:
            for url in sorted(product_urls):
                f.write(url + "\n")

        logger.info(f"Saved {len(product_urls)} product links to {self.output_file}")
        return product_urls
