from fastapi import APIRouter

from app.api.endpoints import users, faculties, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(faculties.router, prefix="/faculties", tags=["faculties"])
