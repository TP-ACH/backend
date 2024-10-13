from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from utils.species import Species
from models.rule import RulesByDevice, DefaultRuleBySpecies
from services.auth_service import get_current_user
from typing import List
from clients.rules_client import (
    init_species_rules,
    get_default_species_rules,
    add_device_rules,
    read_device_rules,
)


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/default")
async def init_rules():
    if await init_species_rules():
        return JSONResponse(
            status_code=200, content={"message": "Default rules set successfully"}
        )
    return JSONResponse(
        status_code=500, content={"message": "Error setting default rules"}
    )


@router.get("/default", response_model=DefaultRuleBySpecies)
async def get_default_rules(species: Species):
    rules = await get_default_species_rules(species)
    if not rules:
        return JSONResponse(
            status_code=404,
            content={"message": f"No default rules found for {species.value}"},
        )
    return rules


@router.put("/device")
async def add_device_rule(rules: RulesByDevice):
    update = await add_device_rules(rules)
    if update:
        return JSONResponse(
            status_code=200, content={"message": "Rules updated successfully"}
        )
    return JSONResponse(
        status_code=500,
        content={"message": f"Error updating rules for device {rules.device}"},
    )


@router.get("/device", response_model=RulesByDevice)
async def get_device_rules(device_id: str):
    rules = await read_device_rules(device_id)
    if not rules:
        return JSONResponse(
            status_code=404,
            content={"message": f"No rules found for device {device_id}"},
        )
    return rules

@router.get("/species", response_model=List[Species])
async def get_species():
    return JSONResponse(
        status_code=200, content={"species": [species.value for species in Species]}
    )