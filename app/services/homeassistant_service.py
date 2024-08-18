from clients.homeassistant_client import post_automation
from exceptions.not_found_exception import NotFoundException
from models.model_type import ModelType
from models.sensors import Sensors
from utils.logger import logger
from clients.mongodb_client import get_ha_data_by_model, add_ha_data_by_model
from models import automation, template, rest_command, script
from validators.automations_validator import validate


async def create_automation(automation: automation.Automation, name: str):
    automation.alias = name
    logger.info(f"checking if automation: {automation.alias} exists already")
    existing = True
    try:
        automation_db = await get_ha_data_by_model(name, ModelType.automations)
        automation.id = automation_db._id
        logger.info(f"automation: {automation.alias} exists, updating automation")
    except NotFoundException as e:
        logger.info(f"automation: {automation.alias} does not exist, creating new automation")
        existing = False
        try:
            automation_db = await add_ha_data_by_model(automation, ModelType.automations)
            automation.id = automation_db._id
        except Exception as e:
            logger.error(f"Failed to create automation: {e}")
            raise e
    automation = await validate(automation)
    try:
        logger.info(f"posting automation: {automation}")
        result = await post_automation(automation)
    except Exception as e:
        logger.error(f"Failed to post automation: {e}")
        raise e
    return result, existing