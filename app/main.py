import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from controllers.auth_controller import router as auth_router
from controllers.mqtt_controller import router as mqtt_router
from controllers.users_controller import router as users_router
from controllers.rules_controller import router as rules_router
from controllers.alerts_controller import router as alerts_router
from controllers.sensors_controller import router as sensors_router
from services.auth_service import generate_token


tags_metadata = [
    {
        "name": "Auth",
        "description": "Operations for users authentication.",
    },
    {
        "name": "Users",
        "description": "Operations for users management.",
    },
    {
        "name": "Alerts",
        "description": "Operations for alerts management.",
    },
    {
        "name": "Rules",
        "description": "Operations for rules management.",
    },
    {
        "name": "Sensors",
        "description": "Operations for sensors management.",
    },
]

app = FastAPI(
    title="Cleverleafy",
    description="CleverLeafy API helps you with your hydroponic garden by automating tasks and sending alerts when needed.",
    summary="API for the automation of your hydroponic gardens.",
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    docs_url=None,
)


security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mqtt_router, prefix="/mqtt")

# Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# APP routes
app.include_router(sensors_router, prefix="/sensors", tags=["Sensors"])
app.include_router(rules_router, prefix="/rules", tags=["Rules"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello": "World"}


@app.get("/docs", include_in_schema=False)
async def get_documentation(credentials: HTTPBasicCredentials = Depends(security)):
    access_token = await generate_token(credentials.username, credentials.password)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
