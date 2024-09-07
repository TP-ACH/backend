from fastapi import APIRouter
from utils.logger import logger
from clients.rules_client import set_default_rules, set_device_rules
from models.template import Attribute
from utils.species import Species


router = APIRouter()

@router.post("/default")
async def set_default(device_id: str, species:Species):
    return await set_default_rules(device_id, species)

@router.get("/device")
async def set_default(device_id: str, species:Species):
    return await set_device_rules(device_id, species)