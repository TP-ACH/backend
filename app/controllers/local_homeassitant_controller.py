from fastapi.responses import JSONResponse
from fastapi import APIRouter
from utils.logger import logger
from backend.app.clients import local_homeassistant_client
from models.template import Attribute
from models.sensors import Sensors
from datetime import datetime

router = APIRouter()

@router.get("/fetch_and_save_ha_files")
async def fetch_and_save():
    try:
        config_files = await local_homeassistant_client.get_homeassistant_config_files()
        return JSONResponse(status_code=200, content=config_files)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to fetch ha files {str(e)}"})
    
@router.post("/modify_threshold/{sensor_name}")
async def modify_threshold(sensor_name: str, attribute: Attribute):
    logger.info(f"Modifying threshold for sensor {sensor_name}, upper: {attribute.upper}, lower: {attribute.lower}")
    try:
        match sensor_name:
            case Sensors.PH, Sensors.TEMPERATURE, Sensors.HUMIDITY, Sensors.ROOM_TEMPERATURE, Sensors.EC:
                await local_homeassistant_client.modify_threshold(sensor_name, attribute)
                return response()
            case Sensors.FLOATER:
                return JSONResponse(status_code=400, content={"message": "floater threshold cant be modified"})
            case _:
                return JSONResponse(status_code=400, content={"message": f"Sensor {sensor_name} not supported"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to modify threshold {str(e)}"})

    
@router.post("/modify_light_cycle")
async def modify_light_cycle(cycle: datetime.time):
    try:
        await local_homeassistant_client.modify_light_cycle(cycle)
        return response()
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to modify light cycle {str(e)}"})

def response():
    return JSONResponse(status_code=200, content={"result": "Threshold modified successfully"})