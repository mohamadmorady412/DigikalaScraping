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