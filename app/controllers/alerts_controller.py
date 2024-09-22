from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from utils.alerts import Type, Status
from models.alert import Alert
from clients.mongodb_client import read_alerts, insert_alert
from services.auth_service import get_current_user


# router = APIRouter(dependencies=[Depends(get_current_user)])
router = APIRouter()

@router.get("/")
async def get_alerts(type: Type = None, status: Status = None):
    return await read_alerts(type, status)

@router.post("/")
async def create_alert(alert: Alert):
    return await insert_alert(alert)