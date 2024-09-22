from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str


class UserRegister(BaseModel):
    user: User
    device_id: str
