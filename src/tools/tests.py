import time

from src.core.database import database as db
from src.tools.po_generator import PoGenerator


def stress_test():
    """Performs a stress test by generating 10 POs"""
    time.sleep(2)

    for _ in range(10):
        # Create a fake PO
        pogen = PoGenerator()
        pogen.generate_pdf()
        pogen.print_po_table()

        time.sleep(0.5)

    print("Stress test complete")


def database_test():
    """Adds a new item and a new mapping to the database"""
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
