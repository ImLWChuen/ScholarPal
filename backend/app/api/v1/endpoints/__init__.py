from __future__ import annotations

from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.interviews import router as interviews_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.offers import router as offers_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.tasks import router as tasks_router

__all__ = [
    "applications_router",
    "auth_router",
    "health_router",
    "interviews_router",
    "notifications_router",
    "offers_router",
    "profiles_router",
    "tasks_router",
]
