from fastapi import FastAPI

from scholarpal.application.api.health import router as health_router

app = FastAPI(title="ScholarPal")
app.include_router(health_router, prefix="/api")
