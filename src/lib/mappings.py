from loguru import logger

from src.core.logger import task_scope
from src.core.database import database as db

@logger.catch(reraise=True)
def save_mappings_batch(supplier, batch: list[dict]):
    """Saves a list of mappings to the database"""
    with task_scope(f"Saving mappings for {supplier}"):
        for mapping in batch:
            db.add_mapping(
                supplier_name=supplier,
                supplier_sku=mapping["sku"],
                warehouse_code=mapping["warehouse_code"]
            )
        logger.info(f"Added {len(batch)} new mappings")
