import queue
from datetime import datetime
from queue import Queue


class AppLogger:
    def __init__(self):
        self._queue = Queue()

    def _add(self, level, message):
        """Internal helper to compose the packet with time and level"""
        now = datetime.now().strftime("[%H:%M:%S]")

        log_packet = {
            "time": now,
            "level": level,
            "msg": message,
        }

        self._queue.put(log_packet)

    def info(self, message):
        self._add("INFO", message)

    def warning(self, message):
        self._add("WARNING", message)

    def error(self, message):
        self._add("ERROR", message)

    def has_messages(self):
        return not self._queue.empty()

    def get_next_message(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None


log = AppLogger()
