from typing import Annotated

from fastapi.responses import Response
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from models.auth import User, Token, UserRegister
from services.auth_service import get_password_hash
from clients.mongodb_client import insert_user, get_user
from services.auth_service import generate_token, get_current_user


router = APIRouter()


@router.post("/register")
async def register_user(new_user: UserRegister):
    user = await get_user(new_user.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    new_user.password = get_password_hash(new_user.password)
    await insert_user(new_user)

    return Response(status_code=201)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    access_token = await generate_token(form_data.username, form_data.password)
    return Token(access_token=access_token, token_type="bearer")
