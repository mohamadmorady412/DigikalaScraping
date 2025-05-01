from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict
from core.abstractions import SpecsScraper
from core.config_loader import ConfigLoader
from loguru import logger

class DigikalaSpecsScraper(SpecsScraper):
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader.get_scraper_config()
        self.category = self.config["category"]
        self.input_file = self.config["specs_input_file"].format(category=self.category)
        self.page_timeout = self.config["page_timeout"]
        self.wait_state = self.config["wait_state"]
        self.spec_div_id = self.config["spec_div_id"]
        self.spec_keys = self.config["spec_keys"]

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

        title_tag = soup.find("title")
        name = title_tag.get_text(strip=True) if title_tag else "N/A"

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

        result = {
            "نام محصول": name,
            "لینک": url
        }
        for key in self.spec_keys:
            result[key] = specs.get(key, "N/A")

        return result
