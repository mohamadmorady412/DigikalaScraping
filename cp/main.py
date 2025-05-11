# first part
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

# secend part
import pandas as pd
import os
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")

    # حذف کامل تگ‌های ناخواسته: script, style, symbol
    for tag in soup(["script", "style", "symbol"]):
        tag.decompose()

    # حذف تمام تگ‌های <link>
    for link in soup.find_all("link"):
        link.decompose()

    # حذف تگ <a> و نگه‌داشتن متن داخلی آن
    for a in soup.find_all("a"):
        a.unwrap()

    return str(soup)

def save_clean_html_pages(csv_file_path, output_dir="clean_html_outputs"):
    # خواندن URLها از فایل CSV
    df = pd.read_csv(csv_file_path)
    urls = df.iloc[:, 0].dropna().tolist()

    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for idx, url in enumerate(urls):
            try:
                print(f"🔄 در حال بارگذاری: {url}")
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")  # منتظر بارگذاری کامل JS

                raw_html = page.content()
                cleaned_html = clean_html(raw_html)

                filename = f"page_{idx+1}.html"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(cleaned_html)

                print(f"✅ ذخیره شد: {filepath}")
                time.sleep(1)

            except Exception as e:
                print(f"❌ خطا در بارگذاری {url}: {e}")

        browser.close()

if __name__ == "__main__":
    input_csv = "auto_detected_products.csv"
    save_clean_html_pages(input_csv)

# trr part
from bs4 import BeautifulSoup
import json
import csv
import re
from pathlib import Path

def scrape_product_specs(html_content):
    # Parsing HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Dictionary to store product specifications
    product_data = {}
    
    # Helper function to clean text
    def clean_text(text):
        if text is None or isinstance(text, str) and not text.strip():
            return 'N/A'
        return re.sub(r'\s+', ' ', str(text).strip())

    # Find title (looking for common title tags)
    title_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|product|name', re.I)) or \
                 soup.find(['h1', 'h2', 'h3'])
    product_data['title'] = clean_text(title_elem.text) if title_elem else 'N/A'
    
    # Find rating (looking for numeric patterns or star ratings)
    rating_elem = soup.find(string=re.compile(r'\d+\.?\d*\s*(?:out of|\/|\|)\s*\d+')) or \
                  soup.find(class_=re.compile(r'rating|score', re.I))
    product_data['rating'] = clean_text(rating_elem) if rating_elem else 'N/A'
    
    # Find number of reviews
    reviews_elem = soup.find(string=re.compile(r'\d+\s*(?:review|comment|نظر)', re.I)) or \
                   soup.find(class_=re.compile(r'review|comment|count', re.I))
    product_data['reviews'] = clean_text(reviews_elem) if reviews_elem else 'N/A'
    
    # Find price (looking for currency symbols or price-related classes)
    price_elem = soup.find(string=re.compile(r'[\$€£]?[\d,.]+\s*(?:تومان|USD|EUR)?', re.I)) or \
                 soup.find(class_=re.compile(r'price|cost|value', re.I))
    product_data['final_price'] = clean_text(price_elem) if price_elem else 'N/A'
    
    # Find original price (looking for strikethrough or original price classes)
    original_price_elem = soup.find(class_=re.compile(r'original|list-price|strikethrough', re.I)) or \
                         soup.find('s') or soup.find('del')
    product_data['original_price'] = clean_text(original_price_elem.text) if original_price_elem else 'N/A'
    
    # Find discount
    discount_elem = soup.find(string=re.compile(r'\d+%')) or \
                    soup.find(class_=re.compile(r'discount|sale|off', re.I))
    product_data['discount'] = clean_text(discount_elem) if discount_elem else 'N/A'
    
    # Find seller
    seller_elem = soup.find(class_=re.compile(r'seller|vendor|merchant', re.I)) or \
                  soup.find(string=re.compile(r'آرشان|sold by|فروشنده', re.I))
    product_data['seller'] = clean_text(seller_elem.text if isinstance(seller_elem, BeautifulSoup) else seller_elem) if seller_elem else 'N/A'
    
    # Find specifications (looking for key-value pair patterns)
    specs = {}
    specs_container = soup.find(['div', 'section', 'ul'], class_=re.compile(r'spec|info|details', re.I)) or \
                     soup.find(['div', 'section', 'ul'])
    if specs_container:
        # Look for list items or divs containing key-value pairs
        spec_items = specs_container.find_all(['li', 'div', 'p'], class_=re.compile(r'spec|item|detail', re.I)) or \
                     specs_container.find_all(['li', 'div', 'p'])
        for item in spec_items:
            # Try to find key-value pairs within each item
            key_elem = item.find(['p', 'span', 'div'], class_=re.compile(r'key|label|title', re.I)) or \
                       item.find(['p', 'span', 'div'])
            value_elem = item.find(['p', 'span', 'div'], class_=re.compile(r'value|content|data', re.I)) or \
                        item.find_next(['p', 'span', 'div'])
            if key_elem and value_elem:
                key = clean_text(key_elem.text)
                value = clean_text(value_elem.text)
                if key and value and key != value:  # Ensure key and value are different
                    specs[key] = value
    
    product_data['specifications'] = specs
    
    return product_data

def save_to_csv(product_data, output_file='product_data.csv'):
    # Prepare CSV headers
    headers = ['title', 'rating', 'reviews', 'final_price', 'original_price', 'discount', 'seller']
    # Add specification keys to headers
    spec_headers = list(product_data['specifications'].keys())
    headers.extend(spec_headers)
    
    # Prepare data row
    row = {
        'title': product_data['title'],
        'rating': product_data['rating'],
        'reviews': product_data['reviews'],
        'final_price': product_data['final_price'],
        'original_price': product_data['original_price'],
        'discount': product_data['discount'],
        'seller': product_data['seller']
    }
    # Add specification values
    for spec_key in spec_headers:
        row[spec_key] = product_data['specifications'].get(spec_key, 'N/A')
    
    # Write to CSV
    file_exists = Path(output_file).exists()
    with open(output_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# Example usage
if __name__ == "__main__":
    # Load HTML content
    with open(r'C:\Users\moham\Documents\GitHub\DigikalaScraping\clean_html_outputs\page_1.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Scrape product data
    product_info = scrape_product_specs(html_content)
    
    # Save to CSV
    save_to_csv(product_info)
    
    # Optional: Print the result as JSON for verification
    print(json.dumps(product_info, ensure_ascii=False, indent=2))