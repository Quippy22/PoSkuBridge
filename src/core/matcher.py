import pandas as pd
from rapidfuzz import fuzz, process

from src.core.settings import settings
from src.core.database import database as db


def fuzzy_match(po_items: pd.DataFrame, supplier: str):
    """
    Creates a DataFrame mapping PDF items to internal codes.

    Returns:
        New DF with columns: ['sku', 'warehouse_code', 'flag', 'score']
    """
    # 1. Requests
    # Get the available SKU's for the supplier
    available_mappings = db.get_supplier_history(supplier)

    # Get the available product codes
    all_products = db.get_products()

    # 2. Declarations
    # History map (green): key = sku, value = warehouse_code
    history_map = dict(
        zip(available_mappings.iloc[:, 1], available_mappings.iloc[:, 0])
    )

    # Product map (yellow): key = description, value = warehouse_code
    product_map = dict(zip(all_products.iloc[:, 1], all_products.iloc[:, 0]))

    valid_descriptions = list(product_map.keys())

    results = []

    # 3. Parsing
    for index, row in po_items.iterrows():
        # Clean inputs
        pdf_sku = str(row["SKU"]).strip()
        pdf_desc = str(row["DESCRIPTION"]).strip()

        # Check history for perfect matches
        if pdf_sku in history_map:
            results.append(
                {
                    "sku": pdf_sku,
                    "warehouse_code": history_map[pdf_sku],
                    "flag": "green",
                    "score": 100,
                }
            )
            # Found it, moving on
            continue

        match = process.extractOne(
            pdf_desc, valid_descriptions, scorer=fuzz.token_sort_ratio
        )

        # match returns: (best_string, score, index)
        if match:
            best_desc, score, _ = match

            if score >= settings.fuzzy_threshold:
                results.append(
                    {
                        "sku": pdf_sku,
                        "warehouse_code": product_map[best_desc],
                        "flag": "yellow",
                        "score": int(score),
                    }
                )
            # Found it, moving on
            continue

        # We didn't get a match/it wasn't good enough
        results.append(
            {
                "sku": pdf_sku,
                "warehouse_code": None,
                "flag": "red",
                "score": 0,
            }
        )

    # 4. Return
    return pd.DataFrame(results)
