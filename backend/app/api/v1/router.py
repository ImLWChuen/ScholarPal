from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.interviews import router as interviews_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.offers import router as offers_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profiles_router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(profiles_router, prefix="/profile", tags=["Profiles"])
api_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(offers_router, prefix="/offers", tags=["Offers"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
