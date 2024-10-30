import json
import pytz
import datetime
from bson import json_util
from fastapi import Response, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import List
from services.auth_service import get_current_user
from services.scheduler_service import sensors_heartbeat
from clients.mongodb_client import fetch_data, fetch_devices, validate_connection

from utils.logger import logger
from utils.consts import TIMEZONE

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.on_event("startup")
async def startup_event():
    sensors_heartbeat()
    try:
        await validate_connection()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")


@router.get("/devices")
async def get_devices() -> List[str]:
    """Get the list of the devices available."""
    devices = await fetch_devices()
    return Response(
        status_code=status.HTTP_200_OK, content=json.dumps(devices, default=json_util.default)
    )


@router.get("/{device_id}")
async def get_device_data(
    device_id: str,
    sensor: str | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> dict:
    """Get entries with the given filters for a specific device."""
    query = {}
    tz = pytz.timezone(TIMEZONE)
    if start_date:
        start_date = tz.localize(start_date).astimezone(pytz.utc)
        query["created_at"] = {"$gte": start_date}
    if end_date:
        end_date = tz.localize(end_date).astimezone(pytz.utc)
        if "created_at" in query:
            query["created_at"].update({"$lte": end_date})
        else:
            query["created_at"] = {"$lte": end_date}
    try:
        data_entries = await fetch_data(device_id, sensor, query)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"Failed to fetch data: {str(e)}"}
        )
    return Response(
        status_code=status.HTTP_200_OK, content=json.dumps(data_entries, default=json_util.default)
    )
