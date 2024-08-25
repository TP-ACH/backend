import os
import requests
import json
import yaml
import httpx

from utils.logger import logger
from urllib.parse import urlencode
from clients.mongodb_client import insert_ha_data
from models import automation, template, rest_command, script

HA_BASE_URL = os.getenv("HA_URL")
HA_AUTH_URL = os.getenv("HA_AUTH_URL")
HA_TOKEN_URL = os.getenv("HA_TOKEN_URL")

HEADERS = {
    "Content-Type": "application/json"
}
def send_to_ha(device_id: str, sensor: str, reading: float):
    HA_TOPIC = {}
    try:
        with open('ha_endpoints.json', 'r') as file:
            HA_TOPIC = json.load(file)
            logger.info(f"ha topic endpoints: {HA_TOPIC}")
    except Exception as e:
        logger.error(f"error reading json file with HA endpoints")
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
    logger.info("Getting automations from Home Assistant container")
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
    return automations

async def get_template_file():
    logger.info("Getting templates.yaml file from Home Assistant container")
    with open('../config/templates.yaml', 'r') as f:
        contents = f.read()
    data = yaml.safe_load(contents)
    templates = [template.Template(**item) for item in data]
    
    # Convert to JSON and save to MongoDB
    template_json = [template.model_dump() for template in templates]
    logger.info("Saving templates to MongoDB")
    try:
        await insert_ha_data("homeassistant", "templates", template_json)
    except Exception as e:
        logger.error(f"Failed to save templates to MongoDB: {e}")
    for val in template_json:
        val.pop("_id")
    return templates


async def get_rest_command_file():
    logger.info("Getting rest_commands.yaml file from Home Assistant container")
    with open('../config/rest_commands.yaml', 'r') as f:
        contents = f.read()
    data = yaml.safe_load(contents)
    rest_commands = []
    for item in data:
        rc = rest_command.RestCommand(**item)
        for key in item.keys():
            if item[key] is None:
                rc.alias = key
        rest_commands.append(rc)
    
    # Convert to JSON and save to MongoDB
    rest_command_json = [rest_command.model_dump() for rest_command in rest_commands]
    logger.info("Saving templates to MongoDB")
    try:
        await insert_ha_data("homeassistant", "rest_commands", rest_command_json)
    except Exception as e:
        logger.error(f"Failed to save rest_commands to MongoDB: {e}")
    for val in rest_command_json:
        val.pop("_id")
    return rest_commands


async def get_script_file():
    logger.info("Getting script.yaml file from Home Assistant container")
    with open('../config/scripts.yaml', 'r') as f:
        contents = f.read()
    data = yaml.safe_load(contents)
    scrpts = []
    for key, value in data.items():
        s = script.Script(**value)
        s.alias = key
        scrpts.append(s)
    # Convert to JSON and save to MongoDB
    script_json = [s.model_dump() for s in scrpts]
    logger.info("Saving templates to MongoDB")
    try:
        await insert_ha_data("homeassistant", "scripts", script_json)
    except Exception as e:
        logger.error(f"Failed to save scripts to MongoDB: {e}")
    for val in script_json:
        val.pop("_id")
    return scrpts

async def get_homeassistant_config_files():
    automations = [a.model_dump() for a in await get_automation_file()]
    templates = [t.model_dump() for t in await get_template_file()]
    rest_commands = [r.model_dump() for r in await get_rest_command_file()]
    scripts = [s.model_dump() for s in await get_script_file()]
    return [automations, templates, rest_commands, scripts]


async def modify_ph_threshold(attribute: template.Attribute):
    logger.info("Modifying PH threshold in Home Assistant to upper: {attribute.upper} and lower: {attribute.lower}")
    templates = await get_template_file()
    for t in templates:
        for sensor in t.sensor:
            if sensor.name == "ph":
                sensor.attributes.upper = attribute.upper
                sensor.attributes.lower = attribute.lower
    data = [template.model_dump() for template in templates]
    logger.info("Saving modified templates to Home Assistant")
    with open('../config/templates.yaml', 'w') as f:
        yaml.dump(data, f)
        
async def get_login_request(redirect_uri: str, client_id: str):
    query_params = urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read",
    })
    return f"{HA_AUTH_URL}?{query_params}"

async def get_token_request(redirect_uri: str, client_id: str, code: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    return {
        "url": HA_TOKEN_URL,
        "kwargs": {
            "headers": headers,
            "data": data,
        },
    }

async def def_access_token_response(redirect_uri: str, client_id: str, code: str):
    req = await get_token_request(redirect_uri, client_id, code)

    async with httpx.AsyncClient() as client:
        response = await client.post(req["url"], **req["kwargs"])
        
        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"message": response.text})

        access_token = response.json()['access_token']
        logger.info("Access token retrieved successfully")
        return JSONResponse(status_code=200, content={"access_token": access_token})
    