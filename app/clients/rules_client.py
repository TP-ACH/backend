import json

from clients.mongodb_client import get_device_rules
from clients.mongodb_client import get_species_defaults
from clients.mongodb_client import insert_species_defaults
from clients.mongodb_client import update_rules_by_device
from models.rule import DefaultRuleBySpecies
from models.rule import RulesByDevice
from utils.logger import logger
from utils.species import Species


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
