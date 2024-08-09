from fastapi import Response, APIRouter
from fastapi.responses import JSONResponse
import datetime
from clients.mongodb_client import fetch_data
from utils.logger import logger
from clients.mongodb_client import validate_connection


router = APIRouter()


@router.on_event("startup")
async def startup_event():
    try:
        await validate_connection()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

@router.get("/{device_id}?start_date={start_date}&end_date={end_date}")
async def get_device_data(device_id: str,
                   start_date: datetime.date | None = None,
                   end_date: datetime.date | None = None):
    query = {}
    try:
        if start_date:
            start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            query["created_at"] = {"$gte": start_date}
        if end_date:
            end_date = datetime.datetime.combine(end_date, datetime.datetime.max.time())
            query["created_at"] = {"$lte": end_date}
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": f"Failed to parse dates: {str(e)}"})
    try:
        data_entries = await fetch_data(device_id, query)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to fetch data: {str(e)}"})
    return Response(status_code=200, content=data_entries)
