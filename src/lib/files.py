import os

from loguru import logger

from src.core.settings import settings
from src.core.logger import task_scope


def setup_filesystem():
    with task_scope("Filesystem Initialization"):
        
        # 1. Setup Internal Folders
        internal = [
            settings.backup_path,
            settings.logs_path, 
        ]
        
        for f in internal:
            os.makedirs(f, exist_ok=True)
            logger.info(f"Checked internal directory: {f}")

        # 2. Setup Data Folders
        data = [
            settings.input_dir,
            settings.output_dir,
            settings.review_dir,
            settings.archive_dir,
        ]
        
        for f in data:
            os.makedirs(f, exist_ok=True)
            logger.info(f"Checked data directory: {f}")


def move_review_to_input():
    """Moves all files from Review folder back to Input."""
    import shutil
    
    review_dir = settings.review_dir
    input_dir = settings.input_dir
    
    files = list(review_dir.glob("*.pdf"))
    if not files:
        return

    with task_scope("Restoring Review Files"):
        for f in files:
            try:
                dest = input_dir / f.name
                shutil.move(f, dest)
                logger.info(f"Restored to Input: {f.name}")
            except Exception as e:
                logger.error(f"Failed to restore {f.name}: {e}")
