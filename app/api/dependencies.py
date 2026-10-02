from __future__ import annotations

from fastapi import Request

from app.services.catalog_service import CatalogService
from app.services.query_service import QueryService


def get_query_service(request: Request) -> QueryService:
    return request.app.state.query_service


def get_catalog_service(request: Request) -> CatalogService:
    return request.app.state.catalog_service
