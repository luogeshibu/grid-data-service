from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import ConfigStore
from app.core.logging import configure_logging, request_id_ctx
from app.core.middleware import RequestIdMiddleware
from app.db.registry import DatabaseRegistry
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.query_repository import QueryRepository
from app.services.cache import TTLCache
from app.services.catalog_service import CatalogService
from app.services.query_service import (
    QueryAccessError,
    QueryNotFoundError,
    QueryParameterError,
    QueryService,
)

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_store = ConfigStore()
    config_store.load()

    profiles = {p.id: p for p in config_store.profiles()}

    registry = DatabaseRegistry(
        query_timeout_seconds=config_store.application.runtime.query_timeout_seconds
    )
    for profile in profiles.values():
        registry.register_profile(profile)

    repository = QueryRepository(registry=registry, profiles=profiles)
    query_service = QueryService(
        profiles=profiles,
        repository=repository,
        cache=TTLCache(),
    )
    catalog_repository = CatalogRepository(registry=registry, profiles=profiles)
    catalog_service = CatalogService(
        profiles=profiles,
        repository=catalog_repository,
        cache=TTLCache(),
    )

    app.state.config_store = config_store
    app.state.registry = registry
    app.state.query_service = query_service
    app.state.catalog_service = catalog_service

    logger.info(
        "application_started profiles=%s version=%s",
        sorted(profiles),
        __version__,
    )

    try:
        yield
    finally:
        await registry.close_all()
        logger.info("application_stopped")


# Load application metadata once for app construction.
_bootstrap_config = ConfigStore()
_bootstrap_config.load()
_app_cfg = _bootstrap_config.application

app = FastAPI(
    title=_app_cfg.api.title,
    description=_app_cfg.api.description,
    version=__version__,
    docs_url=_app_cfg.api.docs_url,
    redoc_url=_app_cfg.api.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    RequestIdMiddleware,
    header_name=_app_cfg.runtime.request_id_header,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=_app_cfg.runtime.trusted_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_app_cfg.runtime.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(QueryNotFoundError)
@app.exception_handler(KeyError)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "code": "not_found",
            "message": str(exc).strip("'"),
            "request_id": request_id_ctx.get(),
        },
    )


@app.exception_handler(QueryParameterError)
@app.exception_handler(ValueError)
async def bad_request_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={
            "code": "bad_request",
            "message": str(exc),
            "request_id": request_id_ctx.get(),
        },
    )


@app.exception_handler(QueryAccessError)
async def forbidden_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=403,
        content={
            "code": "forbidden",
            "message": str(exc),
            "request_id": request_id_ctx.get(),
        },
    )


app.include_router(
    api_v1_router,
    prefix=_app_cfg.api.prefix,
)


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "grid-data-service",
        "version": __version__,
        "api": _app_cfg.api.prefix,
        "docs": _app_cfg.api.docs_url,
    }
