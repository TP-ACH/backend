from fastapi import FastAPI
from mqtt_client import start_mqtt_client

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_mqtt_client()

@app.get("/")
def read_root():
    return {"Hello": "World"}
