import os
import shutil
from pathlib import Path

from src.core.settings import settings


def nuke_environment():
    # Define paths to destroy
    targets = [
        settings.backup_path,
        settings.logs_path,
        settings.db_path,
        settings.config_path,
        settings.internal_dir,
        settings.input_dir,
        settings.output_dir,
        settings.archive_dir,
        settings.review_dir,
        settings.root / "Data",
    ]

    print("⚠️  Starting Environment Nuke...")
    for t in targets:
        print(f"{t} \n")

    confirm = input("This will delete all data and databases. Are you sure? (y/n): ")
    if confirm.lower() != "y":
        print("Nuke aborted.")
        return

    for target in targets:
        path = Path(target)
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"[-] Deleted Directory: {target}")
                else:
                    os.remove(path)
                    print(f"[-] Deleted File: {target}")
            except Exception as e:
                print(f"[!] Error deleting {target}: {e}")
        else:
            print(f"[ ] {target} does not exist. Skipping.")

    print("\n✅ Environment wiped. Run your setup script to rebuild.")
