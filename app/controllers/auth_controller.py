from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, Request
from utils.logger import logger
from clients.homeassistant_client import get_login_request, get_token_request
from models.template import Attribute
import httpx

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    url = request.url_for("auth_callback")
    auth_req = await get_login_request(url)
    return RedirectResponse(auth_req)

@router.get("/callback")
async def auth_callback(request: Request):
    logger.info(str(request.url))
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"message": "Authorization code not provided"})
    url = request.url_for("auth_callback")
    req = await get_token_request(url, code)

    async with httpx.AsyncClient() as client:
        response = await client.post(req["url"], **req["kwargs"])
        
        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"message": response.text})

        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']
        expires_in = response.json()['expires_in']
        # insert data into mongo client
        return access_token
    