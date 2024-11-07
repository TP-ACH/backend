from enum import Enum
from clients.alerts_client import sync_create_new_alert
from controllers.mqtt_controller import mqtt_client
from models.alert import DBAlert
from utils.alerts import Topic
from utils.logger import logger


class Action(Enum):
    MQTT = "mqtt"
    ALERT = "alert"

    def execute(self, device_id, sensor, action, reading: float, bound: float):
        if self == Action.MQTT:
            return self._execute_mqtt(device_id, sensor, action, reading, bound)
        elif self == Action.ALERT:
            return self._execute_alert(device_id, action, reading, bound)

    def _execute_mqtt(self, device_id, sensor, action, reading: float, bound: float):
        topic = f"{device_id}/{action.dest}"
        logger.info(
            f"Sending MQTT message to {topic}. Reading: {reading}, Bound: {bound}"
        )
        mqtt_client.publish_message(topic, reading)
        logger.info(f"Creating alert for {device_id} of type {sensor}_ok")
        sync_create_new_alert(DBAlert.from_topic(device_id, Topic(f"{sensor}_ok")))

    def _execute_alert(self, device_id, action, reading: float, bound: float):
        logger.info(
            f"Sending alert to {action.dest}. Reading: {reading}, Bound: {bound}"
        )
        sync_create_new_alert(DBAlert.from_topic(device_id, Topic(action.dest.rsplit('/', 1)[-1].lower())))
