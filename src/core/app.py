import queue
import threading
import time
import shutil

from loguru import logger

from src.core.backup import backup
from src.core.logger import task_scope
from src.core.matcher import fuzzy_match, green_check
from src.core.pdf_parser import PdfParser
from src.core.settings import settings
from src.lib.data import prepare_review_data


class App:
    def __init__(self):
        # -- Shared Resources --
        # The file queue
        self.file_queue = queue.Queue()
        # Don't process a file twice
        self.processed_files = set()
        # Hybrid mode
        self.user_event = threading.Event()  # Stop the parser
        self.stop_event = threading.Event()  # Safely stop the app
        self.user_decision = None  # approve or skip
        self.needs_review = False

        # -- The Threads --
        # The Watcher
        threading.Thread(target=self.watcher_loop, daemon=True).start()
        # The Worker
        threading.Thread(target=self.worker_loop, daemon=True).start()
        # The Archivist
        threading.Thread(target=self.archivist_loop, daemon=True).start()

    def exit(self):
        logger.info("Stopping system!")
        self.stop_event.set()

        # If the worker is stuck waiting for a file
        try:
            self.file_queue.put(None)
        except Exception:
            pass

    @logger.catch
    def watcher_loop(self):
        """Monitors the input directory for new orders"""
        logger.info("THREAD: Watcher is active")
        while not self.stop_event.is_set():
            try:
                in_path = settings.input_dir
                files = list(in_path.glob("*.pdf"))

                for f in files:
                    if f.name not in self.processed_files:
                        logger.info(f"Found new file: {f.name}")
                        self.file_queue.put(f)

                        self.processed_files.add(f.name)
            except Exception as e:
                logger.error(f"Watcher: {e}")

            if self.stop_event.wait(timeout=2):
                break

        logger.info("Watcher: Stopped")

    @logger.catch
    def worker_loop(self):
        logger.info("THREAD: Worker is active")
        while not self.stop_event.is_set():
            mode = settings.working_mode
            if mode.lower() == "off":
                time.sleep(1)
                continue

            try:
                file_path = self.file_queue.get(timeout=1)
                if file_path is None:
                    break
            except queue.Empty:
                continue

            try:
                parser = PdfParser(file_path)
                # items format: [QTY, SKU, DESCRIPTION]
                supplier, items = parser.run()

                # Filter items
                # format: [sku, warehouse_code, flag, score]
                if supplier is None or items is None:
                    logger.warning(f"Skipping {file_path.name}: Could not parse supplier/items.")
                    continue

                match_results = fuzzy_match(po_items=items, supplier=supplier)
                print(match_results)
                print()
                # Check for all green status
                if green_check(match_results):
                    # Yes -> export the file
                    logger.info(f"Auto-exporting {file_path.name}")
                else:
                    # No -> check working mode
                    if mode.lower() == "auto":
                        # Move the file
                        shutil.move(file_path, settings.review_dir / file_path.name)
                        # Remove the file name from the set
                        self.processed_files.discard(file_path.name)
                    else:
                        logger.info(f"Requesting user review for {file_path.name}")
                        # 1. Format the data
                        stats, rows = prepare_review_data(items, match_results)

                        # 2. Statsh the data
                        self.current_review_payload = {
                            "supplier": supplier,
                            "rows": rows,
                            "stats": stats
                        }
                        self.needs_review = True

                        # 3. Clear the flag so we can wait on it
                        self.user_event.clear()
                        
                        # 4. Wait for human confirmation
                        self.user_event.wait()

                        # 5. Clean up
                        self.current_review_payload = None

                # Archive the file after it was processed
                if settings.archive_processed_files:
                    try:
                        dest = settings.archive_dir / file_path.name
                        shutil.move(file_path, dest)
                        logger.info(f"Archived {file_path.name}")

                        self.processed_files.discard(file_path.name)
                    except Exception as e:
                        logger.error(f"Failed to archive {file_path.name}: {e}")

            except Exception as e:
                logger.error(f"Worker: {e}")
        logger.info("Worker: Stopped")

    @logger.catch
    def archivist_loop(self):
        logger.info("THREAD: Archivist is active")
        while not self.stop_event.is_set():
            interval = settings.backup_interval

            # Disabled state
            if interval <= 0:
                # Wait 60 seconds to see if settings change or app stops
                self.stop_event.wait(timeout=60)
                continue

            seconds = settings.backup_interval * 3600
            # Wait for the interval or for the app to stop
            if self.stop_event.wait(timeout=seconds):
                break

            with task_scope("Scheduled Backup"):
                backup("AUTO")

        logger.info("Archivist: Stopped")
