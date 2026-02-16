import tkinter as tk
import ttkbootstrap as ttk
from rapidfuzz import process, fuzz
import pandas as pd

from src.gui.widgets.registry_widgets import RegistryRow, RegistryHeader, RegistrySearch


class Registry(ttk.Frame):
    """The main Registry tab orchestrating search, headers, and data view."""

    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        self.data = pd.DataFrame()

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        # 1. Search Component
        self.search_bar = RegistrySearch(self, on_search_callback=self.perform_search)
        self.search_bar.pack(side="top", fill="x")

        # 2. Main Container for Data (Canvas + Scrollbars)
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Canvas for both Header and Rows to sync horizontal scroll
        self.canvas = ttk.Canvas(self.container, highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(
            self.container, orient=tk.VERTICAL, command=self.canvas.yview, bootstyle="primary-round"
        )
        self.h_scrollbar = ttk.Scrollbar(
            self.container, orient=tk.HORIZONTAL, command=self.canvas.xview, bootstyle="primary-round"
        )

        # Layout using grid for precise placement of scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        # Configure Canvas
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Content Frame inside Canvas
        self.scroll_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )

        # 3. Header and Row holders inside the scroll_frame
        self.header_holder = ttk.Frame(self.scroll_frame)
        self.header_holder.pack(side="top", fill="x")

        self.rows_holder = ttk.Frame(self.scroll_frame)
        self.rows_holder.pack(side="top", fill="x")

        # Bindings for scrolling
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

    def refresh_data(self):
        """Fetches fresh data and updates UI."""
        self.data = self.backend.database.get_registry_data()
        self._update_headers()
        self.perform_search("")

    def _update_headers(self):
        """Updates the dynamic header based on current data columns."""
        for widget in self.header_holder.winfo_children():
            widget.destroy()

        if not self.data.empty:
            header = RegistryHeader(self.header_holder, self.data.columns)
            header.pack(fill="x")

    def perform_search(self, query):
        """Logic for filtering data based on search query and prefixes."""
        query = query.strip()

        if not query:
            self._display_results(self.data)
            return

        # Handle prefixes
        search_col = "description"  # Default
        actual_query = query

        if query.startswith("@wcd"):
            search_col = "warehouse_code"
            actual_query = query[4:].strip()
        elif query.startswith("@desc"):
            search_col = "description"
            actual_query = query[5:].strip()
        elif query.startswith("@sku"):
            search_col = "all"
            actual_query = query[4:].strip()

        if not actual_query:
            self._display_results(self.data)
            return

        # Prepare search series
        if search_col == "all":
            search_series = self.data.apply(
                lambda row: " ".join(row.values.astype(str)), axis=1
            )
        else:
            target = search_col if search_col in self.data.columns else "description"
            search_series = self.data[target].astype(str)

        # RapidFuzz search
        results = process.extract(
            actual_query, search_series, scorer=fuzz.partial_ratio, limit=100
        )

        ordered_indices = [idx for res, score, idx in results if score > 40]
        matched_df = self.data.iloc[ordered_indices]

        self._display_results(matched_df)

    def _display_results(self, df):
        """Clears and repopulates the rows holder with new data."""
        for widget in self.rows_holder.winfo_children():
            widget.destroy()

        for i, (idx, row) in enumerate(df.iterrows()):
            row_widget = RegistryRow(self.rows_holder, row.to_dict(), i + 1)
            row_widget.pack(fill="x", pady=1)


if __name__ == "__main__":
    class MockDatabase:
        def get_registry_data(self):
            # Create a very wide dataframe to test horizontal scrolling
            cols = {
                "warehouse_code": [f"WCD{i:03d}" for i in range(1, 31)],
                "description": [f"Long Product Description for Item {i} that should take some space" for i in range(1, 31)]
            }
            for v in range(1, 11): # 10 vendors
                cols[f"vendor_{v}_sku"] = [f"V{v}-SKU-{i*100}" for i in range(1, 31)]
            
            return pd.DataFrame(cols)

    class MockBackend:
        def __init__(self):
            self.database = MockDatabase()

    app = ttk.Window(themename="darkly")
    app.title("Registry Test - Dual Scrollbars")
    app.geometry("1000x600")

    registry = Registry(app, MockBackend())
    registry.pack(fill="both", expand=True)

    app.mainloop()
