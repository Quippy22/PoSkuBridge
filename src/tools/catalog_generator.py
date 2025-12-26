"""
Logic:
populates the 'Master Catalog' with data
creates warehouse codes: 'prefix-number-suffix'
descriptions with adjective noun size and then adds then saves them as key words

Roadmap:
1. Define the Data Pool: Create the Python lists containing the building blocks.
2. Generate a unique Warehouse_Code (Prefix-Number-Suffix).
3. Construct the Official_Description by randomly sampling the adjective, size, and noun lists.
4. Create a Keywords string (lowercase, comma-separated version of the description).
5. DataFrame Assembly: Store these entries in a list of dictionaries.
5. File Export: Save the final product to data/Master_Catalog.xlsx using the openpyxl engine.
"""

import os
import random

import pandas as pd

from core import config


def wh_code_gen():
    """Creates the warehouse code 'prefix-number-suffix'"""
    prefixes = ["WH", "ST", "EL", "ME", "CH"]
    suffixes = ["L", "S", "B", "PK", "IND", "PRO", "ECO", "X", "HD", "LT"]

    prefix = random.choice(prefixes)
    number = random.randint(1, 999)
    suffix = random.choice(suffixes)
    return f"{prefix}-{number:03d}-{suffix}"

def item_data_gen():
    """Creates the item description and keywords"""
    adjectives = [
        "Galvanized", "Stainless", "Insulated", "Heavy-Duty", "Reinforced",
        "Precision", "Industrial", "Flexible", "Corrugated", "Heat-Resistant",
        "Synthetic", "Polished", "Rubberized", "Anodized", "Compressed",
        "Modular", "Magnetic", "Hydraulic", "Pneumatic", "Coated"
    ]
    nouns = [
        "Bolt", "Pipe", "Valve", "Switch", "Coupling", 
        "Gasket", "Flange", "Bracket", "Washer", "Fitting", 
        "Piston", "Bearing", "Seal", "Connector", "Filter", 
        "Pump", "Sensor", "Gear", "Bushing", "Spring"
    ]
    sizes = [
        "10mm", "5-inch", "12-gauge", "240V", "1/2-inch", 
        "3-meter", "50lb", "20-amp", "M8", "15psi", 
        "110V", "2-inch", "40mm", "6-foot", "0.5-hp", 
        "10k-psi", "18-gauge", "1/4-NPT", "220V", "75mm"
    ]

    words = [
        random.choice(adjectives),
        random.choice(sizes),
        random.choice(nouns),
    ]

    description = " ".join(words)
    keywords = ", ".join([p.lower() for p in words])
    
    return description, keywords

def catalog_gen():
    print("Populating the Master Catalog")
    # Store the used warehouse codes, they can't repeat
    used_codes = []
    # List of dicts
    rows = []

    excel_path = config.root / "data/Master Catalog.xlsx" 
    # Import the headers
    catalog = pd.read_excel(excel_path)
    # The first row is 'Unnamed' because index=True
    # Drop it
    catalog = catalog.drop(catalog.columns[0], axis=1) 

    for i in range(random.randint(100, 900)):
        code = wh_code_gen()
        # Generate codes untill a new one is found
        while code in used_codes:
            code = wh_code_gen()
        used_codes.append(code)

        desc, keys = item_data_gen()

        row = {
            catalog.columns[0] : code,
            catalog.columns[1]: desc,
            catalog.columns[2]: keys,
        }

        rows.append(row)
    
    # Put the fake data in a dataframe
    fake_data = pd.DataFrame(rows) 
    # Add the fake data to the catalog
    catalog = pd.concat([catalog, fake_data], ignore_index=True)
    print(catalog)

    # Save
    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            catalog.to_excel(writer, sheet_name="Core", index=True)