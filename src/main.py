import threading
import time

from core.app import App

from gui.application import GUI

# Development tools
from tools.po_generator import PoGenerator
from tools.wipe_data import nuke_environment


if __name__ == "__main__":
    # For testing, wipe all the files before starting
    # nuke_environment()

    backend = App()
    gui = GUI(backend)


    def test():
        """The stress test"""
        time.sleep(2)

        for i in range(10):
            # Create a fake PO
            pogen = PoGenerator()
            pogen.generate_pdf()
            pogen.print_po_table()

            time.sleep(0.5)

        print("Stress test complete")

    #threading.Thread(target=test, daemon=True).start()


    gui.mainloop()
