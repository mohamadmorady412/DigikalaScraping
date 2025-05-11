from bs4 import BeautifulSoup
import json

def scrape_product_specs(html_content):
    # Parsing HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Dictionary to store product specifications
    product_data = {}
    
    # Extract product title
    title_elem = soup.find('h1', {'data-testid': 'pdp-title'})
    product_data['title'] = title_elem.text.strip() if title_elem else 'N/A'
    
    # Extract rating
    rating_elem = soup.find('p', class_='mr-1 text-body-2')
    product_data['rating'] = rating_elem.text.strip() if rating_elem else 'N/A'
    
    # Extract number of reviews
    reviews_elem = soup.find('p', class_='mr-1 text-caption text-neutral-300 whitespace-nowrap')
    product_data['reviews'] = reviews_elem.text.strip() if reviews_elem else 'N/A'
    
    # Extract price and discount
    price_final_elem = soup.find('span', {'data-testid': 'price-final'})
    product_data['final_price'] = price_final_elem.text.strip() if price_final_elem else 'N/A'
    
    price_no_discount_elem = soup.find('span', {'data-testid': 'price-no-discount'})
    product_data['original_price'] = price_no_discount_elem.text.strip() if price_no_discount_elem else 'N/A'
    
    discount_elem = soup.find('span', {'data-testid': 'price-discount-percent'})
    product_data['discount'] = discount_elem.text.strip() if discount_elem else 'N/A'
    
    # Extract seller
    seller_elem = soup.find('div', class_='text-neutral-700 text-body-2')
    product_data['seller'] = seller_elem.text.strip() if seller_elem and 'آرشان' in seller_elem.text else 'N/A'
    
    # Extract specifications
    specs_container = soup.find('div', class_='styles_InfoSection__spec__X1ocW')
    specs = {}
    if specs_container:
        spec_items = specs_container.find_all('li', class_='flex flex-col items-start justify-start bg-neutral-100 p-2 rounded-md')
        for item in spec_items:
            key_elem = item.find('p', class_='text-neutral-500 text-body-2')
            value_elem = item.find('p', class_='text-body2-strong')
            if key_elem and value_elem:
                key = key_elem.text.strip()
                value = value_elem.text.strip()
                specs[key] = value
    
    product_data['specifications'] = specs
    
    return product_data

# Example usage
if __name__ == "__main__":
    # Load HTML content (replace with your HTML content or file)
    with open(r'C:\Users\moham\Documents\GitHub\DigikalaScraping\clean_html_outputs\page_1.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Scrape product data
    product_info = scrape_product_specs(html_content)
    
    # Print the result as JSON
    print(json.dumps(product_info, ensure_ascii=False, indent=2))