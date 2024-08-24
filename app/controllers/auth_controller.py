from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, Request
from utils.logger import logger
from clients.homeassistant_client import get_login_request, get_token_request
from models.template import Attribute
import httpx

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    client_id = str(request.url).rsplit("/", 2)[0]
    auth_req = await get_login_request(redirect_uri, client_id)
    return RedirectResponse(auth_req)

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"message": "Authorization code not provided"})
    redirect_uri = request.url_for("auth_callback")
    client_id = str(request.url).rsplit("/", 2)[0]
    req = await get_token_request(redirect_uri, client_id, code)

    async with httpx.AsyncClient() as client:
        response = await client.post(req["url"], **req["kwargs"])
        
        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"message": response.text})

        access_token = response.json()['access_token']
        logger.info("Access token retrieved successfully")
        return JSONResponse(status_code=200, content={"access_token": access_token})
    