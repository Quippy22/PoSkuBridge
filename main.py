import threading

from src.core.app import App
from src.core.database import database as db
from src.core.logger import setup_logging
from src.core.settings import settings
from src.gui.application import GUI
from src.lib.files import setup_filesystem

# Development tools
from src.tools.po_generator import PoGenerator
from src.tools.tests import database_test, stress_test, matcher_test
from src.tools.wipe_data import nuke_environment

if __name__ == "__main__":
    # -- Infrastructure Setup --
    setup_filesystem()
    setup_logging()
    # For testing, wipe all the files before starting
    # nuke_environment()

    backend = App()
    gui = GUI(backend)

    # The stress test
    threading.Thread(target=stress_test, daemon=True).start()

    # The database test
    # threading.Thread(target=database_test, daemon=True).start()

    # Populate db for the matcher test
    #threading.Thread(target=matcher_test, daemon=True).start()

    gui.mainloop()
