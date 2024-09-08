from models.rule import Action, Rule, RuleBySensor, DefaultRuleBySpecies, RulesByDevice
from utils.species import Species
import json
from utils.logger import logger
from clients.mongodb_client import insert_species_defaults, get_default_rules


async def set_default_rules(species: Species):
    try:
        with open('default_rules.json', 'r') as file:
            data = json.load(file)
            species_defaults = [DefaultRuleBySpecies(**species_rules) for species_rules in data]
                
            await insert_species_defaults(species_defaults)
            
            logger.info("Reglas predeterminadas cargadas correctamente.")

    except FileNotFoundError:
        logger.error("El archivo 'default_rules.json' no se encontro.")
    except json.JSONDecodeError:
        logger.error("Error al decodficar el archivo JSON.")
        
        
async def set_device_rules(device_id: str, species: Species):
    rules = await get_default_rules(species.value)
    return rules