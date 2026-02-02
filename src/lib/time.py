import re

multipliers = {
    "h": 1,     # Hours
    "d": 24,    # Days
    "w": 168,   # Weeks
}


def parse_duration(duration: str) -> int | None:
    """Parses a sting like '2w', '10d', '5h' and converts it into hours"""
    if not duration:
        return None

    # Normalize input
    s = duration.lower().strip()

    # Separates the number from the symbol(unit)
    match = re.match(r"^([0-9]+)([hdw]?)$", s)
    # Invalid format
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)
    
    if value < 0:
        return None

    if not unit:
        return value
    return value * multipliers[unit]


def format_duration(hours: int) -> str:
    """Concers a number of hours into a unit string"""

    if not isinstance(hours, int) or hours <= 0:
        return "0h"

    hours = int(hours)
    
    for m in reversed(multipliers.items()):
        unit, var = m
        if hours >= var and hours % var == 0:
            return f"{hours // var}{unit}"
