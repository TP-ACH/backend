from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from utils.species import Species
from utils.logger import logger
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

@router.get("/default")
async def get_default_rules(species: Species) -> DefaultRuleBySpecies:
    """Get the default rules for a given species."""
    rules = await get_default_species_rules(species)
    if not rules:
        logger.info(f"No rules found for {species.value}. Initializing default rules.")
        if await init_species_rules():
            rules = await get_default_species_rules(species)
            if not rules:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"message": f"No default rules found for {species.value}"},
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Error setting default rules"},
            )
    return rules


@router.put("/device")
async def add_device_rule(rules: RulesByDevice):
    """Add or update rules for a device."""
    update = await add_device_rules(rules)
    if update:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Rules updated successfully"},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": f"Error updating rules for device {rules.device}"},
    )


@router.get("/device", response_model=RulesByDevice)
async def get_device_rules(device_id: str):
    """Get all the rules set for the given device."""
    rules = await read_device_rules(device_id)
    if not rules:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"No rules found for device {device_id}"},
        )
    return rules


@router.get("/species")
async def get_species() -> List[Species]:
    """Get all the species available."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"species": [species.value for species in Species]},
    )
