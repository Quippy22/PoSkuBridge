import json
from pathlib import Path

from loguru import logger

from src.lib.time import parse_duration


class Settings:
    DEFAULTS = {
        # --- GUI ---
        "resolution": "800x600",
        "gui_theme": "litera",
        # --- WORKFLOW ---
        # Options: "OFF", "AUTO", "HYBRID"
        "working_mode": "off",
        "keep_working_mode": False,
        # Moved processed files into archive folder
        "archive_processed_files": True,
        # After processing a file/batch of files open the output folder
        "open_output_folder": False,
        # --- MATCHER ---
        # Switch to turn fuzzy matching ON or OFF
        "enable_fuzzy_match": False,
        # The threshold for the fuzzy match (0.1 to 0.9)
        "fuzzy_threshold": 0.8,
        # --- BACKUP ---
        "max_backups": 10,
        "backup_interval": 24,
    }

    def __init__(self):
        # Paths
        self.root = self._get_root_path()
        self.internal_dir = self.root / "Internal"
        self.config_path = self.internal_dir / "config.json"
        self.db_path = self.internal_dir / "mappings.db"
        self.logs_path = self.internal_dir / "Logs"
        self.backup_path = self.internal_dir / "Backups"

        # Load the defaults
        self._data = self.DEFAULTS.copy()

        # Dynamic defaults (Based on Root)
        self._data["input_dir"] = str(self.root / "Data" / "Input")
        self._data["output_dir"] = str(self.root / "Data" / "Output")
        self._data["review_dir"] = str(self.root / "Data" / "Review")
        self._data["archive_dir"] = str(self.root / "Data" / "Archive")

        # Make sure the internal folder exists
        self._ensure_internal_structure()
        # Load settings if they exist
        self.load()

    def _get_root_path(self):
        """Finds the Root by searching for the 'src' folder and going one above"""
        current_path = Path(__file__).resolve()
        for p in current_path.parents:
            if p.name == "src":
                return p.parent

        # If things fail, go back to the origins
        logger.warning("Could not find 'src' folder. Falling back to relative path.")
        return Path(__file__).resolve().parent.parent.parent

    def _ensure_internal_structure(self):
        if not self.internal_dir.exists():
            self.internal_dir.mkdir(parents=True)

    def load(self):
        """Loads JSON and pushes values through the Setters"""
        if not self.config_path.exists():
            logger.warning(f"No config found at {self.config_path}. Creating a new one")
            self.save()
            return

        try:
            with open(self.config_path, "r") as f:
                loaded_data = json.load(f)

            for key, value in loaded_data.items():
                self._data[key] = value

            # Enforce the logic: If we don't keep the mode, reset to OFF
            if not self._data.get("keep_working_mode", False):
                self._data["working_mode"] = "off"

            logger.info("Settings loaded.")
        except Exception as e:
            logger.error(f"Config corrupt ({e}). Using defaults.")
            self._data = self.DEFAULTS.copy()
            self.save()

    def save(self, path=None):
        if path is None:
            path = self.config_path
        with open(path, "w") as f:
            json.dump(self._data, f, indent=4)
        logger.info("Settings saved")

    # -- Path Properties --
    @property
    def input_dir(self) -> Path:
        return Path(self._data["input_dir"])

    @input_dir.setter
    def input_dir(self, value):
        self._data["input_dir"] = str(value)

    @property
    def output_dir(self) -> Path:
        return Path(self._data["output_dir"])

    @output_dir.setter
    def output_dir(self, value):
        self._data["output_dir"] = str(value)

    @property
    def review_dir(self) -> Path:
        return Path(self._data["review_dir"])

    @review_dir.setter
    def review_dir(self, value):
        self._data["review_dir"] = str(value)

    @property
    def archive_dir(self) -> Path:
        return Path(self._data["archive_dir"])

    @archive_dir.setter
    def archive_dir(self, value):
        self._data["archive_dir"] = str(value)

    # -- GUI Properties --
    @property
    def resolution(self) -> str:
        return self._data.get("resolution")

    @resolution.setter
    def resolution(self, res):
        self._data["resolution"] = str(res)

    @property
    def gui_theme(self) -> str:
        return self._data.get("gui_theme")

    @gui_theme.setter
    def gui_theme(self, theme):
        self._data["gui_theme"] = theme

    # -- Workflow Properties --
    @property
    def working_mode(self) -> str:
        return self._data.get("working_mode")

    @working_mode.setter
    def working_mode(self, value):
        # 1. Define allowed states
        valid_modes = ["off", "auto", "hybrid"]

        # 2. Normalize input (Handle "auto", "Auto", "AUTO")
        val = str(value).lower()

        # 3. Validate
        if val in valid_modes:
            self._data["working_mode"] = val
        else:
            logger.error(f"Invalid mode: '{value}'. Must be one of {valid_modes}")

    @property
    def archive_processed_files(self) -> bool:
        # Default: True (Move files out of Input when done)
        return self._data.get("archive_processed_files", True)

    @archive_processed_files.setter
    def archive_processed_files(self, value):
        self._data["archive_processed_files"] = bool(value)

    @property
    def open_output_folder(self) -> bool:
        # Default: False (Don't annoy user with popups)
        return self._data.get("open_output_folder", False)

    @open_output_folder.setter
    def open_output_folder(self, value):
        self._data["open_output_folder"] = bool(value)

    @property
    def keep_working_mode(self) -> bool:
        return self._data.get("keep_working_mode", False)

    @keep_working_mode.setter
    def keep_working_mode(self, value):
        self._data["keep_working_mode"] = bool(value)

    # -- Matcher Properties --
    @property
    def enable_fuzzy_match(self) -> bool:
        # Master switch for the feature
        return self._data.get("enable_fuzzy_match", False)

    @enable_fuzzy_match.setter
    def enable_fuzzy_match(self, value):
        self._data["enable_fuzzy_match"] = bool(value)

    @property
    def fuzzy_threshold(self) -> float:
        # Default to 0.8 if missing
        return self._data.get("fuzzy_threshold", 0.8)

    @fuzzy_threshold.setter
    def fuzzy_threshold(self, value):
        try:
            val = float(value)
            val = round(val, 1)

            if val < 0.1:
                val = 0.1
            if val > 0.9:
                val = 0.9

            self._data["fuzzy_threshold"] = val

        except ValueError:
            logger.error(f"Invalid threshold: {value}. Must be a number.")

    # -- Backup Properties --
    @property
    def max_backups(self) -> int:
        return self._data.get("max_backups")

    @max_backups.setter
    def max_backups(self, value):
        if value == 0:
            # None = no limit
            self._data["max_backups"] = None
        elif value > 0:
            self._data["max_backups"] = value
        else:
            logger.error(f"Invalid value: {value}, value has to be a positive integer!")

    @property
    def backup_interval(self) -> int:
        return self._data.get("backup_interval")

    @backup_interval.setter
    def backup_interval(self, value):
        """Accepts strings like '4w', '2d', '1'. 0 = Disabled"""
        if isinstance(value, str):
            hours = parse_duration(value)
            # Invalid format, don't change the value
            if hours is None:
                logger.error(f"Invalid time format. The backup interval cannot be {value}")
                return
        else:
            hours = value
            if hours < 0:
                logger.error("Backup interval cannot be negative.")
                return

        if hours == 0:
            logger.info("Automated backup disabled")

        self._data["backup_interval"] = hours


settings = Settings()
