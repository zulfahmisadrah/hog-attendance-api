from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: Optional[str] = None
    name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserOut(UserBase):
    pass


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

