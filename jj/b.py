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