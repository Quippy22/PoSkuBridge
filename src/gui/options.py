import ttkbootstrap as ttk

from src.core.config import settings
from src.gui.widgets import PathSelector, SliderSetting, ToggleSetting
from src.lib.time import format_duration, parse_duration


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
            row=1, column=0, sticky="w", padx=(0, 10)
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

    def save(self):
        settings.resolution = self.var_res.get()
        settings.gui_theme = self.var_theme.get()

    def is_modified(self):
        if self.var_res.get() != settings.resolution:
            return True

        if self.var_theme.get() != settings.gui_theme:
            return True

        return False


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

    def save(self):
        settings.input_dir = self.var_input.get()
        settings.output_dir = self.var_output.get()
        settings.review_dir = self.var_review.get()
        settings.archive_dir = self.var_archive.get()

    def is_modified(self):
        if settings.input_dir != self.var_input.get():
            return True
        if settings.output_dir != self.var_output.get():
            return True
        if settings.review_dir != self.var_review.get():
            return True
        if settings.archive_dir != self.var_archive.get():
            return True

        return False


class WorkflowSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="General Behavior")

        # -- Archive Files --
        self.var_archive = ttk.BooleanVar(value=settings.archive_processed_files)
        ToggleSetting(self, "Archive processed files", self.var_archive).pack(
            fill="x", pady=5
        )

        # -- Open Output --
        self.var_open = ttk.BooleanVar(value=settings.open_output_folder)
        ToggleSetting(self, "Open output folder after completion", self.var_open).pack(
            fill="x", pady=5
        )

        # -- Keep Working Mode --
        self.var_keep_mode = ttk.BooleanVar(value=settings.keep_working_mode)
        ToggleSetting(
            self, "Keep the working mode after application close", self.var_keep_mode
        ).pack(fill="x", pady=5)

    def save(self):
        settings.archive_processed_files = self.var_archive.get()
        settings.open_output_folder = self.var_open.get()
        settings.keep_working_mode = self.var_keep_mode.get()

    def is_modified(self):
        if settings.archive_processed_files != self.var_archive.get():
            return True
        if settings.open_output_folder != self.var_open.get():
            return True
        if settings.keep_working_mode != self.var_keep_mode.get():
            return True

        return False


class MatcherSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Accuracy Settings")
        # -- Fuzzy Match Switch --
        self.var_fuzzy = ttk.BooleanVar(value=settings.enable_fuzzy_match)
        ToggleSetting(
            self, "Enable Fuzzy Matching", self.var_fuzzy, color="success"
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

    def save(self):
        settings.enable_fuzzy_match = self.var_fuzzy.get()
        settings.fuzzy_threshold = self.var_threshold.get()

    def is_modified(self):
        if settings.enable_fuzzy_match != self.var_fuzzy.get():
            return True
        if settings.fuzzy_threshold != self.var_threshold.get():
            return True

        return False


class BackupSettings(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Data & Backup", padding=15)

        # --- 1. Max Backups ---
        self.var_max_backups = ttk.IntVar(value=settings.max_backups)

        self._create_labeled_entry(
            label_text="Maximum number of backups to keep",
            variable=self.var_max_backups,
            help_text="0 = No limit (keep all backups)",
        )

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15)

        # --- 2. Auto Backup Frequency ---
        # Get the interval in hours
        raw_interval = format_duration(settings.backup_interval)
        # The number
        self.var_freq_val = ttk.StringVar(value=raw_interval[:-1])
        # Map the char back to full word
        unit_map = {"h": "Hours", "d": "Days", "w": "Weeks"}
        self.var_freq_unit = ttk.StringVar(value=unit_map[raw_interval[-1]])

        self._create_frequency_row(
            label_text="Auto-backup frequency",
            var_value=self.var_freq_val,
            var_unit=self.var_freq_unit,
            help_text="0 = Disabled (Manual backups only)",
        )

    def save(self):
        settings.max_backups = self.var_max_backups.get()

        val = self.var_freq_val.get()
        unit = self.var_freq_unit.get()
        settings.backup_interval = f"{val}{unit}"

    def is_modified(self):
        if settings.max_backups != self.var_max_backups.get():
            return True
        val = self.var_freq_val.get()
        unit = self.var_freq_unit.get().lower()[0]
        if settings.backup_interval != parse_duration(f"{val}{unit}"):
            return True

        return False

    def _create_labeled_entry(self, label_text, variable, help_text):
        container = ttk.Frame(self)
        container.pack(fill="x", pady=5)

        ttk.Label(container, text=label_text).pack(anchor="w")
        ttk.Entry(container, textvariable=variable).pack(fill="x", pady=(5, 0))
        ttk.Label(
            container, text=help_text, bootstyle="secondary", font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(2, 0))

    def _create_frequency_row(self, label_text, var_value, var_unit, help_text):
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

        self.modules = [
            self.ui_settings,
            self.path_settings,
            self.workflow_settings,
            self.matcher_settings,
            self.backup_settings,
        ]

        # Packs
        for module in self.modules:
            module.pack(fill="x", padx=10, pady=10)

    def save_settings(self):
        """Save changes and close"""
        self.apply_settings()
        self.destroy()

    def apply_settings(self):
        """Apply the changes without closing"""
        for m in self.modules:
            m.save()
        settings.save()
