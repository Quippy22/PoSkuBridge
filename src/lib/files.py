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
