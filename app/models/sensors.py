from enum import Enum

class Sensors(Enum):
    TEMPERATURE = 'temperature'
    ROOM_TEMPERATURE = 'room_temperature'
    HUMIDITY = 'humidity'
    PH = 'ph'
    EC = 'ec'
    FLOATER = 'floater'
    LIGHT = 'light'