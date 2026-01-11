import os
import sqlite3

from core import settings


def initialize_filesystem():
    # Setup the settings.root folders
    folders = ["Data", "Database", "Logs", "Backups"]
    for f in folders:
        os.makedirs(settings.root / f, exist_ok=True)

    # Setup 'Data/' if it doesn't exist
    folders = ["Input", "Review", "Output", "Archive"]
    for f in folders:
        os.makedirs(settings.root / "Data" / f, exist_ok=True)

    print("File system initialized")


def initialize_database():
    db_path = settings.root / "Database" / "mappings.db"

    conn = sqlite3.connect(db_path)
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
        print(f"Database initialized at: {db_path}")
    except Exception as e:
        print(f"Database failed, error: {e}")
    finally:
        conn.close()
