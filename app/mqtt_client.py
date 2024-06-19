import os
import time
import asyncio
import datetime
import paho.mqtt.client as mqtt

from main import validator
from logger import logger
from database import get_collection

logger = logger.getChild("mqtt_client")

MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='fastapi-mqtt')


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code.is_failure:
        logger.error(f"Failed to connect: {reason_code}. Retrying in 5 seconds")
    else:
        logger.info("Connected to broker")
        client.subscribe("sensors/#")


def on_subscribe(client, userdata, mid, reason_code_list, properties=None):
    if reason_code_list[0].is_failure:
        logger.error(f"Failed to subscribe: {reason_code_list[0]}")
    else:
        logger.info("Subscribed to sensors/#")


def on_message(client, userdata, msg):
    logger.info(msg.topic + " " + str(msg.payload))
    data_collection = get_collection("temperature")
    # Save data to MongoDB
    data_entry = {
        "device_id": 32,
        "reading": msg.payload,
        "timestamp": datetime.datetime.now()
    }
    data_collection.insert_one(data_entry)
    # validator.validate(data_entry)


def publish_message(topic, message):
    logger.info(f"Publishing message to {topic}: {message}")
    mqtt_client.publish(topic, message)


def start_mqtt_client():
    while True:
        try:
            mqtt_client.on_connect = on_connect
            mqtt_client.on_message = on_message
            mqtt_client.on_subscribe = on_subscribe
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
            mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
            mqtt_client.loop_start()
            break
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying
