from bs4 import BeautifulSoup
import csv
import re
from pathlib import Path
import logging
from typing import Dict, List
from src.interfaces.scraper import AbstractScraper

class ProductScraper(AbstractScraper):
    """Scrapes product details from cleaned HTML files."""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config['scraper']
        self.patterns = config['patterns']
        self.logger = logger

    def scrape(self) -> None:
        """Scrape product details from HTML files."""
        self.logger.info("Starting product scraping")
        try:
            html_files = Path(self.config['html_input_dir']).glob("*.html")
            for html_file in html_files:
                self.logger.info(f"Processing HTML file: {html_file}")
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                product_data = self._scrape_product_specs(html_content)
                self._save_to_csv(product_data)
            self.logger.info("Product scraping completed")
        except Exception as e:
            self.logger.error(f"Error during product scraping: {e}")
            raise

    def _scrape_product_specs(self, html_content: str) -> Dict:
        """Extract product specifications from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        product_data = {}

        def clean_text(text) -> str:
            if text is None or (isinstance(text, str) and not text.strip()):
                return 'N/A'
            return re.sub(r'\s+', ' ', str(text).strip())

        # Title
        title_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|product|name', re.I)) or \
                    soup.find(['h1', 'h2', 'h3'])
        product_data['title'] = clean_text(title_elem.text) if title_elem else 'N/A'

        # Rating
        rating_elem = soup.find(string=re.compile(self.patterns['rating'], re.I)) or \
                     soup.find(class_=re.compile(r'rating|score', re.I))
        product_data['rating'] = clean_text(rating_elem) if rating_elem else 'N/A'

        # Reviews
        reviews_elem = soup.find(string=re.compile(self.patterns['reviews'], re.I)) or \
                      soup.find(class_=re.compile(r'review|comment|count', re.I))
        product_data['reviews'] = clean_text(reviews_elem) if reviews_elem else 'N/A'

        # Price
        price_elem = soup.find(string=re.compile(self.patterns['price'], re.I)) or \
                    soup.find(class_=re.compile(r'price|cost|value', re.I))
        product_data['final_price'] = clean_text(price_elem) if price_elem else 'N/A'

        # Original Price
        original_price_elem = soup.find(class_=re.compile(r'original|list-price|strikethrough', re.I)) or \
                            soup.find('s') or soup.find('del')
        product_data['original_price'] = clean_text(original_price_elem.text) if original_price_elem else 'N/A'

        # Discount
        discount_elem = soup.find(string=re.compile(self.patterns['discount'], re.I)) or \
                       soup.find(class_=re.compile(r'discount|sale|off', re.I))
        product_data['discount'] = clean_text(discount_elem) if discount_elem else 'N/A'

        # Seller
        seller_elem = soup.find(class_=re.compile(r'seller|vendor|merchant', re.I)) or \
                     soup.find(string=re.compile(self.patterns['seller'], re.I))
        product_data['seller'] = clean_text(seller_elem.text if isinstance(seller_elem, BeautifulSoup) else seller_elem) if seller_elem else 'N/A'

        # Specifications
        specs = {}
        specs_container = soup.find(['div', 'section', 'ul'], class_=re.compile(r'spec|info|details', re.I)) or \
                         soup.find(['div', 'section', 'ul'])
        if specs_container:
            spec_items = specs_container.find_all(['li', 'div', 'p'], class_=re.compile(r'spec|item|detail', re.I)) or \
                        specs_container.find_all(['li', 'div', 'p'])
            for item in spec_items:
                key_elem = item.find(['p', 'span', 'div'], class_=re.compile(r'key|label|title', re.I)) or \
                          item.find(['p', 'span', 'div'])
                value_elem = item.find(['p', 'span', 'div'], class_=re.compile(r'value|content|data', re.I)) or \
                            item.find_next(['p', 'span', 'div'])
                if key_elem and value_elem:
                    key = clean_text(key_elem.text)
                    value = clean_text(value_elem.text)
                    if key and value and key != value:
                        specs[key] = value
        product_data['specifications'] = specs

        return product_data

    def _save_to_csv(self, product_data: Dict) -> None:
        """Save product data to CSV."""
        headers = ['title', 'rating', 'reviews', 'final_price', 'original_price', 'discount', 'seller']
        spec_headers = list(product_data['specifications'].keys())
        headers.extend(spec_headers)

        row = {
            'title': product_data['title'],
            'rating': product_data['rating'],
            'reviews': product_data['reviews'],
            'final_price': product_data['final_price'],
            'original_price': product_data['original_price'],
            'discount': product_data['discount'],
            'seller': product_data['seller']
        }
        for spec_key in spec_headers:
            row[spec_key] = product_data['specifications'].get(spec_key, 'N/A')

        file_exists = Path(self.config['product_data_csv']).exists()
        with open(self.config['product_data_csv'], 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        self.logger.info(f"Saved product data to {self.config['product_data_csv']}")