from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import api_router
from app.core.config import settings
from app.domain.schemas import ALL_DOMAIN_ENUMS, ALL_DOMAIN_SCHEMAS


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

    def custom_openapi():
        if application.openapi_schema:
            return application.openapi_schema

        openapi_schema = get_openapi(
            title=application.title,
            version=application.version,
            openapi_version=application.openapi_version,
            description=application.description,
            routes=application.routes,
        )

        components = openapi_schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})

        # 1. Register shared domain enums
        for enum_cls in ALL_DOMAIN_ENUMS:
            schemas[enum_cls.__name__] = {
                "type": "string",
                "title": enum_cls.__name__,
                "description": (enum_cls.__doc__ or "").strip(),
                "enum": [item.value for item in enum_cls],
            }

        # 2. Register all Pydantic v2 domain schemas
        for model in ALL_DOMAIN_SCHEMAS:
            s = model.model_json_schema(ref_template="#/components/schemas/{model}")
            defs = s.pop("$defs", {})
            for def_name, def_schema in defs.items():
                if def_name not in schemas:
                    schemas[def_name] = def_schema
            name = model.__name__
            if name not in schemas:
                schemas[name] = s

        application.openapi_schema = openapi_schema
        return application.openapi_schema

    application.openapi = custom_openapi
    return application


app = create_application()
