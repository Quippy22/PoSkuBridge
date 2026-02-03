import threading
import time

from src.core.app import App
from src.core.config import settings
from src.core.database import database as db
from src.core.logger import setup_logging
from src.gui.application import GUI

# Development tools
from src.tools.po_generator import PoGenerator
from src.tools.wipe_data import nuke_environment

if __name__ == "__main__":
    setup_logging()
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

    threading.Thread(target=test, daemon=True).start()

    def test_database_logic():
        time.sleep(2)
        print("\n--- 🧪 STARTING DATABASE TEST ---")

        # No need to use backend.db, just use 'db' directly
        print("Step 1: Creating Product...")
        db.add_product("WH-100", "Global Singleton Bolt")

        print("Step 2: Mapping New Supplier...")
        db.add_mapping("GlobalCo", "G-1", "WH-100")

        # Verify
        df = db.get_supplier_history("GlobalCo")
        if not df.empty:
            print(f"✅ SUCCESS! Found: {df.iloc[0].to_dict()}")
        else:
            print("❌ FAILURE!")

    # threading.Thread(target=test_database_logic, daemon=True).start()

    gui.mainloop()
