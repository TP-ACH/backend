from fastapi import FastAPI
from database import validate_connection
from mqtt_client import start_mqtt_client
from validator import Validator
from logger import logger

app = FastAPI()

validator = Validator()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting MQTT client")
    start_mqtt_client()
    try:
        await validate_connection()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/set_thresholds")
def set_thresholds(validator: Validator):
    logger.info(f"Setting thresholds: {validator.dict()}")
    return validator
