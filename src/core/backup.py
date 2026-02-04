import shutil
from datetime import datetime

from loguru import logger

from src.core.settings import settings
from src.core.logger import task_scope


def backup(tag="auto"):
    with task_scope(f"Backup {tag}"):
        # 1. Setup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"backup_{timestamp}_{tag}"
        temp_folder = settings.backup_path / folder_name

        # 2. Define what to backup (Destination Name : Source Object/Path)
        # logic: if value is a Path, copy it. If it's a method (like .save), call it.
        targets = {
            "mappings.db": settings.db_path,
            "config.json": settings.save,  # passing the function to call later
            "system.log": settings.logs_path,
        }

        try:
            temp_folder.mkdir(parents=True, exist_ok=True)

            # 3. Execution Loop
            for name, source in targets.items():
                dest = temp_folder / name

                if callable(source):
                    # It's a function (like settings.to_json), so run it
                    source(dest)
                    logger.info(f"Generated {name}")
                elif hasattr(source, "exists") and source.exists():
                    # It's a file path, so copy it
                    shutil.copy2(source, dest)
                    logger.info(f"Copied {name}")

            # 4. Zip it
            shutil.make_archive(
                base_name=str(temp_folder), format="zip", root_dir=temp_folder
            )
            logger.info(f"Created archive: {folder_name}.zip")

            # 5. Cleanup (Remove the unzipped folder)
            shutil.rmtree(temp_folder)

            # Prune logic
            if settings.max_backups is not None:
                prune_backups()

            logger.info("Backup finished")
        except Exception as e:
            logger.error(f"Backup failed: {e}")


def prune_backups():
    with task_scope("Pruning Backups"):
        logger.warning("Reached maximum number of backups. Deleting oldest backups")
        # 1. Get a list of all backup directories
        # Filter for folders starting with "backup_"
        backups = []
        for d in settings.backup_path.iterdir():
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
                    logger.info(f"Pruned old backup: {oldest_folder.name}")
                except Exception as e:
                    logger.error(f"Could not delete {oldest_folder.name}: {e}")
