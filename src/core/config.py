from pathlib import Path
import json


class Settings:
    def __init__(self):
        # Paths
        # src/core/config.py -> src/core/ -> src/ -> root
        self.root = Path(__file__).resolve().parent.parent.parent

        # Backup settings
        self._max_backups = 2
        self._backup_interval = 24  # Hours

    @property
    def max_backups(self):
        return self._max_backups

    @max_backups.setter
    def max_backups(self, value):
        if value == 0:
            # None = no limit
            self._max_backups = None
            print("Backup limit disabled")
        elif value > 0:
            self._max_backups = value
            print(f"Backup limit set to {value}")
        else:
            print(f"Invalid value: {value}, value has to be a pozitive integer!")

    @property
    def backup_interval(self):
        return self._backup_interval

    @backup_interval.setter
    def backup_interval(self, value):
        # 0 = Disabled
        if value == 0 or value == "0":
            self._backup_interval = 0
            print("Automated backups: DISABLED")
            return

        # Logic for strings (1d, 2w, etc.)
        if isinstance(value, str):
            unit = value[-1].lower()
            try:
                number = int(value[:-1])

                if number < 1:
                    print("Value must be positive")
                    return

                multipliers = {"h": 1, "d": 24, "w": 168}

                if unit in multipliers:
                    self._backup_interval = number * multipliers[unit]
                    print(
                        f"Automated backups: Every {self._backup_interval} hours ({value})"
                    )
                else:
                    print(f"Unknown unit '{unit}'. Use h, d, or w.")
            except ValueError:
                print(f"Invalid format '{value}'. Settings unchanged.")

        # Logic for raw integers (Hours)
        elif isinstance(value, int) and value > 0:
            self._backup_interval = value
            print(f"Automated backups: Every {value} hours")

    def to_json(self, destination_path):
        # 1. Get the raw dictionary
        raw_data = vars(self)

        # 2. Create a "Clean" dictionary
        clean_data = {}
        for key, value in raw_data.items():
            # Remove leading underscore if it exists
            clean_key = key.lstrip("_")

            # Convert Path objects to strings
            if isinstance(value, Path):
                clean_data[clean_key] = str(value)
            else:
                clean_data[clean_key] = value

        # 3. Save the file
        with open(destination_path, "w") as f:
            json.dump(clean_data, f, indent=4)


config = Settings()
