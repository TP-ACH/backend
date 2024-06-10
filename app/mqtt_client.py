import time
import asyncio
import datetime
import paho.mqtt.client as mqtt

from logger import logger
# from database import data_collection

logger = logger.getChild("mqtt_client")

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code.is_failure:
        logger.error(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
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
    # data_collection = database.get_collection("temperature")
    # # Save data to MongoDB
    # data_entry = {
    #     "device_id": 32,
    #     "reading": msg.payload,
    #     "timestamp": datetime.datetime.now()
    # }
    # data_collection.insert_one(data_entry)

def start_mqtt_client():
    while True:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='fastapi-mqtt')
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_subscribe = on_subscribe
            client.username_pw_set("test", "test")
            logger.info("Connecting to broker")
            client.connect("yuyo-mqtt5", 1883, 60)
            client.loop_forever()
            break
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying
