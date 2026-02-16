import re

import pandas as pd
import pdfplumber
from loguru import logger

from src.core.settings import settings
from src.core.logger import task_scope


class PdfParser:
    def __init__(self, file_path):
        self.file_path = file_path

        self.pdf = None
        self.pages = None
        self.page_width = None
        self.page_height = None

        self.supplier = "Unknown"
        self.po_table = None

    def run(self) -> tuple[str | None, pd.DataFrame | None]:
        # Open the file
        self._pdf_opener(str(self.file_path))
        if self.pdf is None:
            return None, None
        # Search for supplier
        self._obtain_supplier()
        # Get the table
        self._extract_table()
        if self.po_table is None:
            logger.error("Could not detect table")
            return self.supplier, None

        # If the table isn't empty, clean the data
        self._clean_table()

        # Return the supplier and table as a tuple
        return self.supplier, self.po_table

    def _pdf_opener(self, file_path):
        try:
            self.pdf = pdfplumber.open(file_path)
        except Exception as e:
            logger.error(f"Couldn't open file {file_path},error: {e}")
            return

        self.pages = self.pdf.pages
        self.page_height = self.pages[0].height
        self.page_width = self.pages[0].width

    def _obtain_supplier(self):
        """Looks for supplier, vendor etc at the top of the first page"""
        logger.info("Obtaining supplier")
        # look into the top 20% of the page (header)
        page = self.pages[0].crop((0, 0, self.page_width, self.page_height * 0.2))

        supplier_keys = [
            "Vendor",
            "Supplier",
            "Provider",
            "From",
            "Sold By",
            "Remit To",
            "Seller",
        ]
        text = page.extract_text()

        for key in supplier_keys:
            # Look for Key + colon (optional) + text until end of line
            # (?:...) is a non-capturing group for the colon
            # \s* handles spaces
            # (.+) captures the name
            pattern = rf"{re.escape(key)}\s*[:]?\s*(.+)"

            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.supplier = match.group(1).strip()

        # If it isn't found, remains Unknown pending human intervention

    def _extract_table(self):
        """
        Universal Extractor:
        1. Tries to find a specific Grid.
        2. If no grid, assumes whitespace structure.
        """
        logger.info("Extracting items")
        full_table = []
        for page in self.pages:
            # Remove the header
            page = self._crop_to_header(page)

            # ATTEMPT 1: LATTICE (Best for Grids/Lines)
            # This looks for physical lines separating cells.
            table = page.extract_table(
                {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 3,
                }
            )

            # Validation: Did we get a real table? (At least Header + 1 Row)
            if not table or not len(table) >= 2:
                # ATTEMPT 2: STREAM (Best for Whitespace/No Lines)
                # If the above failed (no lines found), we scan for text alignment.
                table = page.extract_table(
                    {
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "intersection_tolerance": 5,
                        "snap_tolerance": 3,
                    }
                )

            full_table.extend(table)

        if full_table:
            self.po_table = pd.DataFrame(full_table[1:], columns=full_table[0])

        # print("Uncleaned DataFrame")
        # print(self.po_table)

    def _crop_to_header(self, page):
        """
        Scans the page for header keywords and crops everything above them.
        Returns the cropped page (or original if no header found).
        """
        header_keywords = [
            "sku",
            "qty",
            "quantity",
            "description",
            "desc",
            "unit price",
            "price",
            "unit",
            "total",
            "amount",
            "item",
            "ref",
            "part number",
        ]

        # Get all words to find positions
        words = page.extract_words()

        # Sort by vertical position (top to bottom) to find the highest header
        words.sort(key=lambda w: w["top"])

        crop_y = 0
        for word in words:
            if word["text"].lower().strip() in header_keywords:
                # Found the start of the table.
                # Crop slightly above the word (minus 2 pixels)
                crop_y = max(0, word["top"] - 2)
                break

        # If we found a header, crop the page.
        # If not (crop_y is 0), return the full page (useful for Page 2 continuations).
        if crop_y > 0:
            return page.crop((0, crop_y, page.width, page.height))

    def _clean_table(self):
        if self.po_table.empty:
            return

        # 1. Standardize headers
        self.po_table.columns = (
            self.po_table.columns.astype(str)
            .str.replace(r"\n", "")
            .str.strip()
            .str.lower()
        )

        # Change duplicate headers to 'name.number'
        new_columns = []
        seen_counts = {}  # Tracks how many times we've seen a header

        for col in self.po_table.columns:
            col_name = col.strip()
            if col_name in seen_counts:
                seen_counts[col_name] += 1
                # Create unique name: "Total.1", "nan.2", ".1"
                new_col = f"{col_name}.{seen_counts[col_name]}"
            else:
                seen_counts[col_name] = 0
                new_col = col_name
            new_columns.append(new_col)

        self.po_table.columns = new_columns

        # 1.5 Normalize common names
        norm_map = {
            "quantity": "qty",
            "quantity.1": "qty",
            "item": "description",
            "desc": "description",
            "part number": "sku",
            "pn": "sku",
            "ref": "sku",
        }
        self.po_table.rename(columns=norm_map, inplace=True)

        # 2. Drop price/total
        cols_to_drop = [
            c
            for c in self.po_table.columns
            if any(x in c for x in ["price", "total", "amount", "cost"])
        ]
        self.po_table = self.po_table.drop(columns=cols_to_drop)

        def is_header_bad(col_name):
            """Returns True if the column header looks like a ghost/split artifact"""
            name = str(col_name).lower()
            return (
                name == "nan"
                or "unnamed" in name
                or name == ""
                or name == "none"
                or name.startswith(".")
            )

        # 3. Fix split data (Merge Left)
        # We iterate backwards (right to left) so we don't mess up indexes while dropping
        i = 1
        while i < len(self.po_table.columns):
            curr_col = self.po_table.columns[i]
            prev_col = self.po_table.columns[i - 1]

            if is_header_bad(curr_col):
                # Merge Data: Previous + Space + Current
                self.po_table[prev_col] = (
                    self.po_table[prev_col].astype(str).replace("nan", "")
                    + " "
                    + self.po_table[curr_col].astype(str).replace("nan", "")
                ).str.strip()

                self.po_table.drop(columns=[curr_col], inplace=True)
            else:
                i += 1

        # 4. Fix split headers (Merge Header Name Left)
        self.po_table = self.po_table.replace(r"^\s*$", pd.NA, regex=True)

        i = 1
        while i < len(self.po_table.columns):
            curr_col = self.po_table.columns[i]
            prev_col = self.po_table.columns[i - 1]

            # If column is empty (all NaNs), it's a split header artifact
            if self.po_table[curr_col].isna().all():
                new_name = str(prev_col) + str(curr_col)  # Merge Names
                self.po_table.rename(columns={prev_col: new_name}, inplace=True)
                self.po_table.drop(columns=[curr_col], inplace=True)
            else:
                i += 1

        # 5. Remove repeated headers
        if len(self.po_table.columns) > 0:
            first_col = self.po_table.columns[0]
            self.po_table = self.po_table[
                self.po_table[first_col].astype(str) != str(first_col)
            ]

        # 6. Final cleanup
        self.po_table = self.po_table.replace(r"\n", "", regex=True)
        # Fix split words (e.g. "G asket")
        self.po_table = self.po_table.replace(
            r"(?<=[a-zA-Z])\s(?=[a-z])", "", regex=True
        )
        # Drop empty columns/rows
        self.po_table = self.po_table.dropna(how="all").reset_index(drop=True)
        # Remove leading/trailing spaces from the cells
        self.po_table = self.po_table.apply(
            lambda x: x.str.strip() if x.dtype == "object" else x
        )
