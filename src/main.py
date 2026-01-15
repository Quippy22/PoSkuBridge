import threading
import time
import queue 

from core.backup import backup
from core.config import settings
from core.logger import log
from core.pdf_parser import PdfParser
from core.setup import initialize_database, initialize_filesystem

# Development tools
from tools.po_generator import PoGenerator
from tools.wipe_data import nuke_environment


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
        self.user_decision = None  # aprove or skip

        # -- The Threads --
        # The Watcher
        threading.Thread(target=self.watcher_loop, daemon=True).start()
        # The Worker
        threading.Thread(target=self.worker_loop, daemon=True).start()
        # The Archivist
        threading.Thread(target=self.archivist_loop, daemon=True).start()
        # The Talker (untill the GUI is connected)
        threading.Thread(target=self.show_log, daemon=True).start()

    def watcher_loop(self):
        """Monitors the input direcotry for new orders"""
        self.log.info("THREAD: Watcher is active")
        while True:
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

            time.sleep(2)

    def worker_loop(self):
        self.log.info("THREAD: Worker is active")
        while True:
            mode = settings.working_mode
            if mode.lower() == "off":
                time.sleep(1)
                continue

            try:
                file_path = self.file_queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                parser = PdfParser(file_path)
                supplier, items = parser.run()

                # filter items

                # check working mode
                if mode.lower() == "auto":
                    # skip files without the all green status
                    pass
                else:
                    # wait for human confirmation
                    pass

                print(supplier)
                print(items)
                
            except Exception as e:
                log.error(f"Worker: {e}")
        

    def archivist_loop(self):
        self.log.info("THREAD: Archivist is active")
        while True:
            time.sleep(settings.backup_interval * 3600)
            backup("AUTO")

    def show_log(self):
        """Temporary log viewer"""
        while True:
            if self.log.has_messages():
                log = self.log.get_next_message()
                print(f"{log['time']} {log['level'] if log['level'] != 'INFO' else ''}: {log['msg']}")

            time.sleep(0.1)


if __name__ == "__main__":
    # For testng, wipe all the files before starting
    nuke_environment()

    app = App()
    settings.working_mode = "auto"

    try:
        print("System running. Press Ctrl+C to stop.")
        for i in range(10):
            # Create a fake PO
            pogen = PoGenerator()
            pogen.generate_pdf()
            pogen.print_po_table()
        while True:
            time.sleep(1) # Just sit here so the threads can work
    except KeyboardInterrupt:
        print("Shutting down...")

