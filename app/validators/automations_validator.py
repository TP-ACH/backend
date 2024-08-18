
from exceptions.not_found_exception import NotFoundException
from models.automation import Automation, Trigger
from clients.mongodb_client import get_ha_data_by_model
from models.model_type import ModelType


async def validate(automation: Automation):
    if automation.action.service is None or not automation.action.service.contains("script."):
        raise ValueError("action.service must be a script")
    try:
        await get_ha_data_by_model(automation.action.service.split(".")[1], ModelType.scripts)
    except NotFoundException as e:
        raise ValueError(f"script {automation.action.service} not found")
    automation.trigger = Trigger()
    automation.trigger.webhook_id = f"-{automation.id}"
    automation.action.data = {
                "reading": "{{ trigger.json.reading }}"
            }
    return automation