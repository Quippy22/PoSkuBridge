import ttkbootstrap as ttk

from core.config import settings
from gui.widgets import PathSelector, SliderSetting, ToggleSetting


class UiSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Appearance", padding=10)

        # Make the first column expand to fill space
        self.columnconfigure(0, weight=1)

        # -- Resolution --
        ttk.Label(self, text="Window Resolution:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        self.var_res = ttk.StringVar(value=settings.resolution)
        self.combo_res = ttk.Combobox(
            self,
            textvariable=self.var_res,
            values=[
                "640x480",
                "800x600",
                "1024x768",
                "1280x720",
                "1366x768",
                "1920x1080",
            ],
            bootstyle="primary",
            state="readonly",
        )
        self.combo_res.grid(row=0, column=1, sticky="ew", pady=5)

        # -- Theme --
        ttk.Label(self, text="GUI Theme:").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(
                0,
                10,
            ),
        )

        self.var_theme = ttk.StringVar(value=settings.gui_theme)
        self.combo_theme = ttk.Combobox(
            self,
            textvariable=self.var_theme,
            values=[
                "cosmo",
                "flatly",
                "journal",
                "litera",
                "lumen",
                "minty",
                "pulse",
                "sandstone",
                "united",
                "yeti",
                "cyborg",
                "darkly",
                "solar",
                "superhero",
                "vapor",
            ],
            bootstyle="primary",
            state="readonly",
        )
        self.combo_theme.grid(row=1, column=1, sticky="ew", pady=5)


class PathSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Storage Locations")

        self.var_input = ttk.StringVar(value=str(settings.input_dir))
        self.var_output = ttk.StringVar(value=str(settings.output_dir))
        self.var_review = ttk.StringVar(value=str(settings.review_dir))
        self.var_archive = ttk.StringVar(value=str(settings.archive_dir))

        # -- Create the Selectors --
        PathSelector(self, "Input Directory", self.var_input).pack(fill="x")
        PathSelector(self, "Output Directory", self.var_output).pack(fill="x")
        PathSelector(self, "Review Directory", self.var_review).pack(fill="x")
        PathSelector(self, "Archive Directory", self.var_archive).pack(fill="x")


class WorkflowSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="General Behavior")

        # --- 1. Archive Files ---
        self.var_archive = ttk.BooleanVar(value=settings.archive_processed_files)
        ToggleSetting(self, "Archive processed files", self.var_archive).pack(
            fill="x", pady=5
        )

        # --- 2. Open Output ---
        self.var_open = ttk.BooleanVar(value=settings.open_output_folder)
        ToggleSetting(self, "Open output folder after completion", self.var_open).pack(
            fill="x", pady=5
        )


class MatcherSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Accuracy Settings")
        # -- Fuzzy Match Switch --
        self.var_fuzzy = ttk.BooleanVar(value=settings.enable_fuzzy_match)
        ToggleSetting(
            self, "Enable Fuzzy Matching", self.var_fuzzy, color="primary"
        ).pack(fill="x", pady=5)

        # -- Threshold Slider ---
        self.var_threshold = ttk.DoubleVar(value=settings.fuzzy_threshold)
        SliderSetting(
            self,
            label_text="Match Confidence Threshold",
            variable=self.var_threshold,
            min_val=0.1,  # 10%
            max_val=0.9,  # 90%
        ).pack(fill="x", pady=5)


class BackupSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Data & Backup", padding=15)

        # --- 1. Max Backups ---
        # accessing global settings directly
        self.var_max_backups = ttk.StringVar(value=str(settings.max_backups))

        self.create_labeled_entry(
            label_text="Maximum number of backups to keep",
            variable=self.var_max_backups,
            help_text="0 = No limit (keep all backups)",
        )

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15)

        # --- 2. Auto Backup Frequency ---
        # Parse the global setting "5d" or "2w"
        raw_interval = str(settings.backup_interval)

        # Defaults
        init_val = raw_interval
        init_unit = "Hours"

        if raw_interval.endswith("w"):
            init_val = raw_interval[:-1]  # "5w" -> "5"
            init_unit = "Weeks"
        elif raw_interval.endswith("d"):
            init_val = raw_interval[:-1]  # "5d" -> "5"
            init_unit = "Days"

        self.var_freq_val = ttk.StringVar(value=init_val)
        self.var_freq_unit = ttk.StringVar(value=init_unit)

        self.create_frequency_row(
            label_text="Auto-backup frequency",
            var_value=self.var_freq_val,
            var_unit=self.var_freq_unit,
            help_text="0 = Disabled (Manual backups only)",
        )

    def create_labeled_entry(self, label_text, variable, help_text):
        container = ttk.Frame(self)
        container.pack(fill="x", pady=5)

        ttk.Label(container, text=label_text).pack(anchor="w")
        ttk.Entry(container, textvariable=variable).pack(fill="x", pady=(5, 0))
        ttk.Label(
            container, text=help_text, bootstyle="secondary", font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(2, 0))

    def create_frequency_row(self, label_text, var_value, var_unit, help_text):
        container = ttk.Frame(self)
        container.pack(fill="x", pady=5)

        ttk.Label(container, text=label_text).pack(anchor="w")

        row = ttk.Frame(container)
        row.pack(fill="x", pady=(5, 0))

        # Number Box
        ttk.Entry(row, textvariable=var_value).pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )

        # Unit Dropdown
        dropdown = ttk.Combobox(
            row,
            textvariable=var_unit,
            values=["Hours", "Days", "Weeks"],
            width=10,
            state="readonly",
        )
        dropdown.pack(side="right")

        ttk.Label(
            container, text=help_text, bootstyle="secondary", font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(2, 0))

    # Use this helper in save_settings()
    def get_interval_string(self):
        val = self.var_freq_val.get().strip()
        unit = self.var_freq_unit.get()

        if not val or val == "0":
            return "0"

        if unit == "Weeks":
            return f"{val}w"
        elif unit == "Days":
            return f"{val}d"
        else:
            return val


class SettingsActions(ttk.Frame):
    def __init__(self, parent, on_save, on_apply, on_close):
        super().__init__(parent, padding=10)

        # A visual separator line above the buttons
        ttk.Separator(self, orient="horizontal").pack(
            side="top", fill="x", pady=(0, 10)
        )

        # Buttons to the right
        self.btn_close = ttk.Button(
            self, text="Close", bootstyle="secondary", command=on_close
        )
        self.btn_close.pack(side="right", padx=5)

        self.btn_apply = ttk.Button(
            self, text="Apply", bootstyle="info", command=on_apply
        )
        self.btn_apply.pack(side="right", padx=5)

        self.btn_save = ttk.Button(
            self, text="Save", bootstyle="success", command=on_save
        )
        self.btn_save.pack(side="right", padx=5)


class SettingsWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry(settings.resolution)
        self.transient(parent)
        self.grab_set()

        # -- The Footer --
        # Fixed section
        self.footer = SettingsActions(
            self,
            on_save=self.save_settings,
            on_apply=self.apply_settings,
            on_close=self.destroy,
        )
        self.footer.pack(side="bottom", fill="x")

        # -- The Body --
        body = ttk.Frame(self)
        body.pack(side="top", fill="both", expand=True)
        self.canvas = ttk.Canvas(body, highlightthickness=0)

        # The Scrollbar
        self.scrollbar = ttk.Scrollbar(
            body, orient="vertical", bootstyle="round", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # The Scrollable Space
        self.scrollable_frame = ttk.Frame(self.canvas, padding=10)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width),
        )
        container = self.scrollable_frame

        # The content
        self.ui_settings = UiSettings(container)
        self.path_settings = PathSettings(container)
        self.workflow_settings = WorkflowSettings(container)
        self.matcher_settings = MatcherSettings(container)
        self.backup_settings = BackupSettings(container)

        # Packs
        self.ui_settings.pack(fill="x", padx=10, pady=10)
        self.path_settings.pack(fill="x", padx=10, pady=10)
        self.workflow_settings.pack(fill="x", padx=10, pady=10)
        self.matcher_settings.pack(fill="x", padx=10, pady=10)
        self.backup_settings.pack(fill="x", padx=10, pady=10)

    def save_settings(self):
        """Save changes and close"""
        # Save

        self.destroy()

    def apply_settings(self):
        """Apply the changes without closing"""
        pass
