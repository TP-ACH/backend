from fastapi import Response, APIRouter
from fastapi.responses import JSONResponse
from utils.consts import PUMP_PH_UP_TOPIC, PUMP_PH_DOWN_TOPIC, PUMP_NUTRIENT_TOPIC, \
    SWITCH_LIGHT_TOPIC, PUMP_WATER_TOPIC
from utils.logger import logger
from clients.mqtt_client import MQTTClient

router = APIRouter()


mqtt_client = MQTTClient()

@router.on_event("startup")
async def startup_event():
    logger.info("Starting MQTT client")
    mqtt_client.start_mqtt_client()

@router.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping MQTT client")
    mqtt_client.client.loop_stop()
    mqtt_client.client.disconnect()


@router.get("/actuator/ph_up")
def ph_up():
    if mqtt_client.publish(PUMP_PH_UP_TOPIC, 1):
        return Response(status_code=200, content={"result": "OK"})
    return JSONResponse(status_code=500, content={"message": "Failed to publish message"})

@router.get("/actuator/ph_down")
def ph_down():
    if mqtt_client.publish(PUMP_PH_DOWN_TOPIC, 1):
        return Response(status_code=200, content={"result": "OK"})
    return JSONResponse(status_code=500, content={"message": "Failed to publish message"})

@router.get("/actuator/nutrient_up")
def nutrient_up():
    if mqtt_client.publish(PUMP_NUTRIENT_TOPIC, 1):
        return Response(status_code=200, content={"result": "OK"})
    return JSONResponse(status_code=500, content={"message": "Failed to publish message"})

@router.get("/switch_light")
def switch_light():
    if mqtt_client.publish(SWITCH_LIGHT_TOPIC, 1):
        return Response(status_code=200, content={"result": "OK"})
    return JSONResponse(status_code=500, content={"message": "Failed to publish message"})

@router.post("/water_on")
def water_on():
    if mqtt_client.publish(PUMP_WATER_TOPIC, 1):
        return Response(status_code=200, content={"result": "OK"})
    return JSONResponse(status_code=500, content={"message": "Failed to publish message"})

