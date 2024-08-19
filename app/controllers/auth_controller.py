from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, Request
from utils.logger import logger
from clients.homeassistant_client import get_login_request, get_token_request
from models.template import Attribute
import httpx

router = APIRouter()

@router.get("/login")
async def login():
    auth_req = await get_login_request("http://localhost:8000/auth/callback")
    logger.info(auth_req)
    return RedirectResponse(auth_req)

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"message": "Authorization code not provided"})

    req = await get_token_request("http://localhost:8000/auth/callback", code)

    async with httpx.AsyncClient() as client:
        # response = await client.post(req["url"], **req["kwargs"])
        headers=req["kwargs"]["headers"]
        data=req["kwargs"]["data"]
        logger.info("********** POST ***********")
        logger.info(headers)
        logger.info(data)
        logger.info(req["url"])
        response = await client.post(req["url"], headers=headers, data=data)

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"message": response.text})

        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']
        expires_in = response.json()['expires_in']
        # insert data into mongo client
        return access_token
    