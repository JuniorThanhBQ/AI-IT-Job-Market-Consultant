from fastapi import APIRouter

from app.modules.consultant.views import router as consultant_router
from app.modules.user.views import login_router
from app.modules.user.views import router as user_router

api_router = APIRouter()
api_router.include_router(login_router, prefix="/login", tags=["login"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(consultant_router, prefix="/consultant", tags=["consultant"])
