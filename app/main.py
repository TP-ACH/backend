import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.auth_controller import router as auth_router
from controllers.mqtt_controller import router as mqtt_router
from controllers.rules_controller import router as rules_router
from controllers.sensors_controller import router as sensors_router

APP_URL = os.getenv("APP_URL")

app = FastAPI()

origins = [
    APP_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mqtt_router, prefix="/mqtt")

# Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# APP routes
app.include_router(sensors_router, prefix="/sensors", tags=["App"])
app.include_router(rules_router, prefix="/rules", tags=["App"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
