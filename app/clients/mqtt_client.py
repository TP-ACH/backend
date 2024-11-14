import os
import time
import json
import paho.mqtt.client as mqtt

from utils.logger import logger
from utils.consts import TEMP_TOPIC, PH_TOPIC, EC_TOPIC, FLOATER_TOPIC, HUMIDITY_TOPIC
from utils.utils import value_in_range
from clients.mongodb_client import insert_data


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
        client.subscribe(TEMP_TOPIC, qos=1)
        client.subscribe(HUMIDITY_TOPIC, qos=1)
        client.subscribe(PH_TOPIC, qos=1)
        client.subscribe(EC_TOPIC, qos=1)
        client.subscribe(FLOATER_TOPIC, qos=1)


def on_subscribe(client, userdata, mid, reason_code_list, properties=None):
    if reason_code_list[0].is_failure:
        logger.error(f"Failed to subscribe: {reason_code_list[0]}")
    else:
        logger.info("Successfully subscribed to topic")


def on_message(client, userdata, msg):
    try:
        device_id = msg.topic.split("/")[0]
        sensor = msg.topic.split("/")[2]
        data = json.loads(msg.payload.decode("utf-8"))

        reading = float(data.get("reading", None))
        if device_id and reading is not None and value_in_range(sensor, reading):
            logger.info(
                f"Received message from topic: {sensor}, device: {device_id} and reading: {reading}"
            )
            insert_data(device_id, sensor, reading)

            from clients.rules_client import execute_sensor_rules

            executed = execute_sensor_rules(device_id, sensor, reading)
            if not executed:
                logger.error(f"No rules executed for {device_id} and {sensor}")

        else:
            logger.error(f"Invalid message received: {data}")

    except ValueError:
        logger.error(f"Failed to convert reading to float")
    except Exception as e:
        logger.error(f"Something went wrong, data received: {msg.payload}")
        logger.error(f"Error: {e.with_traceback()}")


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi-mqtt"
        )

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
                time.sleep(5)

    def publish_message(self, topic, message, qos=1):
        self.client.publish(topic, message, qos=qos)
