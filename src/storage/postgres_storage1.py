import psycopg2
from core.abstractions import Storage
from core.config_loader import ConfigLoader
from loguru import logger

class PostgresStorage(Storage):
    def __init__(self, config_loader: ConfigLoader):
        self.db_config = config_loader.get_database_config()
        self.table_name = self.db_config["table_name"]
        self.fieldnames = config_loader.get_scraper_config()["csv_fieldnames"] + \
                          [key for key in config_loader.get_scraper_config()["spec_keys"]]
        self._create_table()

    def _create_table(self):
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["name"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            cursor = conn.cursor()

            columns = ["نام_محصول TEXT", "لینک TEXT"]
            for field in self.fieldnames[2:]:
                columns.append(f'"{field}" TEXT')
            columns_str = ", ".join(columns)

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                {columns_str}
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            logger.info(f"Table {self.table_name} created or verified")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def save(self, data):
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["name"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            cursor = conn.cursor()

            for item in data:
                columns = [key.replace(" ", "_") for key in item.keys()]
                placeholders = ", ".join(["%s"] * len(item))
                values = [item[key] for key in item]
                insert_query = f"""
                INSERT INTO {self.table_name} ({', '.join([f'"{col}"' for col in columns])})
                VALUES ({placeholders})
                """
                cursor.execute(insert_query, values)

            conn.commit()
            logger.info(f"Saved {len(data)} products to PostgreSQL table {self.table_name}")
        except Exception as e:
            logger.error(f"Error saving to PostgreSQL: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
