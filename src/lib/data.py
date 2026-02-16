import pandas as pd


def prepare_review_data(parsed_items: pd.DataFrame, matched_items: pd.DataFrame) -> tuple[dict, list[dict]]:
    """Merges the dataframes into a list of dicts for the review rows"""
    # parsed_items has [QTY, SKU, DESCRIPTION]
    # matched_items has [sku, warehouse_code, flag, score]

    # 1. Normalize 'sku' columns for merging
    items = parsed_items[["sku", "description"]].copy().astype(str)
    items["sku"] = pd.Series(items["sku"]).astype(str).str.strip()

    matches = matched_items.copy()
    matches["sku"] = pd.Series(matches["sku"]).astype(str).str.strip()

    # 2. Merge
    merged = pd.merge(matches, items, on="sku", how="left")

    # 3. Fill mising and reorder
    merged["description"] = merged["description"].fillna("No description found")
    final = merged[["sku", "description", "warehouse_code", "flag", "score"]]

    # 4. Generate stats
    counts = pd.Series(final["flag"]).value_counts()
    stats = {
        "green": int(counts.get("green", 0)),
        "yellow": int(counts.get("yellow", 0)),
        "red": int(counts.get("red", 0))
    }

    priority = {"yellow": 0, "red": 1, "green": 2}
    rows = final.assign(p=final["flag"]
                        .map(priority))\
                        .sort_values("p")\
                        .drop(columns="p")\
                        .to_dict("records")

    return stats, rows


def prepare_registry_data(df: pd.DataFrame) -> list[dict]:
    """Converts the database dataframe into a list of dicts for the registry rows"""
    if df.empty:
        return []

    # Ensure everything is string/readable
    return df.fillna("-").to_dict("records")
