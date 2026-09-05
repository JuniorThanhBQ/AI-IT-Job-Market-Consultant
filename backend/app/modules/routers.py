from fastapi import APIRouter

from app.modules.company.views import router as company_router
from app.modules.consultant.views import router as consultant_router
from app.modules.consultee_profile.views import profile_router
from app.modules.job.views import router as job_router
from app.modules.user.views import auth_router
from app.modules.user.views import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/accounts", tags=["auth"])
api_router.include_router(profile_router, prefix="/users/profile", tags=["profile"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(consultant_router, prefix="/consultants", tags=["consultant"])
api_router.include_router(company_router, prefix="/companies", tags=["companies"])
api_router.include_router(job_router, prefix="/jobs", tags=["jobs"])
