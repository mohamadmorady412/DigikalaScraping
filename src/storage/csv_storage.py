import csv
from core.abstractions import Storage
from core.config_loader import ConfigLoader
from loguru import logger

class CSVStorage(Storage):
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader.get_scraper_config()
        self.output_csv = self.config["output_csv"].format(category=self.config["category"])
        self.fieldnames = self.config["csv_fieldnames"] + [key for key in self.config["spec_keys"]]

    def save(self, data):
        with open(self.output_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        logger.info(f"Saved {len(data)} products to {self.output_csv}")
