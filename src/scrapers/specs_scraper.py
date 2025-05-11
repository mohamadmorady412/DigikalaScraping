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
    """

    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader.get_scraper_config()
        self.category = self.config["category"]
        self.input_file = self.config["specs_input_file"].format(category=self.category)
        self.page_timeout = self.config["page_timeout"]
        self.wait_state = self.config["wait_state"]
        self.spec_fields = self.config["spec_fields"]

    async def scrape_specs(self, urls: List[str]) -> List[Dict]:
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
                    info = self._extract_product_info(html, url)
                    all_data.append(info)
                    await page.close()
                except Exception as e:
                    logger.error(f"Failed to fetch {url}: {e}")

            await browser.close()

        logger.info(f"Extracted specs for {len(all_data)} products")
        return all_data

    def _extract_product_info(self, html: str, url: str) -> Dict:
        soup = BeautifulSoup(html, "html.parser")

        # Extract product title
        title_tag = soup.find("title")
        name = title_tag.get_text(strip=True) if title_tag else "N/A"

        result = {
            "نام محصول": name,
            "لینک": url
        }

        # Extract fields based on config-defined selectors
        for label, config in self.spec_fields.items():
            selector = config.get("selector")
            if not selector:
                result[label] = "N/A"
                continue

            elements = soup.select(selector)
            found = False
            for el in elements:
                ps = el.find_all("p")
                if len(ps) >= 2:
                    key_text = ps[0].get_text(strip=True)
                    value_text = " - ".join(p.get_text(strip=True) for p in ps[1:])
                    if key_text == label:
                        result[label] = value_text
                        found = True
                        break
            if not found:
                result[label] = "N/A"

        return result
