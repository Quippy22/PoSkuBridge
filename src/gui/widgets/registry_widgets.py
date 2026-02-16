import ttkbootstrap as ttk


class RegistryRow(ttk.Frame):
    """A single row representing a database record. Displays all elements horizontally."""

    def __init__(self, parent, row_data: dict, index: int):
        # Add a subtle border to the row
        super().__init__(parent, relief="solid", borderwidth=1)

        if index:
            # 1. The Index Label
            lbl_idx = ttk.Label(
                self,
                text=str(index),
                padding=(5, 5),
                width=6,
                anchor="center",
                bootstyle="secondary",
            )
            lbl_idx.grid(row=0, column=0, sticky="nsew")

        # Divider for index
        ttk.Frame(self, width=1, bootstyle="secondary").grid(
            row=0, column=1, sticky="ns"
        )

        # 2. Iterate through the dictionary and create a label for every element
        for i, (key, value) in enumerate(row_data.items()):
            # Determine width based on column key
            col_width = 50 if key == "description" else 20

            # Handle None values gracefully
            display_text = str(value) if value is not None else "-" * col_width

            # Create the label with the full text
            lbl = ttk.Label(
                self,
                text=display_text,
                padding=(10, 5),
                width=col_width,
                anchor="w",
            )
            # Offset column by 2 because of the index label and its divider
            lbl.grid(row=0, column=(i * 2) + 2, sticky="nsew")

            # Add a more visible divider (using a Frame with background color)
            divider = ttk.Frame(self, width=1, bootstyle="secondary")
            divider.grid(row=0, column=(i * 2) + 3, sticky="ns", padx=0)


class RegistryHeader(ttk.Frame):
    """Header for the registry table, dynamically adjusts to columns."""

    def __init__(self, parent, columns):
        super().__init__(parent, padding=(0, 0))

        # Index placeholder
        ttk.Label(
            self,
            text="No.",
            width=6,
            anchor="center",
            bootstyle="inverse-secondary",
            padding=(5, 5),
        ).grid(row=0, column=0)
        ttk.Frame(self, width=1, bootstyle="secondary").grid(
            row=0, column=1, sticky="ns"
        )

        for i, col in enumerate(columns):
            col_width = 50 if col == "description" else 20
            # Clean up column name: "vendor_name" -> "Vendor Name"
            display_name = col.replace('"', "").replace("_", " ").title()

            lbl = ttk.Label(
                self,
                text=display_name,
                width=col_width,
                anchor="w",
                bootstyle="inverse-secondary",
                padding=(10, 5),
            )
            lbl.grid(row=0, column=(i * 2) + 2, sticky="nsew")
            ttk.Frame(self, width=1, bootstyle="secondary").grid(
                row=0, column=(i * 2) + 3, sticky="ns"
            )


class RegistrySearch(ttk.Frame):
    """Search bar component with prefix support and fuzzy finding logic."""

    def __init__(self, parent, on_search_callback):
        super().__init__(parent, padding=10)
        self.callback = on_search_callback

        # Help label for prefixes - Moved to the left
        help_lbl = ttk.Label(
            self,
            text="@wcd: code | @desc: description | @sku: all",
            font=("Segoe UI", 9),
            bootstyle="secondary",
        )
        help_lbl.pack(side="left", padx=(0, 15))

        ttk.Label(self, text="Search:", font=("Segoe UI", 10, "bold")).pack(
            side="left", padx=(0, 5)
        )

        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.callback(self.search_var.get()))

        self.search_entry = ttk.Entry(
            self, textvariable=self.search_var, font=("Segoe UI", 11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
