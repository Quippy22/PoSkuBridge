import pandas as pd
from loguru import logger
<<<<<<< HEAD

from src.core.logger import task_scope
from src.core.settings import settings
=======
from pathlib import Path

from src.core.settings import settings
from src.core.logger import task_scope
>>>>>>> 16ae141 (core: add exporter)


class Exporter:
    """Handles data export to various formats (.xlsx, .xls, .csv)."""

    def __init__(self):
        self.output_dir = settings.output_dir

    def run(self, df: pd.DataFrame, filename: str):
        """
        Exports the dataframe to the configured format.
        """
        fmt = settings.export_format.lower()
<<<<<<< HEAD

        # 1. Prepare path
        export_path = self.output_dir / filename

=======
        
        # 1. Prepare path
        export_path = self.output_dir / filename
        
>>>>>>> 16ae141 (core: add exporter)
        # Ensure correct extension
        if not export_path.suffix == fmt:
            export_path = export_path.with_suffix(fmt)

        with task_scope(f"Exporting to {export_path.name}"):
            try:
                if fmt == ".csv":
                    df.to_csv(export_path, index=False)
                elif fmt in [".xlsx", ".xls"]:
                    # pandas handles both via openpyxl or xlwt/xlsxwriter
                    df.to_excel(export_path, index=False)
                else:
                    logger.error(f"Unsupported export format: {fmt}")
                    return None

                logger.info(f"File exported successfully: {export_path.name}")
                return export_path

            except Exception as e:
                logger.error(f"Export failed: {e}")
                return None
