import json
import pytz
import datetime
from bson import json_util
from fastapi import Response, APIRouter, Depends
from fastapi.responses import JSONResponse

from services.auth_service import get_current_user
from clients.mongodb_client import fetch_data, validate_connection

from utils.logger import logger
from utils.consts import TIMEZONE

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.on_event("startup")
async def startup_event():
    try:
        await validate_connection()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")


@router.get("/{device_id}")
async def get_device_data(
    device_id: str,
    sensor: str | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
):
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
            status_code=500, content={"message": f"Failed to fetch data: {str(e)}"}
        )
    return Response(
        status_code=200, content=json.dumps(data_entries, default=json_util.default)
    )
