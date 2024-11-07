from enum import Enum


class Type(Enum):
    OK = "ok"
    ACTION = "action"
    ERROR = "error"
    WARNING = "warning"


class Status(Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"


class Topic(Enum):
    CONNECTION_LOST = "connection_lost"  # Se perdio la conexion con el microcontrolador
    PH_FAIL = "ph_fail"  # El sensor de Ph no funciona
    EC_FAIL = "ec_fail"  # El sensor de EC no funciona
    HUMIDITY_FAIL = "humidity_fail"  # El sensor de humedad no funciona
    TEMPERATURE_FAIL = "temperature_fail"  # El sensor de temperatura no funciona
    PH_UP = "ph_up"  # El valor de Ph esta bajo
    PH_DOWN = "ph_down"  # El valor de Ph es elevado
    EC_UP = "water"  # El valor de EC esta elevado
    EC_DOWN = "nutrient"  # El valor de EC es bajo
    HUMIDITY_UP = "humidity_up"  # Hay mucha humedad en el ambiente
    HUMIDITY_DOWN = "humidity_down"  # Hay poca humedad en el ambiente
    TEMPERATURE_UP = "temperature_up"  # La temperatura esta elevada
    TEMPERATURE_DOWN = "temperature_down"  # Hay baja temperatura
    LIGHTS_OFF = "lights_off"  # Se apagaron las luces
    LIGHTS_ON = "lights_on"  # Se prendieron las luces
    PH_OK = "ph_ok"  # Se estabilizo el ph
    EC_OK = "ec_ok"  # Se estabilizo la EC
    WATER_DOWN = "water_down"  # El nivel de agua es bajo


TOPIC_MESSAGES = {
    Topic.CONNECTION_LOST: "Connection with the microcontroller lost",
    Topic.PH_FAIL: "Connection with the pH sensor lost",
    Topic.EC_FAIL: "Connection with the EC sensor lost",
    Topic.HUMIDITY_FAIL: "Connection with the humidity sensor lost",
    Topic.TEMPERATURE_FAIL: "Connection with the temperature sensor lost",
    Topic.PH_UP: "The pH value is below the acceptable range",
    Topic.PH_DOWN: "The pH value is above the acceptable range",
    Topic.EC_UP: "The EC value is below the acceptable range",
    Topic.EC_DOWN: "The EC value is above the acceptable range",
    Topic.HUMIDITY_UP: "The humidity level is above the acceptable range",
    Topic.HUMIDITY_DOWN: "The humidity level is below the acceptable range",
    Topic.TEMPERATURE_UP: "The temperature is above the acceptable range",
    Topic.TEMPERATURE_DOWN: "The temperature is below the acceptable range",
    Topic.LIGHTS_OFF: "The lights have been turned off",
    Topic.LIGHTS_ON: "The lights have been turned on",
    Topic.PH_OK: "The pH level has been stabilized",
    Topic.EC_OK: "The Nutrients level has been stabilized",
    Topic.WATER_DOWN: "The water level is low",
}

TOPIC_TITLES = {
    Topic.CONNECTION_LOST: "Connection lost",
    Topic.PH_FAIL: "pH sensor failed",
    Topic.EC_FAIL: "Nutrients sensor failed",
    Topic.HUMIDITY_FAIL: "Humidity sensor failed",
    Topic.TEMPERATURE_FAIL: "Temperature sensor failed",
    Topic.PH_UP: "PH low",
    Topic.PH_DOWN: "PH high",
    Topic.EC_UP: "Nutrients low",
    Topic.EC_DOWN: "Nutrients high",
    Topic.HUMIDITY_UP: "Humidity high",
    Topic.HUMIDITY_DOWN: "Humidity low",
    Topic.TEMPERATURE_UP: "Temperature high",
    Topic.TEMPERATURE_DOWN: "Temperature low",
    Topic.LIGHTS_OFF: "Lights off",
    Topic.LIGHTS_ON: "Lights on",
    Topic.PH_OK: "pH ok",
    Topic.EC_OK: "Nutrients ok",
    Topic.WATER_DOWN: "Water low",
}

TOPIC_TYPE_MAP = {
    Topic.CONNECTION_LOST: Type.ERROR,
    Topic.PH_FAIL: Type.ERROR,
    Topic.EC_FAIL: Type.ERROR,
    Topic.HUMIDITY_FAIL: Type.ERROR,
    Topic.TEMPERATURE_FAIL: Type.ERROR,
    Topic.PH_UP: Type.WARNING,
    Topic.PH_DOWN: Type.WARNING,
    Topic.EC_UP: Type.WARNING,
    Topic.EC_DOWN: Type.WARNING,
    Topic.HUMIDITY_UP: Type.WARNING,
    Topic.HUMIDITY_DOWN: Type.WARNING,
    Topic.TEMPERATURE_UP: Type.WARNING,
    Topic.TEMPERATURE_DOWN: Type.WARNING,
    Topic.LIGHTS_OFF: Type.OK,
    Topic.LIGHTS_ON: Type.OK,
    Topic.PH_OK: Type.OK,
    Topic.EC_OK: Type.OK,
}
