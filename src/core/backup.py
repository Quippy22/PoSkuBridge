import shutil
from datetime import datetime

from core.config import settings


def backup(tag="auto"):
    # 1. Setup Paths
    backup_root = settings.root / "Backups"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"backup_{timestamp}_{tag}"
    temp_folder = backup_root / folder_name

    # 2. Define what to backup (Destination Name : Source Object/Path)
    # logic: if value is a Path, copy it. If it's a method (like to_json), call it.
    targets = {
        "mappings.db": settings.root / "Database/mappings.db",
        # "settings.json": settings.to_json,  # passing the function to call later
        # "system.log": settings.root / "Logs/system.log" # Easy to add later
    }

    try:
        temp_folder.mkdir(parents=True, exist_ok=True)

        # 3. Execution Loop
        for name, source in targets.items():
            dest = temp_folder / name

            if callable(source):
                # It's a function (like settings.to_json), so run it
                source(dest)
                print(f"Generated {name}")
            elif hasattr(source, "exists") and source.exists():
                # It's a file path, so copy it
                shutil.copy2(source, dest)
                print(f"Copied {name}")

        # 4. Zip it
        shutil.make_archive(
            base_name=str(temp_folder), format="zip", root_dir=temp_folder
        )
        print(f"✅ Created archive: {folder_name}.zip")

        # 5. Cleanup (Remove the unzipped folder)
        shutil.rmtree(temp_folder)

        # Prune logic (unchanged)
        if settings.max_backups is not None:
            prune_backups()

    except Exception as e:
        print(f"❌ Backup failed: {e}")


def prune_backups():
    # 1. Get a list of all backup directories
    # Filter for folders starting with "backup_"
    backup_path = settings.root / "backups"
    backups = []
    for d in backup_path.iterdir():
        if d.is_dir() and d.name.startswith("backup_"):
            backups.append(d)

    # 2. Check if the limit was exceeded
    if len(backups) > settings.max_backups:
        # Sort them by creation time (Oldest first)
        backups.sort(key=lambda x: x.stat().st_ctime)

        # 3. Calculate how many folders to delete
        number_to_delete = len(backups) - settings.max_backups

        # 4. Delete the oldest backups
        for i in range(number_to_delete):
            oldest_folder = backups[i]
            try:
                shutil.rmtree(oldest_folder)
                print(f"Pruned old backup: {oldest_folder.name}")
            except Exception as e:
                print(f"Could not delete {oldest_folder.name}: {e}")
