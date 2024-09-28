import json


from clients.mongodb_client import get_sensor_rules
from clients.mongodb_client import get_device_rules
from clients.mongodb_client import get_species_defaults
from clients.mongodb_client import insert_species_defaults
from clients.mongodb_client import update_rules_by_device
from models.rule import DefaultRuleBySpecies
from models.rule import Rule
from models.rule import RuleBySensor
from models.rule import RulesByDevice
from utils.actions import Action
from utils.comparison import Comparison
from utils.logger import logger
from utils.species import Species


rule_failure_counts = {}

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
        if evaluate_rule(device_id, sensor, rule, reading):
            await execute_action(device_id, rule.action, reading, rule.bound)
    
    return sensor_rules


def evaluate_rule(device_id: str, sensor:str, rule: Rule, reading: float) -> bool:
    global rule_failure_counts
    
    out_of_bounds = Comparison(rule.compare.lower()).compare(reading, rule.bound)
    
    rule_key = (device_id, sensor, rule.bound, rule.compare)
        
    if rule_key not in rule_failure_counts:
        rule_failure_counts[rule_key] = 0
    
    if out_of_bounds:
        rule_failure_counts[rule_key] += 1
        logger.info(f"Reading out of bounds. Counter for {rule_key}: {rule_failure_counts[rule_key]}")
        
        if rule_failure_counts[rule_key] >= rule.time:
            rule_failure_counts[rule_key] = 0
            return True
    else:
        rule_failure_counts[rule_key] = 0
        
    return False    
    
async def execute_action(device_id, action: Action, reading: float, bound: float):
    await Action(action.type.lower()).execute(device_id, action, reading, bound)