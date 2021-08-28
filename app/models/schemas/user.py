from typing import Optional, List
from pydantic import BaseModel, EmailStr

from .role import Role


class UserBase(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True


class UserOut(UserBase):
    pass


class UserCreate(UserBase):
    name: str
    username: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: Optional[int] = None
    roles: List[Role]

    class Config:
        orm_mode = True

