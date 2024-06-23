import os
import time
import json
import asyncio
import datetime
import paho.mqtt.client as mqtt

from logger import logger
from consts import TEMP_TOPIC, PH_TOPIC, EC_TOPIC
from database import get_collection

logger = logger.getChild("mqtt_client")

MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code.is_failure:
        logger.error(f"Failed to connect: {reason_code}. Retrying in 5 seconds")
    else:
        logger.info("Connected to broker")
        client.subscribe(TEMP_TOPIC)
        client.subscribe(PH_TOPIC)
        client.subscribe(EC_TOPIC)

def on_subscribe(client, userdata, mid, reason_code_list, properties=None):
    if reason_code_list[0].is_failure:
        logger.error(f"Failed to subscribe: {reason_code_list[0]}")
    else:
        logger.info('Successfully subscribed to topic')


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    sensor = msg.topic.split("/")[1]
    logger.info(f"Received message from {sensor}: {payload}")
    data_collection = get_collection(sensor)
    data_entry = {
        "device_id": 32,
        "reading": payload,
        "timestamp": datetime.datetime.now()
    }
    data_collection.insert_one(data_entry)


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='fastapi-mqtt')

    def start_mqtt_client(self):
        while True:
            try:
                self.client.on_connect = on_connect
                self.client.on_message = on_message
                self.client.on_subscribe = on_subscribe
                self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
                self.client.connect(MQTT_HOST, MQTT_PORT, 60)
                self.client.loop_start()
                break
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                time.sleep(5)  # Wait for 5 seconds before retrying
    
    def publish_message(self, topic, message):
        res = self.client.publish(topic, message)
        res.wait_for_publish(15)
        if res.rc == mqtt.MQTT_ERR_SUCCESS:
            return True
        return False
