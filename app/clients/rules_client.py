from models.rule import Action, Rule, RuleBySensor, DefaultRuleBySpecies, RulesByDevice
from utils.species import Species
import json
from utils.logger import logger
from clients.mongodb_client import insert_species_defaults, get_default_rules


async def set_default_rules(device_id: str, species: Species):
    try:
        with open('default_rules.json', 'r') as file:
            data = json.load(file)
            species_defaults = []
            for species_rules in data:
                species_defaults.append(DefaultRuleBySpecies(**species_rules))
                
            await insert_species_defaults(species_defaults)
            
            species_rules = next((entry for entry in data if entry['species'] == species.value), None)
            if species_rules is not None:
                logger.info(f"Aplicando reglas para {species.value} al dispositivo {device_id}")
                
                default_rule = DefaultRuleBySpecies(**species_rules)
                
                rules = RulesByDevice(
                    device=device_id,
                    rules_by_sensor=default_rule.rules_by_sensor,
                    light_hours=default_rule.light_hours,
                )
                logger.info(rules)
                return rules
            else:
                logger.error(f"No se encontraron reglas para la especie: {species.value}")
    except FileNotFoundError:
        logger.error("El archivo 'default_rules.json' no se encontro.")
    except json.JSONDecodeError:
        logger.error("Error al decodficar el archivo JSON.")
        
        
async def set_device_rules(device_id: str, species: Species):
    rules = await get_default_rules(species.value)
    return rules