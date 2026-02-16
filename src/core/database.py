import re
import sqlite3

import pandas as pd
from loguru import logger

from src.core.settings import settings


class Database:
    def __init__(self):
        self.path = settings.db_path
        self._initialize()

    def add_product(self, warehouse_code, description):
        """Adds a new item to the products list AND initializes the mapping row."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Append the products table
            cursor.execute(
                """
                INSERT INTO products (warehouse_code, description)
                VALUES (?, ?)
            """,
                (warehouse_code, description),
            )

            # Append the mappings table
            cursor.execute(
                "INSERT INTO mappings (warehouse_code) VALUES (?)", (warehouse_code,)
            )

            conn.commit()
            logger.info(f"Added product: {description}")

        except sqlite3.IntegrityError:
            logger.warning(f"Product {warehouse_code} already exists")
        except Exception as e:
            logger.error(f"Failed to add product: {e}")
        finally:
            conn.close()

    def add_mapping(self, supplier_name, supplier_sku, warehouse_code):
        """Maps a Supplier SKU to an existing Warehouse Code."""
        # Ensure column exists first
        col_name = self._ensure_supplier(supplier_name)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = f"UPDATE mappings SET {col_name} = ? WHERE warehouse_code = ?"
            cursor.execute(query, (supplier_sku, warehouse_code))

            if cursor.rowcount == 0:
                logger.error(f"Cannot map to {warehouse_code}: Product not found.")
            else:
                conn.commit()
                logger.info(
                    f"Mapped {supplier_name} [{supplier_sku}] -> {warehouse_code}"
                )

        except Exception as e:
            logger.error(f"Mapping save failed: {e}")
        finally:
            conn.close()

    def get_supplier_history(self, supplier) -> pd.DataFrame:
        """Gets known matches for this supplier."""
        col_name = self._ensure_supplier(supplier)
        conn = self._get_connection()
        try:
            # Select only valid mappings
            query = f"""
                SELECT warehouse_code, {col_name} as supplier_sku
                FROM mappings
                WHERE {col_name} IS NOT NULL
            """
            return pd.read_sql(query, conn)
        finally:
            conn.close()

    def get_products(self) -> pd.DataFrame:
        """Returns the code and description for fuzzy matching."""
        conn = self._get_connection()
        try:
            query = "SELECT warehouse_code, description FROM products"
            return pd.read_sql(query, conn)
        finally:
            conn.close()

    def get_autocomplete_data(self) -> pd.DataFrame:
        """Returns data for UI search bar."""
        conn = self._get_connection()
        try:
            query = "SELECT warehouse_code, description FROM products"
            return pd.read_sql(query, conn)
        finally:
            conn.close()

    def get_registry_data(self) -> pd.DataFrame:
        """Returns the full combined table of products and all their supplier mappings."""
        conn = self._get_connection()
        try:
            # 1. Get all products
            products_df = pd.read_sql("SELECT * FROM products", conn)

            # 2. Get all mappings
            mappings_df = pd.read_sql("SELECT * FROM mappings", conn)

            # 3. Merge them on warehouse_code
            # Since mappings has warehouse_code as PK and matches products,
            # a simple left join ensures we see all products even if they have no mappings yet
            merged_df = pd.merge(
                products_df, mappings_df, on="warehouse_code", how="left"
            )

            return merged_df
        finally:
            conn.close()

    def _ensure_supplier(self, supplier):
        """Dynamically adds a column for the supplier if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get existing columns
        cursor.execute("PRAGMA table_info(mappings)")
        existing_cols = [row["name"] for row in cursor.fetchall()]

        # Clean the supplier name before adding it
        clean_sup = supplier.lower().strip()
        clean_sup = re.sub(r"[^a-z0-9]", "", clean_sup)

        # Check against raw name
        if clean_sup not in existing_cols:
            try:
                logger.info(f"New supplier: {supplier}, adding column...")
                # Use quotes to handle spaces safely
                cursor.execute(f'ALTER TABLE mappings ADD COLUMN "{clean_sup}" TEXT')
                conn.commit()
            except Exception as e:
                logger.error(f"Failed to add supplier column: {e}")

        conn.close()
        return clean_sup

    def _get_connection(self) -> sqlite3.Connection:
        """Ensures there is always a valid connection for the current thread."""
        try:
            conn = sqlite3.connect(self.path)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise e

    def _initialize(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        products_sql = """
            CREATE TABLE IF NOT EXISTS products (
                warehouse_code TEXT PRIMARY KEY,
                description TEXT
            );
        """

        mappings_sql = """
            CREATE TABLE IF NOT EXISTS mappings (
                warehouse_code TEXT PRIMARY KEY,
                FOREIGN KEY(warehouse_code) REFERENCES products(warehouse_code)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );
        """

        cursor.execute(products_sql)
        cursor.execute(mappings_sql)
        conn.commit()
        logger.info("Database initialized")
        conn.close()


database = Database()
