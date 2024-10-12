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
    PH_UP = "ph_up"  # El valor de Ph esta elevado
    PH_DOWN = "ph_down"  # El valor de Ph es bajo
    EC_UP = "ec_up"  # El valor de EC esta elevado
    EC_DOWN = "ec_down"  # El valor de EC es bajo
    HUMIDITY_UP = "humidity_up"  # Hay mucha humedad en el ambiente
    HUMIDITY_DOWN = "humidity_down"  # Hay poca humedad en el ambiente
    TEMPERATURE_UP = "temperature_up"  # La temperatura esta elevada
    TEMPERATURE_DOWN = "temperature_down"  # Hay baja temperatura
    LIGHTS_OFF = "lights_off"  # Se apagaron las luces
    LIGHTS_ON = "lights_on"  # Se prendieron las luces
    PH_OK = "ph_ok"  # Se estabilizo el ph
    EC_OK = "ec_ok"  # Se estabilizo la EC


TOPIC_MESSAGES = {
    Topic.CONNECTION_LOST: "Se perdió la conexión con el microcontrolador",
    Topic.PH_FAIL: "Se perdió la conexión con el sensor de Ph",
    Topic.EC_FAIL: "Se perdió la conexión con el sensor de EC",
    Topic.HUMIDITY_FAIL: "Se perdió la conexión con el sensor de humedad",
    Topic.TEMPERATURE_FAIL: "Se perdió la conexión con el sensor de temperatura",
    Topic.PH_UP: "El valor de Ph está elevado",
    Topic.PH_DOWN: "El valor de Ph es bajo",
    Topic.EC_UP: "El valor de EC está elevado",
    Topic.EC_DOWN: "El valor de EC es bajo",
    Topic.HUMIDITY_UP: "Hay mucha humedad en el ambiente",
    Topic.HUMIDITY_DOWN: "Hay poca humedad en el ambiente",
    Topic.TEMPERATURE_UP: "La temperatura está elevada",
    Topic.TEMPERATURE_DOWN: "Hay baja temperatura",
    Topic.LIGHTS_OFF: "Se apagaron las luces",
    Topic.LIGHTS_ON: "Se prendieron las luces",
    Topic.PH_OK: "Se estabilizó el pH",
    Topic.EC_OK: "Se estabilizó la EC",
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
