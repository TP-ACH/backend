from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.auth_controller import router as auth_router
from controllers.mqtt_controller import router as mqtt_router
from controllers.sensors_controller import router as sensors_router
from controllers.homeassistant_controller import router as ha_router

APP_URL = os.getenv("APP_URL")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    APP_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(mqtt_router, prefix="/mqtt")
app.include_router(sensors_router, prefix="/sensors")
app.include_router(ha_router, prefix="/ha")
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def read_root():
    return {"Hello": "World"}
