import os
import yaml

from datetime import datetime
from models.sensors import Sensors
from utils.logger import logger
from clients.mongodb_client import insert_ha_data
from models import automation, template, rest_command, script

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
        await insert_ha_data("scripts", script_json)
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


async def modify_threshold(sensor_name: str, attribute: template.Attribute):
    logger.info(f"Modifying threshold for sensor {sensor_name}, upper: {attribute.upper}, lower: {attribute.lower}")
    templates = await get_template_file()
    for t in templates:
        for sensor in t.sensor:
            if sensor.name == sensor_name:
                sensor.attributes.upper = attribute.upper
                sensor.attributes.lower = attribute.lower
    data = [template.model_dump() for template in templates]
    logger.info("Saving modified templates to Home Assistant")
    with open('../config/templates.yaml', 'w') as f:
        yaml.dump(data, f)

async def modify_light_cycle(cycle: datetime.time):
    logger.info(f"Modifying light cycle to {cycle.strftime('%H:%M:%S')}")
    templates = await get_template_file()
    for t in templates:
        for sensor in t.sensor:
            if sensor.name == Sensors.LIGHT:
                sensor.state = cycle.strftime("%H:%M:%S")
    data = [template.model_dump() for template in templates]
    logger.info("Saving modified templates to Home Assistant")
    with open('../config/templates.yaml', 'w') as f:
        yaml.dump(data, f)

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
        await insert_ha_data("automations", automation_json)
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
        await insert_ha_data("templates", template_json)
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
        await insert_ha_data("rest_commands", rest_command_json)
    except Exception as e:
        logger.error(f"Failed to save rest_commands to MongoDB: {e}")
    for val in rest_command_json:
        val.pop("_id")
    return rest_commands