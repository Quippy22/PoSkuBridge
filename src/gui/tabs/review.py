import tkinter as tk

import ttkbootstrap as ttk
from loguru import logger

from src.core.database import database as db
from src.gui.widgets.review_widgets import ReviewRow


class Footer(ttk.Frame):
    """The footer for the review tab"""

    def __init__(self, parent, stats: dict, on_unconfirm, on_confirm, on_commit):
        super().__init__(parent)
        self.pack(side="bottom", fill="x", pady=5, padx=10)

        # -- Left side --
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(side="left")

        # Green count
        self.var_green = ttk.StringVar(value=str(stats["green"]))
        ttk.Label(
            self.stats_frame,
            textvariable=self.var_green,
            bootstyle="success",
            font=("Consolas", 12, "bold"),
        ).pack(side="left")

        # Separator
        ttk.Label(self.stats_frame, text=" / ", font=("Consolas", 12)).pack(side="left")

        # Yellow count
        self.var_yellow = ttk.StringVar(value=str(stats["yellow"]))
        ttk.Label(
            self.stats_frame,
            textvariable=self.var_yellow,
            bootstyle="warning",
            font=("Consolas", 12, "bold"),
        ).pack(side="left")

        # Separator
        ttk.Label(self.stats_frame, text=" / ", font=("Consolas", 12)).pack(side="left")

        # Red count
        self.var_red = ttk.StringVar(value=str(stats["red"]))
        ttk.Label(
            self.stats_frame,
            textvariable=self.var_red,
            bootstyle="danger",
            font=("Consolas", 12, "bold"),
        ).pack(side="left")

        # -- Right side __
        self.actions_frame = ttk.Frame(self)
        self.actions_frame.pack(side="right")

        ttk.Button(
            self.actions_frame,
            text="Unconfirm All",
            bootstyle="secondary-outline",
            command=on_unconfirm,
        ).pack(side="left", padx=5)

        ttk.Button(
            self.actions_frame,
            text="Confirm All",
            bootstyle="success-outline",
            command=on_confirm,
        ).pack(side="left", padx=5)

        ttk.Button(
            self.actions_frame, text="Commit", bootstyle="primary", command=on_commit
        ).pack(side="left", padx=5)


class Review(ttk.Labelframe):
    def __init__(
        self, parent, backend, rows_data: list[dict], stats: dict, supplier: str
    ):
        super().__init__(parent, text=f"Reviewing mappings for {supplier}")
        self.backend = backend
        self.supplier = supplier

        # -- The main container --
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # The scrollable window
        self.canvas = ttk.Canvas(self.container)
        self.canvas.pack(side="left", fill="both", expand=True)

        # The scollbar
        self.scrollbar = ttk.Scrollbar(
            self.container, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )
        # Make the inner frame as wide as the canvas
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Force the frame to expand to fill width when window resizes
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        # The rows
        self.rows = []
        self.generate_rows(rows_data)

        # -- The footer --
        self.footer = Footer(
            self,
            stats=stats,
            on_unconfirm=self.on_unconfirm,
            on_confirm=self.on_confirm,
            on_commit=self.on_commit,
        )

    def generate_rows(self, rows_data: list[dict]):
        # Clear
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.rows.clear()

        # Get codes and descriptions
        df = db.get_products()
        codes = df["warehouse_code"].dropna().astype(str).tolist()
        descriptions = df["descriptions"].dropna().astype(str).tolist()

        # Add the row to the list
        for r in rows_data:
            row = ReviewRow(
                self.scroll_frame,
                row_data=r,
                codes_list=codes,
                descriptions_list=descriptions,
            )
            self.rows.append(row)

    def on_unconfirm(self):
        for r in self.rows:
            r.is_confirmed.set(False)
            r.search.enable()

    def on_confirm(self):
        for r in self.rows:
            r.is_confirmed.set(True)
            r.search.disable()

    def on_commit(self):
        mappings = []
        for r in self.rows:
            code, sku = r.get_mapping()
            mappings.append({"sku": sku, "warehouse_code": code})

        if mappings:
            # TODO: call helper to add the mappings
            logger.info(f"User committed {len(mappings)} new mappings for {self.supplier}")
