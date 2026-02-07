import tkinter as tk
from tkinter import END, constants

import ttkbootstrap as ttk

from src.gui.widgets.review_widgets import CodeSearch


class Row:
    pass


class Review:
    pass


if __name__ == "__main__":
    # 1. Setup a test window with a theme (try 'darkly' or 'flatly')
    app = ttk.Window(themename="darkly")
    app.geometry("400x300")
    app.title("Widget Test Lab")

    # 2. Create dummy data
    codes = [
        "WH-001",
        "WH-002",
        "WH-003",
        "WH-104",
    ]
    descriptions = [
        "M5 Hex Bolt Stainless",
        "M5 Hex Nut",
        "M8 Washer",
        "Hydraulic Pump 500W",
    ]
    # 3. Instantiate your widget
    # We pack it with some padding to see it clearly
    widget = CodeSearch(app, codes, descriptions)
    widget.pack(pady=50, padx=20)

    app.mainloop()
