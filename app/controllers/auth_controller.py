from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, Request
from urllib.parse import urlencode
from utils.logger import logger
from clients.homeassistant_client import get_login_url, get_token_request
from models.template import Attribute
import httpx

router = APIRouter()

@router.get("/login")
async def login():
    auth_url = get_login_url("http://127.0.0.1:8000/auth/callback")
    return RedirectResponse(auth_url)

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"message": "Authorization code not provided"})
    
    req = get_token_request("http://127.0.0.1:8000/auth/callback", code)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(req["url"], **req["kwargs"])
        
        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"message": response.text})
        
        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']
        expires_in = response.json()['expires_in']
        # insert data into mongo client
        return access_token
    

@router.get("/fetch_and_save_ha_files")
async def fetch_and_save():
    try:
        config_files = await get_homeassistant_config_files()
        return JSONResponse(status_code=200, content=config_files)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to fetch ha files {str(e)}"})
    
@router.post("/modify_threshold/ph")
async def modify_threshold_ph(attribute: Attribute):
    try:
        await modify_ph_threshold(attribute)
        return JSONResponse(status_code=200, content={"result": "Threshold modified successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to modify threshold {str(e)}"})
