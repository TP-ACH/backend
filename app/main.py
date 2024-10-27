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

APP_URL = os.getenv("APP_URL")

app = FastAPI(docs_url=None)

security = HTTPBasic()

origins = [
    "*",
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
app.include_router(alerts_router, prefix="/alerts", tags=["App"])
app.include_router(users_router, prefix="/users", tags=["App"])


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/docs",include_in_schema=False)
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