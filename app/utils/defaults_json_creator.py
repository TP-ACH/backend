import csv
import json
from utils.consts import (
    PUMP_PH_DOWN_TOPIC,
    PUMP_PH_UP_TOPIC,
    PUMP_NUTRIENT_TOPIC,
    PUMP_WATER_TOPIC,
)
from utils.alerts import Topic
from datetime import datetime
from utils.logger import logger


def create_rule(sensor, lower_bound, upper_bound, lower_action, upper_action):
    return {
        "sensor": sensor,
        "rules": [
            {
                "bound": lower_bound,
                "compare": "less",
                "time": 5,
                "enabled": 1,
                "action": {"type": "mqtt", "dest": lower_action},
            },
            {
                "bound": upper_bound,
                "compare": "greater",
                "time": 5,
                "enabled": 1,
                "action": {"type": "mqtt", "dest": upper_action},
            },
        ],
    }


def create_temperature_and_humidity_rules(humidity_lower_bound, humidity_upper_bound, temp_lower_bound, temp_upper_bound):
    return [
        {
            "sensor": "temperature",
            "rules": [
                {
                    "bound": temp_lower_bound,
                    "compare": "less",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.TEMPERATURE_DOWN.value},
                },
                {
                    "bound": temp_upper_bound,
                    "compare": "greater",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.TEMPERATURE_UP.value},
                },
            ],
        },
        {
            "sensor": "humidity",
            "rules": [
                {
                    "bound": humidity_lower_bound,
                    "compare": "less",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.HUMIDITY_DOWN.value},
                },
                {
                    "bound": humidity_upper_bound,
                    "compare": "greater",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.HUMIDITY_UP.value},
                },
            ],
        },
    ]


def create_floater_rule():
    return [
        {
            "sensor": "floater",
            "rules": [
                {
                    "bound": 0,
                    "compare": "greater",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.WATER_DOWN.value},
                },
            ],
        }
    ]


def create_light_rule(start, end):
    try:
        datetime.strptime(start, "%H:%M")
        datetime.strptime(end, "%H:%M")
    except ValueError:
        raise ValueError(f"Time is not in the correct format '%H:%M'")

    return {
        "start": start,
        "end": end,
        "enabled": 1,
    }


def process_csv_to_json(csv_file="data/plants_defaults.csv"):
    plants_data = []

    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            species = row["species"]
            ph_lower = float(row["ph_lower"])
            ph_upper = float(row["ph_upper"])
            ec_lower = float(row["ec_lower"])
            ec_upper = float(row["ec_upper"])
            humidity_lower = float(row["humidty_lower"])
            humidity_upper = float(row["humidty_upper"])
            temperature_lower = float(row["temperature_lower"])
            temperature_upper = float(row["temperature_upper"])
            light_hours_start = str(row["light_hours_start"])
            light_hours_end = str(row["light_hours_end"])

            plant_rules = {
                "species": species,
                "rules_by_sensor": [
                    create_rule(
                        "ph", ph_lower, ph_upper, PUMP_PH_UP_TOPIC, PUMP_PH_DOWN_TOPIC
                    ),
                    create_rule(
                        "ec", ec_lower, ec_upper, PUMP_NUTRIENT_TOPIC, PUMP_WATER_TOPIC
                    ),
                ]
                + create_temperature_and_humidity_rules(humidity_lower, humidity_upper, temperature_lower, temperature_upper)
                + create_floater_rule(),
                "light_hours": create_light_rule(light_hours_start, light_hours_end),
            }

            plants_data.append(plant_rules)

    return json.dumps(plants_data, indent=4)