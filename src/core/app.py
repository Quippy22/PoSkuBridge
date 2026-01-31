import queue
import threading
import time

from src.core.backup import backup
from src.core.config import settings
from src.core.logger import log
from src.core.pdf_parser import PdfParser
from src.core.setup import initialize_database, initialize_filesystem


class App:
    def __init__(self):
        # -- Infrastructure Setup --
        initialize_filesystem()
        initialize_database()

        # -- Shared Resources --
        self.log = log
        # The file queue
        self.file_queue = queue.Queue()
        # Don't process a file twice
        self.processed_files = set()
        # Hybrid mode
        self.user_event = threading.Event()  # Stop the parser
        self.stop_event = threading.Event()  # Safely stop the app
        self.user_decision = None  # approve or skip

        # -- The Threads --
        # The Watcher
        threading.Thread(target=self.watcher_loop, daemon=True).start()
        # The Worker
        threading.Thread(target=self.worker_loop, daemon=True).start()
        # The Archivist
        threading.Thread(target=self.archivist_loop, daemon=True).start()

    def exit(self):
        self.log.info("Stopping system!")
        self.stop_event.set()

        # If the worker is stuck waiting for a file
        try:
            self.file_queue.put(None)
        except Exception:
            pass

    def watcher_loop(self):
        """Monitors the input directory for new orders"""
        self.log.info("THREAD: Watcher is active")
        while not self.stop_event.is_set():
            try:
                in_path = settings.input_dir
                files = list(in_path.glob("*.pdf"))

                for f in files:
                    if f.name not in self.processed_files:
                        self.log.info(f"Found new file: {f.name}")
                        self.file_queue.put(f)

                        self.processed_files.add(f.name)
            except Exception as e:
                self.log.error(f"Watcher: {e}")

            if self.stop_event.wait(timeout=2):
                break

        self.log.info("Watcher: Stopped")

    def worker_loop(self):
        self.log.info("THREAD: Worker is active")
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
                supplier, items = parser.run()

                # Filter items

                # Check working mode
                if mode.lower() == "auto":
                    # Skip files without the all green status
                    # Remove the file name from the set
                    pass
                else:
                    # Wait for human confirmation
                    pass

                print(supplier)
                print(items)

            except Exception as e:
                log.error(f"Worker: {e}")

        self.log.info("Worker: Stopped")

    def archivist_loop(self):
        self.log.info("THREAD: Archivist is active")
        while not self.stop_event.is_set():
            if self.stop_event.wait(timeout=settings.backup_interval * 3600):
                break
            backup("AUTO")

        self.log.info("Archivist: Stopped")
