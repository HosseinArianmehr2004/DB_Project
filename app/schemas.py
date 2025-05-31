from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union, Literal
from datetime import date


class LoginRequest(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: str
    confirm_password: str
    email: EmailStr
    name: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    is_premium: Optional[bool] = False


class FieldUpdate(BaseModel):
    email: str
    field: str
    value: str


class FavoriteRequest(BaseModel):
    username: str
    title: str
