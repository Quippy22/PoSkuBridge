import os
import shutil
from pathlib import Path


def nuke_environment():
    confirm = input("This will delete all data and databases. Are you sure? (y/n): ")
    if confirm.lower() != "y":
        print("Nuke aborted.")
        return

    # Define paths to destroy
    targets = [
        "data/inbound",
        "data/active",
        "data/export",
        "data/Master Catalog.xlsx",
        "data",
        "database",
        "backups",
        "logs",
    ]

    print("⚠️  Starting Environment Nuke...")

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
