import queue
import threading
from loguru import logger

from src.core.workers import Watcher, Worker, Archivist


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
        self.current_review_payload = None

        # -- The Threads --
        self.watcher = Watcher(self)
        self.worker = Worker(self)
        self.archivist = Archivist(self)

        self.watcher.start()
        self.worker.start()
        self.archivist.start()

    def exit(self):
        logger.info("Stopping system!")
        self.stop_event.set()

        # If the worker is stuck waiting for a file
        try:
            self.file_queue.put(None)
        except Exception:
            pass
        
        # Wake up the user event if stuck
        self.user_event.set()
