from fastapi import APIRouter, Depends, status, HTTPException

from clients.mongodb_client import update_user
from models.auth import UserResponse, UserUpdate, User
from services.auth_service import get_current_user, get_password_hash

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/me")
async def get_user_info(user=Depends(get_current_user)) -> UserResponse:
    """Retrieves the user's non private information."""
    return UserResponse(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.put("/update")
async def update_user_info(user_update: UserUpdate, user=Depends(get_current_user)) -> UserResponse:
    """Updates the user's information. Not the password."""
    if user_update.password:
        user_update.password = get_password_hash(user_update.password)
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
