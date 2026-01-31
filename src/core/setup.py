import os
import sqlite3

from src.core.config import settings 
from src.core.logger import log


def initialize_filesystem():
    log.info("Started filesystem initialization")
    # Setup the internal folder
    internal = [
        settings.backup_path,
        settings.logs_path,
    ]
    for f in internal:
        os.makedirs(f, exist_ok=True)

    # Setup 'Data/' if it doesn't exist
    data = [
        settings.input_dir,
        settings.output_dir,
        settings.review_dir,
        settings.archive_dir,
    ]
    for f in data:
        os.makedirs(f, exist_ok=True)

    log.info("File system initialized")


def initialize_database():
    log.info("Started database initialization")
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    products_sql = """
    CREATE TABLE IF NOT EXISTS products (
        warehouse_code TEXT PRIMARY KEY,
        description TEXT,
        keywords TEXT
    );
    """

    mappings_sql = """
    CREATE TABLE IF NOT EXISTS mappings (
        warehouse_code TEXT,

        FOREIGN KEY(warehouse_code) REFERENCES products(warehouse_code)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """

    try:
        cursor.execute(products_sql)
        cursor.execute(mappings_sql)
        log.info("Database initialized")
    except Exception as e:
        log.error(f"Database failed, error: {e}")
    finally:
        conn.close()
