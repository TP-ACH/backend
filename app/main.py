from fastapi import FastAPI, Response
from database import validate_connection
from mqtt_client import MQTTClient
from consts import PUMP_PH_UP_TOPIC, PUMP_PH_DOWN_TOPIC, PUMP_NUTRIENT_TOPIC, \
    SWITCH_LIGHT_TOPIC
from logger import logger

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