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

    # Setup 'data/' if isnt there
    folders = ["inbound", "active", "export"]
    for f in folders:
        os.makedirs(root / "data" / f, exist_ok=True)

    # Setup the 'Master Catalog' in data/
    excel_path = root / "data" / "Master Catalog.xlsx"
    # Check if the file is missing
    if not os.path.exists(excel_path):
        headers = ["Wharehouse Code", "Official Description", "Keywords"]
        h = pd.DataFrame([], columns=headers)
        h.to_excel(excel_path, index=True)

    print("File system initialized")


def initialize_database():
    pass
