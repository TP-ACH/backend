from fastapi import FastAPI
from controllers.mqtt_controller import router as mqtt_router
from controllers.sensors_controller import router as sensors_router
from controllers.homeassistant_controller import router as ha_router
from controllers.local_homeassitant_controller import router as local_ha_router

app = FastAPI()

app.include_router(mqtt_router, prefix="/mqtt")
app.include_router(sensors_router, prefix="/sensors")
app.include_router(ha_router, prefix="/ha")
app.include_router(local_ha_router, prefix="/local_ha")

@app.get("/")
def read_root():
    return {"Hello": "World"}
