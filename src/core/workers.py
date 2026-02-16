import queue
import shutil
import threading
import time
from typing import Any 

from loguru import logger

from src.core.backup import backup
from src.core.logger import task_scope
from src.core.matcher import fuzzy_match, green_check
from src.core.pdf_parser import PdfParser
from src.core.settings import settings
from src.lib.data import prepare_review_data


class BasicThread(threading.Thread):
    def __init__(self, app: Any, name: str):
        super().__init__(daemon=True, name=name)
        self.app = app
        self.stop_event = app.stop_event

    def run(self):
        logger.info(f"THREAD: {self.name} is active")
        while not self.stop_event.is_set():
            try:
                self.cycle()
            except Exception as e:
                logger.error(f"{self.name} error: {e}")
                # Prevent tight loop on error
                time.sleep(.2)
        logger.info(f"{self.name}: Stopped")

    def cycle(self):
        raise NotImplementedError


class Watcher(BasicThread):
    """Monitors the input directory for new orders"""

    def __init__(self, app):
        super().__init__(app, "Watcher")

    def cycle(self):
        with task_scope("Scanning for files"):
            try:
                in_path = settings.input_dir
                files = list(in_path.glob("*.pdf"))

                for f in files:
                    if f.name not in self.app.processed_files:
                        logger.info(f"Found new file: {f.name}")
                        self.app.file_queue.put(f)
                        # Don't process a file twice
                        self.app.processed_files.add(f.name)
            except Exception as e:
                logger.error(f"Watcher: {e}")

        if self.stop_event.wait(timeout=2):
            return


class Archivist(BasicThread):
    def __init__(self, app):
        super().__init__(app, "Archivist")

    def cycle(self):
        interval = settings.backup_interval

        # Disabled state
        if interval <= 0:
            # Wait 60 seconds to see if settings change or app stops
            self.stop_event.wait(timeout=60)
            return

        seconds = settings.backup_interval * 3600
        # Wait for the interval or for the app to stop
        if self.stop_event.wait(timeout=seconds):
            return

        with task_scope("Scheduled Backup"):
            backup("AUTO")


class Worker(BasicThread):
    def __init__(self, app):
        super().__init__(app, "Worker")

    def cycle(self):
        mode = settings.working_mode
        if mode.lower() == "off":
            time.sleep(1)
            return

        try:
            # If the worker is stuck waiting for a file
            file_path = self.app.file_queue.get(timeout=1)
            if file_path is None:
                return
        except queue.Empty:
            return

        self.process_file(file_path, mode)

    def process_file(self, file_path, mode):
        with task_scope(f"Parsing {file_path.name}"):
            try:
                parser = PdfParser(file_path)
                # items format: [QTY, SKU, DESCRIPTION]
                supplier, items = parser.run()

                # Filter items
                # format: [sku, warehouse_code, flag, score]
                if supplier is None or items is None:
                    logger.warning(
                        f"Skipping {file_path.name}: Could not parse supplier/items."
                    )
                    return

                match_results = fuzzy_match(po_items=items, supplier=supplier)

                # Check for all green status
                if green_check(match_results):
                    self.handle_green(file_path, supplier, match_results)
                else:
                    self.handle_review(file_path, supplier, items, match_results, mode)

            except Exception as e:
                logger.error(f"Worker failed processing {file_path.name}: {e}")

    def handle_green(self, file_path, supplier, match_results):
        with task_scope(f"Archiving {file_path.name}"):
            # Yes -> export the file
            logger.info(f"Auto-exporting {file_path.name}")

            # Archive the file after it was processed
            if settings.archive_processed_files:
                try:
                    dest = settings.archive_dir / file_path.name
                    shutil.move(file_path, dest)
                    logger.info(f"Archived {file_path.name}")

                    self.app.processed_files.discard(file_path.name)
                except Exception as e:
                    logger.error(f"Failed to archive {file_path.name}: {e}")

    def handle_review(self, file_path, supplier, items, match_results, mode):
        with task_scope(f"Requesting Review: {file_path.name}"):
            # No -> check working mode
            if mode.lower() == "auto":
                # Move the file
                shutil.move(file_path, settings.review_dir / file_path.name)
                # Remove the file name from the set
                self.app.processed_files.discard(file_path.name)
            else:
                logger.info(f"Requesting user review for {file_path.name}")

                # 1. Move to Review folder
                review_path = settings.review_dir / file_path.name
                try:
                    shutil.move(file_path, review_path)
                except Exception as e:
                    logger.error(f"Failed to move file to review: {e}")
                    return

                # 2. Format the data
                stats, rows = prepare_review_data(items, match_results)

                # 3. Stash the data in the App
                self.app.current_review_payload = {
                    "supplier": supplier,
                    "rows": rows,
                    "stats": stats,
                }
                self.app.needs_review = True

                # 4. Clear the flag so we can wait on it
                self.app.user_event.clear()

                # 5. Wait for human confirmation
                self.app.user_event.wait()

                # 6. Clean up
                self.app.current_review_payload = None
                self.app.needs_review = False

                # 7. Move back to Input
                input_path = settings.input_dir / file_path.name
                try:
                    shutil.move(review_path, input_path)
                    logger.info(f"Moved {file_path.name} back to Input for re-processing")
                except Exception as e:
                    logger.error(f"Failed to move file back to Input: {e}")

                # 8. Allow re-processing
                self.app.processed_files.discard(file_path.name)
