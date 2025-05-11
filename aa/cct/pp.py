import asyncio
from playwright.async_api import async_playwright
import pandas as pd # type: ignore
from collections import Counter
import re

def extract_ngrams(s, min_len=4, max_len=12):
    return [s[i:i+n] for n in range(min_len, max_len+1) for i in range(len(s)-n+1)]

async def detect_and_extract_product_links(page):
    anchors = await page.locator("a").all()
    hrefs = []
    for a in anchors:
        href = await a.get_attribute("href")
        if href:
            hrefs.append(href)

    print(f"Total <a> hrefs found: {len(hrefs)}")

    clean_hrefs = [
        href for href in hrefs
        if not href.startswith("javascript") and len(href) > 10
    ]

    ngram_counter = Counter()
    for href in clean_hrefs:
        tokens = extract_ngrams(href)
        ngram_counter.update(tokens)

    product_tokens = [
        token for token, freq in ngram_counter.items()
        if re.search(r'[a-z]{2,}-\d+', token) and freq >= 3
    ]

    print(f"Detected candidate product tokens: {product_tokens}")

    seen = set()
    for href in clean_hrefs:
        for token in product_tokens:
            if token in href:
                full_url = f"https://www.digikala.com{href}" if href.startswith('/') else href
                if full_url not in seen:
                    seen.add(full_url)
                    yield full_url

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            base_url = "https://www.digikala.com/search/category-women-perfume/"
            max_pages = 3
            all_links = []

            for page_num in range(1, max_pages + 1):
                url = f"{base_url}?page={page_num}"
                print(f"\n--- Processing page {page_num} ---")
                await page.goto(url, wait_until="networkidle", timeout=40000)

                async for link in detect_and_extract_product_links(page):
                    all_links.append({'url': link, 'page': page_num})

            await page.close()
            await context.close()
            await browser.close()

            if not all_links:
                print("No product links found.")
                return

            df = pd.DataFrame(all_links)
            df.to_csv("auto_detected_products.csv", index=False, encoding="utf-8-sig")
            print(f"\n✅ Done! Extracted {len(df)} product links to 'auto_detected_products.csv'.")

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
