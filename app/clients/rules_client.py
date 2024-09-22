from models.rule import Action, Rule, RuleBySensor, DefaultRuleBySpecies, RulesByDevice
from utils.species import Species
import json
from utils.comparison import Comparison
from utils.logger import logger
from clients.mongodb_client import (
    insert_species_defaults,
    get_species_defaults,
    update_rules_by_device,
    get_device_rules,
    get_sensor_rules,
)
from utils.actions import Action

async def set_default_rules(species: Species):
    try:
        with open("default_rules.json", "r") as file:
            data = json.load(file)
            species_defaults = [
                DefaultRuleBySpecies(**species_rules) for species_rules in data
            ]

            await insert_species_defaults(species_defaults)

            logger.info("Default rules successfully set.")

    except FileNotFoundError:
        logger.error("File 'default_rules.json' was not found.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding the JSON file: {str(e)}")


async def get_default_species_rules(species: Species):
    rules = await get_species_defaults(species.value)
    if rules:
        return DefaultRuleBySpecies(**rules)
    logger.error(f"No default rules found for {species.value}")


async def add_device_rules(rules: RulesByDevice):
    return await update_rules_by_device(rules)


async def read_device_rules(device_id: str):
    rules = await get_device_rules(device_id)
    return RulesByDevice(**rules)


async def execute_sensor_rules(device_id: str, sensor: str, reading):
    rules = await get_sensor_rules(device_id, sensor)
    sensor_rules = RuleBySensor(**rules)
    
    for rule in sensor_rules.rules:
        if evaluate_rule(rule, reading):
            execute_action(rule.action, reading, rule.bound)
    
    return sensor_rules


def evaluate_rule(rule, reading: float) -> bool:
    return Comparison(rule.compare.lower()).compare(reading, rule.bound)
    # aca deberia ver si fallo la cantidad de veces necesarias para triggerearlo
    
    
def execute_action(action: Action, reading: float, bound: float):
    Action(action.type.lower()).execute(action, reading, bound)