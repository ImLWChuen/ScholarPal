from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # API v1 routes
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Direct /api/health and /health convenience routes
    @application.get("/health", tags=["Health"])
    @application.get("/api/health", tags=["Health"])
    async def root_health():
        return {"status": "ok"}

    return application


app = create_application()
