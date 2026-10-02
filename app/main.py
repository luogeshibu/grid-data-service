from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.db.registry import datasources
from app.routers import explorer, profiles as profiles_router, realtime, system
from app.services.profile_manager import profiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    profiles.load_all()

    for profile in profiles.list():
        datasources.initialize_profile(profile)

    yield

    datasources.close_all()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Configuration-driven, read-only FastAPI backend for grid model, "
        "asset, signal and realtime-data exploration."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=settings.cors_origin_list != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/v1")
app.include_router(profiles_router.router, prefix="/api/v1")
app.include_router(explorer.router, prefix="/api/v1")
app.include_router(realtime.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api": "/api/v1",
    }
