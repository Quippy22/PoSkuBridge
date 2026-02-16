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
        # pogen.print_po_table()

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

def matcher_test():
    # List format: (Supplier, Vendor SKU, Description, Internal Code)
    data = [
        # --- ACME SUPPLIES ---
        ("Acme Supplies", "AS-090", "VEND:8478 / Sensor Synthetic 1/2-inch", "WH-A001"),
        ("Acme Supplies", "AS-086", "REF:6833 - Hydraulic Filter 220V (G8)", "WH-A002"),
        ("Acme Supplies", "AS-065", "ITEM-ID:9230 Pneumatic Coupling 50lb (G8)", "WH-A003"),
        ("Acme Supplies", "AS-008", "VEND:2030 Gear Hydraulic 10k-psi - GRADE A", "WH-A004"),
        ("Acme Supplies", "AS-014", "PN:2925 Bracket Heat-Resistant 18-gauge", "WH-A005"),
        ("Acme Supplies", "AS-097", "VEND:2618 - Polished M8 Bolt REV.2", "WH-A006"),
        ("Acme Supplies", "AS-085", "VEND:6740 Piston Anodized 5-inch - GRADE A", "WH-A007"),
        ("Acme Supplies", "AS-007", "VEND:7968 / Heavy- Duty 40mm Valve REV.2", "WH-A008"),
        ("Acme Supplies", "AS-002", "8092 - Polished 50lb Sensor", "WH-A009"),
        ("Acme Supplies", "AS-077", "VEND:9741 - Industrial 0.5-hp Gasket (G8)", "WH-A010"),

        # --- GLOBAL CORP ---
        ("Global Corp", "GC-098", "SKU#2751 - Connector 220V Magnetic REV.2", "WH-G001"),
        ("Global Corp", "GC-069", "REF:2996: 5-inch Bushing Industrial (G8)", "WH-G002"),
        ("Global Corp", "GC-026", "PN:2478 Synthetic 40mm Pipe", "WH-G003"),
        ("Global Corp", "GC-004", "VEND:3829 / Bolt Galvanized 0.5-hp (BULK)", "WH-G004"),
        ("Global Corp", "GC-041", "ITEM-ID:8497 - Pneumatic 10mm Fitting (G8)", "WH-G005"),
        ("Global Corp", "GC-047", "ITEM-ID:9133: Spring 75mm Galvanized [RUSH]", "WH-G006"),
    ]

    print(f"Adding {len(data)} items...")

    for supplier, sku, desc, internal_code in data:
        # 1. Create the Product internally
        db.add_product(internal_code, desc)
        
        # 2. Map the Vendor SKU to that Product
        db.add_mapping(supplier, sku, internal_code)
        
        print(f"Added: {sku} -> {internal_code}")

    print("Done.")

def registry_stress_test():
    """Populates the database with a large amount of data for UI testing."""
    from faker import Faker
    fake = Faker()
    
    print("\n--- 🧪 STARTING REGISTRY STRESS TEST ---")
    
    suppliers = ["Logitech", "Razer", "Dell", "HP", "Apple", "Samsung", "Asus", "MSI", "Corsair", "SteelSeries"]
    
    # Add 500 products
    count = 500
    print(f"Generating {count} products and mappings for {len(suppliers)} suppliers...")
    
    for i in range(1, count + 1):
        wcd = f"WCD-{i:04d}"
        desc = f"{fake.color_name()} {fake.catch_phrase()}"
        
        db.add_product(wcd, desc)
        
        # Add mappings for random suppliers
        for supplier in suppliers:
            # 70% chance to have a mapping for this supplier
            if fake.boolean(chance_of_getting_true=70):
                sku = f"{supplier[:3].upper()}-{fake.bothify(text='??-###-##')}"
                db.add_mapping(supplier, sku, wcd)
        
        if i % 50 == 0:
            print(f"Processed {i}/{count} items...")

    print("✅ Registry stress test complete")
