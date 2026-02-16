from tkinter import messagebox

import ttkbootstrap as ttk

from src.core.database import database as db


class AddCodeRow(ttk.Frame):
    """A row for mapping a vendor to a SKU when adding a new product."""

    def __init__(self, parent, suppliers, on_remove):
        super().__init__(parent)
        self.on_remove = on_remove

        # Vendor Dropdown
        self.vendor_var = ttk.StringVar()
        self.vendor_combo = ttk.Combobox(
            self,
            textvariable=self.vendor_var,
            values=suppliers,
            state="readonly",
            width=20,
        )
        self.vendor_combo.pack(side="left", padx=(0, 10), pady=5)

        # SKU Entry
        self.sku_var = ttk.StringVar()
        self.sku_entry = ttk.Entry(self, textvariable=self.sku_var, width=30)
        self.sku_entry.pack(side="left", padx=(0, 10), pady=5)

        # Remove Button
        ttk.Button(
            self,
            text="×",
            bootstyle="danger-outline",
            width=3,
            command=self.destroy_row,
        ).pack(side="left", pady=5)

    def destroy_row(self):
        self.on_remove(self)
        self.destroy()

    def get_data(self):
        return self.vendor_var.get(), self.sku_var.get()


class AddCode(ttk.Frame):
    """Tab for adding new products and their supplier mappings."""

    def __init__(self, parent, on_save_success, on_close):
        super().__init__(parent, padding=20)
        self.on_save_success = on_save_success
        self.on_close = on_close
        self.mapping_rows = []

        # Get existing suppliers
        self.suppliers = self._get_suppliers()

        self._setup_ui()

    def _get_suppliers(self):
        """Extracts supplier names from database mappings table."""
        try:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(mappings)")
            cols = [row["name"] for row in cursor.fetchall()]
            conn.close()
            return [c for c in cols if c != "warehouse_code"]
        except:
            return []

    def _setup_ui(self):
        # 1. Product Info
        info_frame = ttk.Labelframe(self, text="Product Information", padding=15)
        info_frame.pack(side="top", fill="x", pady=(0, 20))

        ttk.Label(info_frame, text="Warehouse Code:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.code_var = ttk.StringVar()
        ttk.Entry(info_frame, textvariable=self.code_var, width=40).grid(
            row=0, column=1, sticky="w", padx=10
        )

        ttk.Label(info_frame, text="Description:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.desc_var = ttk.StringVar()
        ttk.Entry(info_frame, textvariable=self.desc_var, width=60).grid(
            row=1, column=1, sticky="w", padx=10
        )

        # 2. Mappings List
        map_frame = ttk.Labelframe(self, text="Supplier Mappings", padding=15)
        map_frame.pack(side="top", fill="both", expand=True)

        self.rows_container = ttk.Frame(map_frame)
        self.rows_container.pack(side="top", fill="x")

        # Plus button
        ttk.Button(
            map_frame,
            text="+ Add Mapping",
            bootstyle="secondary-outline",
            command=self.add_mapping_row,
        ).pack(side="top", anchor="w", pady=10)

        # 3. Actions
        action_frame = ttk.Frame(self)
        action_frame.pack(side="bottom", fill="x", pady=20)

        # Save Button (Right)
        ttk.Button(
            action_frame,
            text="Save Product",
            bootstyle="success",
            width=20,
            command=self.save_product,
        ).pack(side="right")

        # Close Button (Next to Save)
        ttk.Button(
            action_frame,
            text="Close",
            bootstyle="secondary-outline",
            width=10,
            command=self.on_close,
        ).pack(side="right", padx=10)

    def add_mapping_row(self):
        row = AddCodeRow(self.rows_container, self.suppliers, self.remove_mapping_row)
        row.pack(side="top", fill="x")
        self.mapping_rows.append(row)

    def remove_mapping_row(self, row):
        if row in self.mapping_rows:
            self.mapping_rows.remove(row)

    def save_product(self):
        """Saves product and mappings with validation"""
        code = self.code_var.get().strip()
        desc = self.desc_var.get().strip()

        if not code or not desc:
            messagebox.showwarning("Validation Error", "Code and Description are required.")
            return

        # 1. Add Product
        if not db.add_product(code, desc):
            messagebox.showerror("Error", f"Could not add product {code}. It might already exist.")
            return

        # 2. Add Mappings
        failed_mappings = []
        for row in self.mapping_rows:
            vendor, sku = row.get_data()
            if vendor and sku:
                if not db.add_mapping(vendor, sku, code):
                    failed_mappings.append(vendor)

        if failed_mappings:
            messagebox.showwarning("Partial Success", f"Product saved, but mappings for {', '.join(failed_mappings)} failed.")
        else:
            messagebox.showinfo("Success", f"Product {code} saved successfully.")
        
        # 3. Cleanup
        self.code_var.set("")
        self.desc_var.set("")
        for row in self.mapping_rows:
            row.destroy()
        self.mapping_rows.clear()
        
        self.on_save_success()
