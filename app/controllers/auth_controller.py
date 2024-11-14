from typing import Annotated

from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, APIRouter, status

from models.auth import Token, UserRegister
from services.auth_service import generate_token
from services.auth_service import get_password_hash
from services.auth_service import validate_access_token
from clients.mongodb_client import insert_user, get_user


router = APIRouter()


@router.post("/register")
async def register_user(new_user: UserRegister):
    """Create a new user."""
    new_user_data = new_user.user
    user = await get_user(new_user_data.username)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    if not validate_access_token(new_user.access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    new_user_data.password = get_password_hash(new_user_data.password)
    await insert_user(new_user_data)

    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login to get an access token. To be used for the other endpoints."""
    access_token = await generate_token(form_data.username, form_data.password)
    return Token(access_token=access_token, token_type="bearer")
