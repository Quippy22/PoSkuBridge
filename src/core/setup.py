import os
from pathlib import Path

import pandas as pd


def initialize_filesystem():
    # Path for this file
    current_file = Path(__file__).resolve()

    # src/core/setup.py -> src/core/ -> src/ -> root
    root = current_file.parent.parent.parent

    # Setup the root folders
    folders = ["data", "database", "logs", "backups"]
    for f in folders:
        os.makedirs(root / f, exist_ok=True)

    # Setup 'data/' if it doesn't exist
    folders = ["inbound", "active", "export"]
    for f in folders:
        os.makedirs(root / "data" / f, exist_ok=True)

    # Setup the 'Master Catalog' in data/
    excel_path = root / "data" / "Master Catalog.xlsx"
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

    
