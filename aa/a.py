from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os

def extract_specifications(url):
    try:
        # راه‌اندازی Playwright برای رندر JavaScript
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # مرورگر بدون رابط گرافیکی
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('networkidle')  # منتظر بارگذاری کامل صفحه
            html_content = page.content()  # دریافت HTML رندرشده
            browser.close()

        # پارس کردن HTML با BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # جستجوی تگ‌هایی که حاوی عبارت "مشخصات" هستند
        specifications = []
        for tag in soup.find_all(string=lambda text: text and 'مشخصات' in text):
            parent = tag.find_parent()
            if parent:
                # استخراج ویژگی‌های تگ والد (attributes)
                attributes = parent.attrs
                class_list = attributes.get('class', [])  # لیست کلاس‌ها
                tag_id = attributes.get('id', None)  # آیدی (اگر وجود داشته باشد)
                other_attributes = {k: v for k, v in attributes.items() if k not in ['class', 'id']}  # سایر ویژگی‌ها

                # افزودن اطلاعات به لیست
                specifications.append({
                    'tag': parent.name,
                    'content': parent.get_text(strip=True),
                    'class': class_list if class_list else None,
                    'id': tag_id,
                    'other_attributes': other_attributes if other_attributes else None
                })

        # اگر داده‌ای پیدا شد، آن را برگردان
        if specifications:
            return specifications
        else:
            return {"error": "هیچ تگی حاوی عبارت 'مشخصات' یافت نشد."}

    except Exception as e:
        return {"error": f"خطا در پردازش: {str(e)}"}

def save_to_json(data, filename="specifications.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return f"داده‌ها با موفقیت در فایل {filename} ذخیره شدند."
    except Exception as e:
        return f"خطا در ذخیره فایل JSON: {str(e)}"

# مثال استفاده
if __name__ == "__main__":
    url = input("لطفاً URL را وارد کنید: ")
    result = extract_specifications(url)
    save_result = save_to_json(result)
    print(save_result)