from fastapi import APIRouter
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
