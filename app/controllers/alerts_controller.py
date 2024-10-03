from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from utils.alerts import Type, Status, Topic
from models.alert import Alert, DBAlert
from clients.mongodb_client import delete_alert
from clients.alerts_client import (
    create_new_alert,
    update_alert_status,
    get_alerts_with_message,
)
from services.auth_service import get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_alerts(
    device_id: str = None, type: Type = None, status: Status = None, topic: Topic = None
):
    return get_alerts_with_message(device_id, type, status, topic)


@router.post("/")
async def create_alert(alert: DBAlert):
    return create_new_alert(alert)


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


@router.delete("/")
async def remove_alert(id: str):
    result = await delete_alert(id)
    if not result:
        return JSONResponse(
            status_code=404,
            content={"message": f"No alert found with id {id}"},
        )
    return JSONResponse(
        status_code=200, content={"message": "Alert deleted successfully"}
    )
