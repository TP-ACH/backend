from fastapi import FastAPI
from controllers.auth_controller import router as auth_router
from controllers.mqtt_controller import router as mqtt_router
from controllers.sensors_controller import router as sensors_router
from controllers.homeassistant_controller import router as ha_router

app = FastAPI()

app.include_router(mqtt_router, prefix="/mqtt")
app.include_router(sensors_router, prefix="/sensors")
app.include_router(ha_router, prefix="/ha")
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def read_root():
    return {"Hello": "World"}
