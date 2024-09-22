from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from utils.alerts import Type, Status
from models.alert import Alert
from clients.mongodb_client import read_alerts
from clients.alerts_client import create_new_alert, update_alert_status
from services.auth_service import get_current_user


# router = APIRouter(dependencies=[Depends(get_current_user)])
router = APIRouter()

@router.get("/")
async def get_alerts(device_id: str = None, type: Type = None, status: Status = None):
    return await read_alerts(device_id, type, status)

@router.post("/")
async def create_alert(alert: Alert):
    return await create_new_alert(alert)

@router.put("/")
async def change_alert_status(id: str, status: Status):
    result = await update_alert_status(id, status=status)
    if not result:
        return JSONResponse(
            status_code=404,
            content={"message": f"No alert found with id {id}"},
        )
    return JSONResponse(
            status_code=200, content={"message": "Alert updated successfully"}
        )