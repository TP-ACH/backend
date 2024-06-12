from fastapi import FastAPI
from database import validate_connection
from mqtt_client import start_mqtt_client
from logger import logger

app = FastAPI()

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
