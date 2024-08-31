from utils.species import Species
import json
from utils.logger import logger


def set_default_rules(device_id: str, species: Species):
    try:
        with open('default_rules.json', 'r') as file:
            data = json.load(file)
            species_rules = next((entry for entry in data if entry['species'] == species.value), None)
            if species_rules is not None:
                logger.info(f"Aplicando reglas para {species.value} al dispositivo {device_id}")
            else:
                logger.error(f"No se encontraron reglas para la especie: {species.value}")
    except FileNotFoundError:
        logger.error("El archivo 'default_rules.json' no se encontro.")
    except json.JSONDecodeError:
        logger.error("Error al decodficar el archivo JSON.")