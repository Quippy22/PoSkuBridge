import os
import sqlite3
from pathlib import Path

import pandas as pd

from core.config import config


def initialize_filesystem():

    # Setup the config.root folders
    folders = ["data", "database", "logs", "backups"]
    for f in folders:
        os.makedirs(config.root / f, exist_ok=True)

    # Setup 'data/' if it doesn't exist
    folders = ["inbound", "active", "export"]
    for f in folders:
        os.makedirs(config.root / "data" / f, exist_ok=True)

    # Setup the 'Master Catalog' in data/
    excel_path = config.root / "data" / "Master Catalog.xlsx"
    # Check if the file is missing
    if not os.path.exists(excel_path):
        # Prepare dataframes
        headers = ["Wharehouse Code", "Official Description", "Keywords"]
        h1 = pd.DataFrame([], columns=headers)
        h2 = pd.DataFrame([], columns=headers[:2])
        
        # Write the sheets 
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            h1.to_excel(writer, sheet_name="Core", index=True)
            h2.to_excel(writer, sheet_name="Mappings", index=True)

    print("File system initialized")

    
def sync_database():
    # Path to the database and too the xlsx file
    db_path = "database/mappings.db"
    excel_path = config.root / "data" / "Master Catalog.xlsx"

    # Read the specific sheet from Excel
    try:
        df = pd.read_excel(excel_path, sheet_name="Mappings")
        df = df.drop(columns=["Official Description"], errors="ignore")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return
    
    # Connect to the sql 
    conn = sqlite3.connect(db_path)

    #  Sync the data
    df.to_sql('mappings', conn, if_exists='replace', index=False)
    
    conn.close()
    print("Sync completed")