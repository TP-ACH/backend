from fastapi import APIRouter, Depends, status
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
from typing import List


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_alerts(
    device_id: str = None, type: Type = None, status: Status = None, topic: Topic = None
) -> List[Alert]:
    """Get all alerts or filter by device_id, type, status or topic."""
    return await get_alerts_with_message(device_id, type, status, topic)


@router.post("/")
async def create_alert(alert: DBAlert) -> Alert:
    """Create a new alert for a given device."""
    return await create_new_alert(alert)


@router.put("/")
async def change_alert_status(id: str, new_status: Status):
    """Change the status of an existing alert."""
    result = await update_alert_status(id, status=new_status)
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"No alert found with id {id}"},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Alert updated successfully"},
    )


@router.delete("/")
async def remove_alert(id: str):
    """Delete an alert by id."""
    result = await delete_alert(id)
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"No alert found with id {id}"},
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Alert deleted successfully"},
    )
