import math
import tkinter as tk

import pandas as pd
import ttkbootstrap as ttk
from rapidfuzz import fuzz, process

from src.core.database import database as db
from src.gui.widgets.registry_widgets import (
    RegistryHeader,
    RegistryPagination,
    RegistryRow,
    RegistrySearch,
)
from src.lib.data import prepare_registry_data


class RegistryFooter(ttk.Frame):
    """Bottom section for pagination, refresh, and navigation to Add Code."""

    def __init__(self, parent, on_page_change, on_refresh, on_add_code):
        super().__init__(parent, padding=10)

        # 1. Pagination (Left)
        self.pagination = RegistryPagination(self, on_page_change=on_page_change)
        self.pagination.pack(side="left")

        # 2. Add Code (Right)
        ttk.Button(
            self,
            text="Add Code",
            bootstyle="success",
            command=on_add_code,
        ).pack(side="right")

        # 3. Refresh (Next to Add Code)
        ttk.Button(
            self,
            text="Refresh",
            bootstyle="info-outline",
            command=on_refresh,
        ).pack(side="right", padx=20)


class Registry(ttk.Frame):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        
        # Data & Pagination State
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self.total_pages = 1
        
        # Search State
        self.last_query = ""
        self.last_search_col = "description"
        
        # Cache for preloading (page_num -> DataFrame)
        self._cache = {}

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        # 1. Search Bar (Top)
        self.search_bar = RegistrySearch(
            self, on_search_callback=self.on_search_triggered
        )
        self.search_bar.pack(side="top", fill="x")

        # 2. Main Container for Data
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10)

        self.canvas = ttk.Canvas(self.container, highlightthickness=0)

        self.v_scrollbar = ttk.Scrollbar(
            self.container,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            bootstyle="primary-round",
        )
        self.h_scrollbar = ttk.Scrollbar(
            self.container,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
            bootstyle="primary-round",
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set
        )

        # Scroll Frame
        self.scroll_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )

        # Header & Rows holders
        self.header_holder = ttk.Frame(self.scroll_frame)
        self.header_holder.pack(side="top", fill="x")

        self.rows_holder = ttk.Frame(self.scroll_frame)
        self.rows_holder.pack(side="top", fill="x")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # 3. Footer (Bottom)
        self.footer = RegistryFooter(
            self, 
            on_page_change=self.change_page, 
            on_refresh=self.refresh_data,
            on_add_code=self.open_add_code
        )
        self.footer.pack(side="bottom", fill="x")

    def open_add_code(self):
        """Notifies application to switch to Add Code tab."""
        self.event_generate("<<OpenAddCode>>")

    def refresh_data(self):
        """Clears cache and fetches current view"""
        self._cache.clear()
        self.total_count = db.get_total_count(self.last_query, self.last_search_col)
        self.total_pages = max(1, math.ceil(self.total_count / self.page_size))
        
        self.current_page = 1
        self._load_and_display()

    def on_search_triggered(self, query):
        """Parses prefix and triggers refresh"""
        query = query.strip()
        search_col = "description"
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

        self.last_query = actual_query
        self.last_search_col = search_col
        self.refresh_data()

    def change_page(self, delta):
        """Navigates pages and triggers preloading"""
        new_page = self.current_page + delta
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self._load_and_display()

    def _load_and_display(self):
        """Gets data (from cache or DB), displays it, and preloads neighbors"""
        # 1. Get current page
        df = self._get_page(self.current_page)
        
        # 2. Update Header (only if columns changed/first time)
        if not self.header_holder.winfo_children() and not df.empty:
            self._update_headers(df.columns)

        # 3. Display
        self._display_results(df)
        
        # 4. Proactive Preloading (Next and Previous)
        if self.current_page + 1 <= self.total_pages:
            self.after(50, lambda: self._get_page(self.current_page + 1))
        if self.current_page - 1 >= 1:
            self.after(50, lambda: self._get_page(self.current_page - 1))

    def _get_page(self, page_num):
        """Returns a page from cache or fetches from DB"""
        if page_num in self._cache:
            return self._cache[page_num]
        
        # Fetch from DB
        df = db.get_registry_page(
            page=page_num, 
            page_size=self.page_size, 
            query=self.last_query, 
            search_col=self.last_search_col
        )
        self._cache[page_num] = df
        
        # Keep cache size small (e.g., current + 2 neighbors)
        if len(self._cache) > 5:
            # Remove furthest page
            keys = sorted(self._cache.keys())
            if keys[0] < self.current_page - 1:
                del self._cache[keys[0]]
            elif keys[-1] > self.current_page + 1:
                del self._cache[keys[-1]]
                
        return df

    def _update_headers(self, columns):
        """Rebuilds header based on columns"""
        for widget in self.header_holder.winfo_children():
            widget.destroy()

        header = RegistryHeader(self.header_holder, columns)
        header.pack(fill="x")

    def _display_results(self, df):
        """Renders the current dataframe rows"""
        for widget in self.rows_holder.winfo_children():
            widget.destroy()

        # Update stats in pagination
        self.footer.pagination.set_page_text(self.current_page, self.total_pages)

        # 1. Prepare data
        rows_data = prepare_registry_data(df)

        # 2. Calculate starting index for display numbering
        start_idx = (self.current_page - 1) * self.page_size

        # 3. Render rows
        for i, row in enumerate(rows_data):
            display_idx = start_idx + i + 1
            row_widget = RegistryRow(self.rows_holder, row, display_idx)
            row_widget.pack(fill="x", pady=1)

        # 4. Reset scroll
        self.canvas.yview_moveto(0)
