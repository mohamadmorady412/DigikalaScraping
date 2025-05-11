#Copyright (C) 2025 MohammadjavadMorady

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.


from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict
from core.abstractions import SpecsScraper
from core.config_loader import ConfigLoader
from loguru import logger

class DigikalaSpecsScraper(SpecsScraper):
    """
    Scrapes product specifications from individual Digikala product pages.

    This class utilizes Playwright to render dynamic content and BeautifulSoup
    to parse the HTML, extracting product titles and specifications based on
    configurations loaded via ConfigLoader.
    """
    def __init__(self, config_loader: ConfigLoader):
        """
        Initializes the DigikalaSpecsScraper with configurations.

        Args:
            config_loader (ConfigLoader): An instance of ConfigLoader providing
                scraper settings, including file paths, timeouts, and CSS selectors.
        """
        self.config = config_loader.get_scraper_config()
        self.category = self.config["category"]
        self.input_file = self.config["specs_input_file"].format(category=self.category)
        self.page_timeout = self.config["page_timeout"]
        self.wait_state = self.config["wait_state"]
        self.spec_div_id = self.config["spec_div_id"]
        self.spec_keys = self.config["spec_keys"]

    async def scrape_specs(self, urls: List[str]) -> List[Dict]:
        """
        Asynchronously scrapes product specifications from a list of Digikala URLs.

        It launches a headless Chromium browser, navigates to each URL, waits for
        the page to load, extracts product information using `_extract_product_info`,
        and returns a list of dictionaries containing the scraped data.

        Args:
            urls (List[str]): A list of Digikala product URLs to scrape.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary contains
                       the 'نام محصول' (product name), 'لینک' (URL), and
                       other specified specifications for a product.
        """
        all_data = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            for idx, url in enumerate(urls):
                logger.info(f"[{idx+1}/{len(urls)}] Visiting: {url}")
                try:
                    page = await context.new_page()
                    await page.goto(url, timeout=self.page_timeout)
                    await page.wait_for_load_state(self.wait_state)
                    html = await page.content()
                    info = self._extract_product_info(html, url) # Extract product info from the page content
                    all_data.append(info)
                    await page.close()
                except Exception as e:
                    logger.error(f"Failed to fetch {url}: {e}")

            await browser.close()

        logger.info(f"Extracted specs for {len(all_data)} products")
        return all_data

    def _extract_product_info(self, html: str, url: str) -> Dict:
        """
        Extracts product name and specifications from the HTML content of a page.

        It uses BeautifulSoup to parse the HTML and locate the product title
        and specification details based on configured IDs and keys.

        Args:
            html (str): The HTML content of the product page.
            url (str): The URL of the product page.

        Returns:
            Dict: A dictionary containing the 'نام محصول', 'لینک', and extracted
                  specifications.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract product title
        title_tag = soup.find("title")
        name = title_tag.get_text(strip=True) if title_tag else "N/A"

        # Extract specifications
        specs = {}
        spec_div = soup.find("div", id=self.spec_div_id)
        if spec_div:
            rows = spec_div.find_all("div", recursive=True)
            for row in rows:
                ps = row.find_all("p")
                if len(ps) >= 2:
                    key = ps[0].get_text(strip=True)
                    values = [p.get_text(strip=True) for p in ps[1:]]
                    value = " - ".join(values)
                    if key and value:
                        specs[key] = value

        # Prepare the result dictionary
        result = {
            "نام محصول": name,
            "لینک": url
        }
        # Add specific specifications based on configured keys
        for key in self.spec_keys:
            result[key] = specs.get(key, "N/A")

        return result
