from fastapi.responses import JSONResponse
from fastapi import APIRouter
from utils.logger import logger
from backend.app.services import homeassistant_service
from models.automation import Automation

router = APIRouter()

@router.post("/automation/{name}")
async def create_aumation(automation: Automation, name: str):
    try:
        automationResult, existed = await homeassistant_service.create_automation(automation, name)
        return JSONResponse(status_code= 200 if existed else 201, content=automationResult)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to create automation {str(e)}"})
