import datetime
import random
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from core.config import settings
from tools.catalog_generator import catalog_gen


class PoGenerator:
    def __init__(self):
        self.po_table = []

        # Calculate the PO number here,
        # It is also used as the name for the file
        self.po_num = f"PO-{random.randint(10000, 99999)}"
        self.path = settings.input_dir / self.po_num

        # Define the supplier here to make a custom SKU for each one
        self.suppliers = ["Acme Supplies", "Global Corp", "Tech Solutions"]
        self.supplier = random.choice(self.suppliers)

        # PDF page
        self.pagesize = A4
        self.width, self.height = self.pagesize

        self.y = 700
        # X Coordinates for columns
        self.col_qty = 40
        self.col_sku = 80
        self.col_desc = 160
        self.col_price = 450
        self.col_total = 520

        self.total_amount = 0.0

        # Create the canvas
        self.canvas = canvas.Canvas(str(self.path), pagesize=self.pagesize)

    def generate_pdf(self):
        # Generate the data
        self._po_table_gen()
        # Generate the pdf
        self._create_pdf_header()
        self._create_pdf_table()
        self._create_pdf_footer()
        self.canvas.save()

    def _create_pdf_header(self):
        # --- HEADER SECTION ---
        # Top Left: Company Info
        self.canvas.setFont("Helvetica-Bold", 20)
        self.canvas.drawString(50, 800, "PURCHASE ORDER")

        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(50, 775, "My Warehouse Inc.")
        self.canvas.drawString(50, 760, "123 Logistics Way")

        # Top Right: PO Details
        po_date = datetime.date.today().strftime("%Y-%m-%d")

        self.canvas.drawRightString(550, 775, f"PO #: {self.po_num}")
        self.canvas.drawRightString(550, 760, f"Date: {po_date}")
        self.canvas.drawRightString(550, 745, f"Supplier: {self.supplier}")

    def _create_pdf_table(self):
        # --- TABLE HEADERS ---
        self.canvas.setFont("Helvetica-Bold", 10)

        self.canvas.drawString(self.col_qty, self.y, "QTY")
        self.canvas.drawString(self.col_desc, self.y, "DESCRIPTION")
        self.canvas.drawString(self.col_sku, self.y, "SKU")
        self.canvas.drawString(self.col_price, self.y, "UNIT PRICE")
        self.canvas.drawString(self.col_total, self.y, "TOTAL")

        # Draw a line under headers
        self.canvas.line(40, self.y - 5, 560, self.y - 5)

        # --- TABLE ROWS ---
        self.y -= 25  # Move down
        self.canvas.setFont("Helvetica", 10)

        for item in self.po_table:
            # 1. Wrap the text
            wrapped_lines = textwrap.wrap(item["Description"], width=70)

            # 2. calculate height of this row based on how many lines we have
            # 12 points per line for size 10 font
            row_height = len(wrapped_lines) * 12

            # 3. check if we need a new page before we start drawing
            if self.y - row_height < 50:
                self.canvas.showPage()
                self.y = 800

                # --- REDRAW HEADERS ---
                self.canvas.setFont("Helvetica-Bold", 10)
                self.canvas.drawString(self.col_qty, self.y, "QTY")
                self.canvas.drawString(self.co_sku, self.y, "SKU")
                self.canvas.drawString(self.col_desc, self.y, "DESCRIPTION")
                self.canvas.drawString(self.col_price, self.y, "UNIT PRICE")
                self.canvas.drawString(self.col_total, self.y, "TOTAL")
                self.canvas.line(40, self.y - 5, 560, self.y - 5)

                # Reset for data
                self.y -= 25
                self.canvas.setFont("Helvetica", 10)

            # 4. Draw Qty, SKU, Price, Total
            self.canvas.drawString(self.col_qty, self.y, str(item["Qty"]))
            self.canvas.drawString(self.col_sku, self.y, str(item["SKU"]))
            self.canvas.drawString(self.col_price, self.y, f"${item['Price']:.2f}")
            self.canvas.drawString(self.col_total, self.y, f"${item['Total']:.2f}")

            # 5. Draw the Description. Loop through the wrapped lines
            text_y = self.y
            for line in wrapped_lines:
                self.canvas.drawString(self.col_desc, text_y, line)
                text_y -= 12  # Move down for the next line of text

            # 6. Update Stats
            self.total_amount += item["Total"]

            # 7. Move the main cursor down for the next item
            # We move down by the height of the text + some padding
            self.y -= row_height + 10

    def _create_pdf_footer(self):
        # --- FOOTER / TOTALS ---
        # Draw logic only if we aren't at the very bottom, else flip page first
        if self.y < 50:
            self.canvas.showPage()
            self.y = 800

        self.canvas.line(40, self.y + 10, 560, self.y + 10)  # Line above total
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawRightString(
            550, self.y - 10, f"GRAND TOTAL: ${self.total_amount:.2f}"
        )

    def _po_table_gen(self):
        # Generate a fake catalog and take the descriptions
        items = catalog_gen()
        descriptions = items.iloc[:, 2].tolist()  # The description

        # Shrink the list
        count = min(len(descriptions), random.randint(4, 20))
        descriptions = random.sample(descriptions, k=count)

        # Scramble them and add some random words
        descriptions = [self._scramble_text(t) for t in descriptions]

        # List of dicts with Qty | Description | Price | Total
        self.po_table = [self._po_item_gen(desc) for desc in descriptions]

    def _scramble_text(self, text):
        # Junk that suppliers add
        prefixes = ["REF:", "SKU#", "ITEM-ID:", "PN:", "VEND:", ""]
        suffixes = ["[RUSH]", "(G8)", "REV.2", "- GRADE A", "(BULK)", ""]
        separators = [" - ", " ", " / ", ": "]

        # 1. Pick a random prefix + random number
        part_num = f"{random.choice(prefixes)}{random.randint(1000, 9999)}"

        # 2. Pick a random suffix
        tag = random.choice(suffixes)

        # 3. Scramble the words in the text
        words = text.split()
        random.shuffle(words)
        text = " ".join(words)

        # 3. Assemble the messy text
        desc = f"{part_num}{random.choice(separators)}{text} {tag}"
        return desc.strip()

    def _po_item_gen(self, desc):
        qty = random.randint(1, 55)
        sku = f"{''.join([word[0] for word in self.supplier.split()[:2]])}-{random.randint(1, 100):03}"
        price = round(random.uniform(2.00, 200.00), 2)
        total = qty * price

        po_item = {
            "Qty": qty,
            "SKU": sku,
            "Description": desc,
            "Price": price,
            "Total": total,
        }

        return po_item

    def print_po_table(self):
        print(
            f"{'QTY':<5} | {'SKU':<15} | {'DESCRIPTION':<50} | {'PRICE':<10} | {'TOTAL':<10}"
        )
        print("-" * 85)  # A line to separate header from data

        for item in self.po_table:
            print(
                f"{item['Qty']:<5} | "
                f"{item['SKU']:<15} | "
                f"{item['Description']:<50} | "
                f"${item['Price']:<9.2f} | "
                f"${item['Total']:<9.2f}"
            )
