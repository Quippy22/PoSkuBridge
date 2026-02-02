import os
import sqlite3

from src.core.config import settings
from src.core.logger import log


def initialize_filesystem():
    log.info("Started filesystem initialization")
    # Setup the internal folder
    internal = [
        settings.backup_path,
        settings.logs_path,
    ]
    for f in internal:
        os.makedirs(f, exist_ok=True)

    # Setup 'Data/' if it doesn't exist
    data = [
        settings.input_dir,
        settings.output_dir,
        settings.review_dir,
        settings.archive_dir,
    ]
    for f in data:
        os.makedirs(f, exist_ok=True)

    log.info("File system initialized")
