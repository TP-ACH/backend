from enum import Enum
from controllers.mqtt_controller import mqtt_client

class Action(Enum):
    MQTT = "mqtt"
    ALERT = "alert"
    
    def execute(self, action, reading: float, bound: float):
        if self == Action.MQTT:
            return self._execute_mqtt(action, reading, bound)
        elif self == Action.ALERT:
            return self._execute_alert(action, reading, bound)
    
    def _execute_mqtt(self, action, reading: float, bound: float):
        print(f"Sending MQTT message to {action.dest}. Reading: {reading}, Bound: {bound}")
        return mqtt_client.publish_message(action.dest, reading)

    def _execute_alert(self, action, reading: float, bound: float):
        print(f"Sending alert to {action.dest}. Reading: {reading}, Bound: {bound}")
        # send_alert(action['dest'], reading)