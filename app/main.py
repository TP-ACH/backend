from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import datetime
from database import validate_connection, fetch_data
from mqtt_client import MQTTClient
from consts import PUMP_PH_UP_TOPIC, PUMP_PH_DOWN_TOPIC, PUMP_NUTRIENT_TOPIC, \
    SWITCH_LIGHT_TOPIC, PUMP_WATER_TOPIC
from logger import logger
from ha_client import get_automation_file, get_configuration_file

app = FastAPI()
mqtt_client = MQTTClient()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting MQTT client")
    mqtt_client.start_mqtt_client()
    try:
        await validate_connection()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping MQTT client")
    mqtt_client.client.loop_stop()
    mqtt_client.client.disconnect()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/{device_id}")
async def get_device_data(device_id: str,
                   start_date: datetime.date | None = None,
                   end_date: datetime.date | None = None):
    query = {}
    if start_date:
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        query["created_at"] = {"$gte": start_date}
    if end_date:
        end_date = datetime.datetime.combine(end_date, datetime.datetime.max.time())
        query["created_at"] = {"$lte": end_date}
    
    data_entries = await fetch_data(device_id, query)
    return data_entries


@app.get("/actuator/ph_up")
def ph_up():
    if mqtt_client.client.publish(PUMP_PH_UP_TOPIC, 1):
        return Response(status_code=200, content="OK")
    return Response(status_code=500, content="Failed to publish message")

@app.get("/actuator/ph_down")
def ph_down():
    if mqtt_client.client.publish(PUMP_PH_DOWN_TOPIC, 1):
        return Response(status_code=200, content="OK")
    return Response(status_code=500, content="Failed to publish message")

@app.get("/actuator/nutrient_up")
def nutrient_up():
    if mqtt_client.client.publish(PUMP_NUTRIENT_TOPIC, 1):
        return Response(status_code=200, content="OK")
    return Response(status_code=500, content="Failed to publish message")

@app.get("/switch_light")
def switch_light():
    if mqtt_client.client.publish(SWITCH_LIGHT_TOPIC, 1):
        return Response(status_code=200, content="OK")
    return Response(status_code=500, content="Failed to publish message")

@app.post("/water_on")
def water_on():
    if mqtt_client.client.publish(PUMP_WATER_TOPIC, 1):
        return Response(status_code=200, content="OK")
    return Response(status_code=500, content="Failed to publish message")


@app.get("/fetch_and_save_ha_files")
async def fetch_and_save():
    try:
        automation = await get_automation_file()
        configuration = await get_configuration_file()
        # rompe al devovler pero guarda ni idea
        print({"automations": automation, "configurations": configuration})
        return JSONResponse(status_code=200, content={"automations": automation, "configurations": configuration})
    except Exception as e:
        return Response(status_code=500, content=f"Failed to fetch ha files {e}")
