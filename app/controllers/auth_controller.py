from typing import Annotated

from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, APIRouter, status

from models.auth import Token, UserRegister
from services.auth_service import generate_token
from services.auth_service import get_password_hash
from clients.mongodb_client import insert_user, get_user


router = APIRouter()


@router.post("/register")
async def register_user(new_user: UserRegister):
    new_user_data = new_user.user
    user = await get_user(new_user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    # TODO: Add device_id validation
    new_user_data.password = get_password_hash(new_user_data.password)
    await insert_user(new_user_data)

    return Response(status_code=201)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    access_token = await generate_token(form_data.username, form_data.password)
    return Token(access_token=access_token, token_type="bearer")
