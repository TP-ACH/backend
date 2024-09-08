from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.logger import logger
from clients.rules_client import set_default_rules, get_default_species_rules
from models.template import Attribute
from utils.species import Species


router = APIRouter()

@router.post("/default")
async def set_default(species:Species):
    return await set_default_rules(species)

@router.get("/default")
async def get_default_rules(species:Species):
    rules = await get_default_species_rules(species)
    if not rules:
        return JSONResponse(status_code=500, content={"message": f"No default rules found for {species.value}"})
    return rules