from src.core.app import App
from src.core.logger import setup_logging
from src.gui.application import GUI
from src.lib.files import setup_filesystem

if __name__ == "__main__":
    # -- Infrastructure Setup --
    setup_filesystem()
    setup_logging()

    backend = App()
    gui = GUI(backend)
    gui.mainloop()
