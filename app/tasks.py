import os
import sys
from celery_app import celery_app
import paho.mqtt.client as mqtt
from utils.logger import logger

sys.path.append(os.getcwd())
MQTT_USER = os.getenv("CELERY_MQTT_USER")
MQTT_PASSWORD = os.getenv("CELERY_MQTT_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))


@celery_app.task
def send_message():
    mqtt_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi-mqtt"
    )
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    res = mqtt_client.publish("actuators/pumps/ph_down", "test")
    res.wait_for_publish(15)

    if res.rc == mqtt.MQTT_ERR_SUCCESS:
        return "Message published successfully"
    else:
        logger.error("Failed to publish message")
