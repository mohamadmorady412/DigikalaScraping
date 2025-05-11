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
