import os
import shutil
import pathlib
from datetime import datetime

from core.config import config


def backup(tag="auto"):
    # 1. Establish the paths
    backup_path = config.root / "backups"
    excel_path = config.root / "data/Master Catalog.xlsx"
    db_path = config.root / "database/mappings.db"

    # 2. Create the folder
    # The backup folder's name is 'timestamp_tag'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
    folder_name = f"backup_{timestamp}_{tag}"

    backup_folder = backup_path / folder_name
    try:
        backup_folder.mkdir(parents=True, exist_ok=True) 

        # 3. Copy the files 
        files = [excel_path, db_path]
        for f in files:
            if f.exists:
                shutil.copy2(f, backup_folder / f.name)
                print(f"Backed up {f.name}")
        
        # Save the settings
        config.to_json(backup_folder / "settings.json")

        # Prune if necessary
        if config.max_backups is not None:
            prune_backups()

    except Exception as e:
        print(f"Backup failed: {e}")

def prune_backups():
    # 1. Get a list of all backup directories
    # Filter for folders starting with "backup_"
    backup_path = config.root / "backups"
    backups = [
        d for d in backup_path.iterdir() 
        if d.is_dir() and d.name.startswith("backup_")
    ]

    # 2. Check if the limit was exceeded
    if len(backups) > config.max_backups:
        # Sort them by creation time (Oldest first)
        backups.sort(key=lambda x: x.stat().st_ctime)

        # 3. Calculate how many folders to delete
        number_to_delete = len(backups) - config.max_backups
       
        # 4. Delete the oldest backups 
        for i in range(number_to_delete):
            oldest_folder = backups[i]
            try:
                shutil.rmtree(oldest_folder)
                print(f"Pruned old backup: {oldest_folder.name}")
            except Exception as e:
                print(f"Could not delete {oldest_folder.name}: {e}") 