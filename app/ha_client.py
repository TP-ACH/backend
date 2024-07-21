import os
import requests
import json
import yaml


from ruamel.yaml import YAML
from logger import logger
from database import insert_ha_data
from models import automation, configuration

HA_BASE_URL = os.getenv("HA_URL")
ya = YAML()
ya.preserve_quotes = True


HEADERS = {
    "Content-Type": "application/json"
}
def send_to_ha(device_id: str, sensor: str, reading: float):
    HA_TOPIC = {}
    try:
        with open('ha_endpoints.json', 'r') as file:
            HA_TOPIC = json.load(file)
            logger.info(f"ha topic endpoints: {HA_TOPIC}");
    except Exception as e:
        logger.error(f"error reading json file with HA endpoints");
    try:
        # Construct the URL
        url = HA_BASE_URL + HA_TOPIC[sensor]

        # Log the request information
        logger.info(f"sending request for topic: {sensor} to HA at url: {url}")

        # Prepare the payload
        payload = {
            "reading": reading
        }

        # Send the POST request
        response = requests.post(url, json=payload, headers=HEADERS)

        # Log the response status
        logger.info(f"Received response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")

    except Exception as e:
        logger.error(f"Something went wrong when sending to HA: {str(e)}")

async def get_automation_file():
    logger.info("Gettin automations from Home Assistant container")
    with open('../config/automations.yaml', 'r') as f:
        contents = f.read()
    data = yaml.safe_load(contents)
    automations = [automation.Automation(**item) for item in data]
    
    # Convert to JSON and save to MongoDB
    automation_json = [automation.model_dump() for automation in automations]
    logger.info("Saving automations to MongoDB")
    try:
        await insert_ha_data("homeassistant", "automations", automation_json)
    except Exception as e:
        logger.error(f"Failed to save automations to MongoDB: {e}")
    for val in automation_json:
        val.pop("_id")
    return automation_json

async def get_configuration_file():
    logger.info("Getting configuration.yaml file from Home Assistant container")
    with open('../config/configuration.yaml', 'r') as file:
        yaml_content = ya.load(file)
    # Convert to JSON and save to MongoDB
    configurations_json = [configuration.Configuration(**yaml_content).model_dump()]
    logger.info("Saving automations to MongoDB")
    try:
        await insert_ha_data("homeassistant", "configurations", configurations_json)
    except Exception as e:
        logger.error(f"Failed to save configurations to MongoDB: {e}")
    for val in configurations_json:
        val.pop("_id")
    return configurations_json
