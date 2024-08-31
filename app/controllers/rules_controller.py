from fastapi import APIRouter
from utils.logger import logger
from clients.rules_client import set_default_rules
from models.template import Attribute
from utils.species import Species


router = APIRouter()

@router.post("/default")
async def set_default(device_id: str, species:Species):
    return set_default_rules(device_id, species)
