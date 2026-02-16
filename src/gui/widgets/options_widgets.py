from tkinter import filedialog

import ttkbootstrap as ttk


class PathSelector(ttk.Frame):
    """
    A reusable widget for selecting a directory path.
    Layout:
      [Label Title]
      [Path Entry (Readonly)] [📂 Button]
    """
    def __init__(self, parent, label_text, path_var):
        super().__init__(parent)
        self.path_var = path_var

        # 1. The Name (Top)
        ttk.Label(self, text=label_text, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", pady=(0, 2)
        )

        # 2. Container for the input row
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x", pady=(0, 10))

        # 3. The Path Display (Entry)
        self.entry = ttk.Entry(row_frame, textvariable=self.path_var, state="readonly")
        self.entry.pack(side="left", fill="x", expand=True)

        # 4. The Icon Button
        self.btn = ttk.Button(
            row_frame,
            text="📂",
            width=4,
            bootstyle="secondary-outline",
            command=self.browse_folder,
        )
        self.btn.pack(side="left", padx=(5, 0))

    def browse_folder(self):
        """Opens directory picker and updates variable"""
        new_path = filedialog.askdirectory()
        if new_path:
            self.path_var.set(new_path)


class ToggleSetting(ttk.Frame):
    """A reusable row with text on the left and a toggle switch on the right"""
    def __init__(self, parent, label_text, variable, color="success"):
        super().__init__(parent)

        # 1. Label (Left)
        lbl = ttk.Label(self, text=label_text)
        lbl.pack(side="left", anchor="center")

        # 2. Toggle Switch (Right)
        style_name = f"{color}-round-toggle"

        self.toggle = ttk.Checkbutton(
            self,
            variable=variable,
            bootstyle=style_name,
            onvalue=True,
            offvalue=False
        )
        self.toggle.pack(side="right", anchor="center")


class SliderSetting(ttk.Frame):
    def __init__(self, parent, label_text, variable, min_val: float = 0, max_val: float = 1):
        super().__init__(parent)
        self.variable = variable
        
        # 1. Label (Left)
        ttk.Label(self, text=label_text).pack(side="left", anchor="center")
        
        # 2. Value Display (Right Edge) - "80%"
        # We save this as self.val_label so we can update it
        self.val_label = ttk.Label(self, text=self.variable.get(), width=4)
        self.val_label.pack(side="right", padx=(10, 0))
        
        # 3. Slider (Fill Remaining Space)
        self.scale = ttk.Scale(
            self, 
            variable=variable, 
            from_=min_val, 
            to=max_val, 
            command=self.snap_to_step
        )
        self.scale.pack(side="right", fill="x", expand=True, padx=10)

    def snap_to_step(self, value):
        """Forces the slider to snap to 0.1 increments"""
        try:
            float_val = float(value)
            snapped_val = round(float_val, 1)
            
            # Force the variable (and slider handle) to the snapped position
            self.variable.set(snapped_val)
            
            # Update text
            percent = int(snapped_val * 100)
            self.val_label.config(text=f"{percent}%")
            
        except ValueError:
            pass


class DropdownSetting(ttk.Frame):
    """A reusable row with text on the left and a dropdown on the right"""
    def __init__(self, parent, label_text, variable, values):
        super().__init__(parent)
        
        # 1. Label (Left)
        ttk.Label(self, text=label_text).pack(side="left", anchor="center")

        # 2. Dropdown (Right)
        self.combo = ttk.Combobox(
            self,
            textvariable=variable,
            values=values,
            state="readonly",
            width=10
        )
        self.combo.pack(side="right", anchor="center")
