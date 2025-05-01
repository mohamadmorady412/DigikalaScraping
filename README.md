# DigikalaScraping
Extract whatever you like from Digikala!

# Digikala Web Scraper

This project is a web scraper designed to collect product data from the Digikala website. It extracts product links for a specified category, then gathers detailed specifications from those product pages, and finally stores the collected data in a configurable format (such as CSV or PostgreSQL).

## 🛠️ Technologies Used

* **Python 3.x**: The primary programming language.
* **Playwright**: For rendering web pages with JavaScript and interacting with them.
* **Beautiful Soup 4**: For parsing and navigating the HTML structure.
* **Requests**: For making simple HTTP requests.
* **Loguru**: For comprehensive logging.
* **PyYAML**: For reading YAML configuration files.
* **python-dotenv**: For managing environment variables from a `.env` file.
* **SQLAlchemy**: For interacting with the PostgreSQL database as an ORM (optional).
* **asyncio**: For running asynchronous operations.

## 🚀 Usage

To run this scraper, follow these steps:

1.  **Prerequisites:**
    * Ensure you have Python 3.x installed on your system.
    * Install Playwright:
        ```bash
        pip install playwright
        playwright install
        ```
    * Install other dependencies:
        ```bash
        pip install -r requirements.txt
        ```
        (if you have a `requirements.txt` file)

2.  **Configuration:**
    * Create a configuration file named `config.yaml` in the `config` directory. This file includes settings such as the base Digikala URL, the product category, the storage type selection (CSV or postgres), and settings specific to each. An example of this file could look like this:

        ```yaml
        scraper:
          category: "mobile"
          base_url_template: "[https://www.digikala.com/search/category-](https://www.digikala.com/search/category-){category}/page-{page}/"
          domain: "[https://www.digikala.com](https://www.digikala.com)"
          start_page: 1
          max_pages: 5
          sleep_duration: 1
          link_output_file: "output/mobile_links.txt"
          specs_input_file: "output/mobile_links.txt"
          storage_type: "csv" # Can be "csv" or "postgres"
          csv_output_file: "output/mobile_specs.csv"
          csv_fieldnames:
            - "نام محصول"
            - "لینک"
          spec_keys:
            - "برند"
            - "مدل"
        headers:
          User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        database:
          table_name: "mobile_products"
          # PostgreSQL connection settings in .env file
        specs_scraper:
          page_timeout: 30000 # milliseconds
          wait_state: "domcontentloaded"
          spec_div_id: "product-params" # Or the ID of the specifications div
          spec_keys:
            - "برند"
            - "حافظه داخلی"
            - "شبکه های ارتباطی"
        ```

    * If you are using PostgreSQL as the storage method, create a `.env` file in the `config` directory and include your database connection information:

        ```dotenv
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=your_database_name
        DB_USER=your_username
        DB_PASSWORD=your_password
        ```

3.  **Execution:**
    Run the scraper using the following command:
    ```bash
    python main.py
    ```

4.  **Output:**
    * If `storage_type` in `config.yaml` is set to `csv`, the collected data will be stored in a CSV file within the `output` directory.
    * If `storage_type` is set to `postgres`, the data will be stored in the specified table in your PostgreSQL database.
    * The extracted product links will also be saved to the file specified in `link_output_file`.
    * Execution logs will be saved in `logs/scraper.log`.

## 🤝 Contributing

Contributions to this project are welcome. Feel free to fork the repository and submit your changes via Pull Request.

## 📜 License

[LICENSE]C:\Users\moham\Documents\GitHub\DigikalaScraping\LICENSE

