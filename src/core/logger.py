import queue
from contextlib import contextmanager

from loguru import logger

from src.core.settings import settings

# The queue for the GUI to read from
log_queue = queue.Queue()
_current_task = "Ready"


def indent_patcher(record):
    """Checks if 'indent' is set. If True adds '> ' to the message"""
    if record["extra"].get("indent"):
        record["message"] = f"> {record['message']}"


def gui_sink(message):
    """Formats the log packet for the GUI"""
    record = message.record

    if record["extra"].get("visual") is False:
        return

    log_packet = {
        "time": record["time"].strftime("%H:%M:%S"),
        "level": record["level"].name,
        "msg": record["message"],
    }

    log_queue.put(log_packet)


def file_formatter(record):
    """Custom formatter for the log message in the file"""
    lvl = record["level"].name.lower()
    lvl_padded = f"{lvl: ^8}"
    return "{time:YYYY-MM-DD HH:mm:ss} | " + lvl_padded + " | {message}\n"


def setup_logging():
    logger.remove()

    # Apply the patcher
    logger.configure(patcher=indent_patcher)

    # 1. File logger
    log_dir = settings.logs_path
    file_name = log_dir / "{time:YYYY-MM-DD_HH-mm-ss}.log"
    logger.add(
        str(file_name),
        format=file_formatter,
        rotation="10 MB",
        retention="1 week",
        level="DEBUG",
        enqueue=True,
    )

    # 2. UI logger
    logger.add(gui_sink, level="INFO", enqueue=True)


# Gui helper
def get_next_log():
    try:
        return log_queue.get_nowait()
    except queue.Empty:
        return None


def get_current_task():
    return _current_task


@contextmanager
def task_scope(task_name):
    """
    Creates a visual "chunk" in the logs.
    All logs inside the scope will be indented.
    """
    global _current_task
    old_task = _current_task
    _current_task = task_name

    logger.info(f"Task started: {task_name}")

    # contextualize
    with logger.contextualize(indent=True):
        try:
            yield
        finally:
            _current_task = old_task

    logger.info(f"Task completed: {task_name}")
