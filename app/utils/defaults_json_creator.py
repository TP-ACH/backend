import csv
import json
from utils.consts import PUMP_PH_DOWN_TOPIC, PUMP_PH_UP_TOPIC, PUMP_NUTRIENT_TOPIC, PUMP_WATER_TOPIC, SWITCH_LIGHT_TOPIC
from utils.alerts import Topic

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


def create_temperature_and_humidity_rules():
    return [
        {
            "sensor": "temperature",
            "rules": [
                {
                    "bound": 25,
                    "compare": "less",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.TEMPERATURE_DOWN.value},
                },
                {
                    "bound": 30,
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
                    "bound": 25,
                    "compare": "less",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.HUMIDITY_DOWN.value},
                },
                {
                    "bound": 30,
                    "compare": "greater",
                    "time": 5,
                    "enabled": 1,
                    "action": {"type": "alert", "dest": Topic.HUMIDITY_UP.value},
                },
            ],
        },
    ]


def process_csv_to_json(csv_file):
    plants_data = []

    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            species = row["species"]
            ph_lower = float(row["ph_lower"])
            ph_upper = float(row["ph_upper"])
            ec_lower = float(row["ec_lower"])
            ec_upper = float(row["ec_upper"])
            light_hours = int(row["light_hours"])

            plant_rules = {
                "species": species,
                "rules_by_sensor": [
                    create_rule("ph", ph_lower, ph_upper, PUMP_PH_UP_TOPIC, PUMP_PH_DOWN_TOPIC),
                    create_rule("ec", ec_lower, ec_upper, PUMP_NUTRIENT_TOPIC, PUMP_WATER_TOPIC),
                ]
                + create_temperature_and_humidity_rules(),
                "light_hours": light_hours,
            }

            plants_data.append(plant_rules)

    return json.dumps(plants_data, indent=4)


csv_file = "app/plants_defaults.csv"
json_data = process_csv_to_json(csv_file)

with open("plants_data.json", "w") as json_file:
    json_file.write(json_data)
