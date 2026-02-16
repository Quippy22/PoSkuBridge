import ttkbootstrap as ttk


class RegistryRow(ttk.Frame):
    """A single row representing a database record. Displays all elements horizontally."""

    def __init__(self, parent, row_data: dict, index: int):
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

        # Divider
        ttk.Frame(self, width=1, bootstyle="secondary").grid(
            row=0, column=1, sticky="ns"
        )

        # 2. Columns
        for i, (key, value) in enumerate(row_data.items()):
            # Dynamic width
            col_width = 50 if key == "description" else 20

            display_text = str(value) if value is not None else "-" * col_width

            lbl = ttk.Label(
                self,
                text=display_text,
                padding=(10, 5),
                width=col_width,
                anchor="w",
            )
            # Offset by 2 (index + divider)
            lbl.grid(row=0, column=(i * 2) + 2, sticky="nsew")

            # Column Divider
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

        # Generate headers
        for i, col in enumerate(columns):
            col_width = 50 if col == "description" else 20
            # Clean name
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


class RegistryPagination(ttk.Frame):
    """Dedicated pagination controls with page number and arrows."""

    def __init__(self, parent, on_page_change):
        super().__init__(parent)
        self.on_page_change = on_page_change

        self.prev_btn = ttk.Button(
            self,
            text="<",
            width=3,
            bootstyle="secondary-outline",
            command=lambda: self.on_page_change(-1),
        )
        self.prev_btn.pack(side="left")

        self.page_label = ttk.Label(
            self,
            text="Page 1",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 0),
        )
        self.page_label.pack(side="left")

        self.next_btn = ttk.Button(
            self,
            text=">",
            width=3,
            bootstyle="secondary-outline",
            command=lambda: self.on_page_change(1),
        )
        self.next_btn.pack(side="left")

    def set_page_text(self, page, total_pages):
        self.page_label.config(text=f"Page {page} / {total_pages}")


class RegistrySearch(ttk.Frame):
    """Search bar component with prefix support and fuzzy finding logic."""

    def __init__(self, parent, on_search_callback):
        super().__init__(parent, padding=10)
        self.callback = on_search_callback
        self._debounce_id = None

        # 1. Help label
        help_lbl = ttk.Label(
            self,
            text="@wcd: code | @desc: description | @sku: all",
            font=("Segoe UI", 9, "bold"),
            bootstyle="info",
        )
        help_lbl.pack(side="left", padx=(0, 15))

        # 2. Search input
        ttk.Label(self, text="Search:", font=("Segoe UI", 10, "bold")).pack(
            side="left", padx=(0, 5)
        )

        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self._on_type)

        self.search_entry = ttk.Entry(
            self, textvariable=self.search_var, font=("Segoe UI", 11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

    def _on_type(self, *args):
        """Cancels previous timer and starts a new 300ms one."""
        if self._debounce_id:
            self.after_cancel(self._debounce_id)

        self._debounce_id = self.after(300, self._trigger_callback)

    def _trigger_callback(self):
        """Executes the search callback with the current query."""
        self.callback(self.search_var.get())
