from fastapi import APIRouter, Depends, status, HTTPException

from clients.mongodb_client import update_user
from models.auth import UserResponse, UserUpdateRequest, UserUpdate
from services.auth_service import get_current_user, get_password_hash, verify_password
from utils.logger import logger

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/me", response_model=UserResponse)
async def get_user_info(user=Depends(get_current_user)):
    return UserResponse(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.put("/update", response_model=UserResponse)
async def update_user_info(user_update: UserUpdateRequest, user=Depends(get_current_user)):
    if user_update.new_password:
        if not user_update.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is required",
            )
        if not verify_password(user_update.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password does not match",
            )
        user_update.new_password = get_password_hash(user_update.new_password)

    user_update = UserUpdate(
        first_name=user_update.first_name,
        last_name=user_update.last_name,
        password=user_update.new_password,
    )

    updated_user = await update_user(user, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse(
        username=updated_user.username,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
    )
