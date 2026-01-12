import os
import sqlite3

from core import settings


def initialize_filesystem():
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

    print("File system initialized")


def initialize_database():
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
        print(f"Database initialized at: {settings.db_path}")
    except Exception as e:
        print(f"Database failed, error: {e}")
    finally:
        conn.close()
