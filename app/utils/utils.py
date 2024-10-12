from utils.consts import MIN_EC, MAX_EC, MIN_TEMP, MAX_TEMP, MIN_HUMIDITY, MAX_HUMIDITY, MIN_FLOATER, MAX_FLOATER, MIN_PH, MAX_PH

def value_in_range(metric, value):
    ranges = {
        "ec": (MIN_EC, MAX_EC),
        "temperature": (MIN_TEMP, MAX_TEMP),
        "humidity": (MIN_HUMIDITY, MAX_HUMIDITY),
        "floater": (MIN_FLOATER, MAX_FLOATER),
        "ph": (MIN_PH, MAX_PH)
    }
    
    if metric in ranges:
        min_val, max_val = ranges[metric]
        return min_val <= value <= max_val
    return False
