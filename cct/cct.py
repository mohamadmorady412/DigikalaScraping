import asyncio
from playwright.async_api import async_playwright
import pandas as pd # type: ignore
import re
from collections import Counter

async def guess_product_links(page):
    # دریافت تمام لینک‌ها
    anchors = await page.locator("a").all()
    hrefs = []
    for a in anchors:
        href = await a.get_attribute("href")
        if href:
            hrefs.append(href)

    # شمارش الگوهای پرتکرار
    pattern_counts = Counter()

    product_like_links = []
    for href in hrefs:
        if not href.startswith("http"):
            href = f"https://www.digikala.com{href}"

        # بررسی تطابق با الگوهای شبیه محصول، مثلاً /product/dkp-12345/
        match = re.search(r'/product/[^/]+/?', href)#TODO
        if match:
            pattern = match.group()
            pattern_counts[pattern] += 1
            product_like_links.append(href)

    if not product_like_links:
        print("هیچ لینکی شبیه محصول پیدا نشد.")
        return []

    print("الگوهای پرتکرار لینک محصولات:")
    for pattern, count in pattern_counts.most_common(5):
        print(f"{pattern}: {count} occurrence(s)")

    return list(set(product_like_links))  # حذف تکراری‌ها


async def fetch_product_urls(page, base_url, page_number):
    try:
        url = f"{base_url}?page={page_number}"
        print(f"Fetching products from {url}")
        await page.goto(url, wait_until="networkidle", timeout=40000)

        await page.wait_for_selector("//a[contains(@href, '/product/dkp-')]", timeout=15000)

        product_elements = await page.locator("//a[contains(@href, '/product/dkp-')]").all() #TODO
        print(f"Found {len(product_elements)} product elements on page {page_number}")

        products = []
        seen = set()
        for elem in product_elements:
            try:
                href = await elem.get_attribute('href')
                if not href or '/product/dkp-' not in href:
                    continue
                product_url = f"https://www.digikala.com{href}" if href.startswith('/') else href

                # جلوگیری از تکرار
                if product_url in seen:
                    continue
                seen.add(product_url)

                #print(f"Product URL found: {product_url}")
                products.append({'url': product_url, 'page': page_number})

            except Exception as e:
                print(f"Error processing product element: {str(e)}")

        if not products:
            print(f"No valid product URLs found on page {page_number}. HTML snippet:")
            print((await page.content())[:2000])

        return products

    except Exception as e:
        print(f"Error fetching products on page {page_number}: {str(e)}")
        return []

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Fetch product URLs from multiple pages
            base_url = "https://www.digikala.com/search/category-women-perfume/"
            max_pages = 4  # Adjust as needed
            all_products = []

            for page_num in range(1, max_pages + 1):
                #products = await fetch_product_urls(page, base_url, page_num)

                await page.goto(f"{base_url}?page={page_num}", wait_until="networkidle", timeout=40000)
                products = await guess_product_links(page)
                products = [{'url': url, 'page': page_num} for url in products]

                all_products.extend(products)

            await page.close()
            await context.close()
            await browser.close()

            if not all_products:
                print("No product URLs found across all pages.")
                return

            print(f"Found {len(all_products)} product URLs.")

            # Save to CSV
            df = pd.DataFrame(all_products)
            df.to_csv('product_urls.csv', index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to product_urls.csv. Total URLs: {len(all_products)}")

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())