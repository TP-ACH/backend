
from backend.app.exceptions.not_found_exception import NotFoundException
from backend.app.models.automation import Automation, Trigger
from backend.app.clients.mongodb_client import get_ha_data_by_model
from backend.app.models.model_type import ModelType


async def validate(automation: Automation):
    if automation.action is None:
        raise ValueError("action is required")
    automation.trigger = Trigger()
    automation.trigger.webhook_id = f"-{automation.id}"
    automation.action.data = {
                "reading": "{{ trigger.json.reading }}"
            }
    if automation.action.service is None or not automation.action.service.contains("script."):
        raise ValueError("action.service must be a script")
    try:
        await get_ha_data_by_model(automation.action.service.split(".")[1], ModelType.scripts)
    except NotFoundException as e:
        raise ValueError(f"script {automation.action.service} not found")
    return automation