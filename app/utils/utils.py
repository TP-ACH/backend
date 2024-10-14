from datetime import datetime
from utils.consts import (
    MIN_EC,
    MAX_EC,
    MIN_TEMP,
    MAX_TEMP,
    MIN_HUMIDITY,
    MAX_HUMIDITY,
    MIN_FLOATER,
    MAX_FLOATER,
    MIN_PH,
    MAX_PH,
)


def value_in_range(metric, value):
    ranges = {
        "ec": (MIN_EC, MAX_EC),
        "temperature": (MIN_TEMP, MAX_TEMP),
        "humidity": (MIN_HUMIDITY, MAX_HUMIDITY),
        "floater": (MIN_FLOATER, MAX_FLOATER),
        "ph": (MIN_PH, MAX_PH),
    }

    if metric == "light_hours":
        return is_valid_light_hours(value)

    return is_value_in_ranges(metric, value, ranges)


def is_valid_light_hours(value):
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


def is_value_in_ranges(metric, value, ranges):
    if metric in ranges:
        min_val, max_val = ranges[metric]
        return min_val <= value <= max_val
    return False
