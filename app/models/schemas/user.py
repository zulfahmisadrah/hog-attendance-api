from typing import Optional, List

from pydantic import BaseModel, EmailStr

from .core import DateTimeModelMixin, IDMixin


class UserRole(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True
    roles: Optional[List[UserRole]] = None


class UserCreate(UserBase):
    name: str
    username: str
    password: str
    roles: List[UserRole]


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(DateTimeModelMixin, UserBase, IDMixin):
    class Config:
        orm_mode = True

