from fastapi.responses import JSONResponse
from fastapi import APIRouter
from utils.logger import logger
from clients.homeassistant_client import get_homeassistant_config_files, modify_ph_threshold
from models.template import Attribute

router = APIRouter()

@router.get("/fetch_and_save_ha_files")
async def fetch_and_save():
    try:
        config_files = await get_homeassistant_config_files()
        return JSONResponse(status_code=200, content=config_files)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to fetch ha files {str(e)}"})
    
@router.post("/modify_threshold/ph")
async def modify_threshold_ph(attribute: Attribute):
    try:
        await modify_ph_threshold(attribute)
        return JSONResponse(status_code=200, content={"result": "Threshold modified successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to modify threshold {str(e)}"})
