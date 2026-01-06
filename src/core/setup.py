import os
import sqlite3

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
        headers = ["Warehouse Code", "Official Description", "Keywords"]
        h1 = pd.DataFrame([], columns=headers)
        h2 = pd.DataFrame([], columns=headers[:2])

        # Write the sheets
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            h1.to_excel(writer, sheet_name="Core", index=True)
            h2.to_excel(writer, sheet_name="Mappings", index=True)

    print("File system initialized")


def sync_database():
    print("Sync started")
    """
    The logic flow:
    1. Read Sheet 1 (The Source of Codes)
    2. Read Sheet 2 (The Existing Mappings)
    3. Merege them: add new codes but keep the existing mappings
    4. Database Sync: take the mappings from sheet 2 and push them to SQL
    """
    # Path to the xlsx file
    excel_path = config.root / "data" / "Master Catalog.xlsx"

    # Read the sheets from Excel
    # First sheet
    try:
        sheet1 = pd.read_excel(excel_path, sheet_name="Core")
        sheet1 = sheet1.drop(columns=["Keywords"], errors="ignore")

        # The first column might be Unnamed since index=True
        if "Unnamed" in sheet1.columns[0]:
            sheet1 = sheet1.drop(sheet1.columns[0], axis=1)
    except Exception as e:
        print(f"Error reading sheet 1(Core): {e}")

    # Second sheet
    try:
        sheet2 = pd.read_excel(excel_path, sheet_name="Mappings")
        if "Unnamed" in sheet2.columns[0]:
            sheet2 = sheet2.drop(sheet2.columns[0], axis=1)
    except Exception as e:
        print(f"Error reading sheet 2(Mappings): {e}")
        return

    # Merge the dataframes
    sheet2 = pd.merge(
        sheet1.iloc[:, [0, 1]], sheet2, on=list(sheet1.columns[:2]), how="left"
    )

    # Write the second sheet
    with pd.ExcelWriter(
        excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        sheet2.to_excel(writer, sheet_name="Mappings", index=True)

    # Sync the database
    db_path = "database/mappings.db"
    # Connect to the sql
    conn = sqlite3.connect(db_path)

    # Sync the data
    sheet2 = sheet2.drop(sheet2.columns[1], axis=1)
    sheet2.to_sql("mappings", conn, if_exists="replace", index=False)

    conn.close()
    print("Sync completed")
