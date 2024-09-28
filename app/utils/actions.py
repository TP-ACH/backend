from enum import Enum
from controllers.mqtt_controller import mqtt_client
from controllers.alerts_controller import create_new_alert
from models.alert import DBAlert
from utils.alerts import Topic

class Action(Enum):
    MQTT = "mqtt"
    ALERT = "alert"
    
    def execute(self, device_id, action, reading: float, bound: float):
        if self == Action.MQTT:
            return self._execute_mqtt(device_id, action, reading, bound)
        elif self == Action.ALERT:
            return self._execute_alert(device_id, action, reading, bound)
    
    def _execute_mqtt(self, device_id, action, reading: float, bound: float):
        print(f"Sending MQTT message to {action.dest}. Reading: {reading}, Bound: {bound}")
        message = f"{device_id};{reading}"
        mqtt_client.publish_message(action.dest, message)

    def _execute_alert(self, device_id, action, reading: float, bound: float):
        print(f"Sending alert to {action.dest}. Reading: {reading}, Bound: {bound}")
        create_new_alert(DBAlert.from_topic(device_id, Topic(action.dest.lower)))