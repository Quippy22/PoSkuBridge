import ttkbootstrap as ttk


class RegistryRow(ttk.Frame):
    """A single row representing a database record.Displays all elements horizontally."""

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
        for i, value in enumerate(row_data.values()):
            # Determine width based on column index
            # Index 1 is description (way bigger)
            col_width = 50 if i == 1 else 20

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
