from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import get_catalog_service
from app.domain.models import CatalogNode, PageResult
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/{profile_id}/catalog", tags=["Catalog"])


@router.get("/roots", response_model=PageResult[CatalogNode])
async def catalog_roots(
    profile_id: str,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.roots(profile_id, offset, limit)


@router.get("/nodes/{node_id}/children", response_model=PageResult[CatalogNode])
async def catalog_children(
    profile_id: str,
    node_id: Annotated[str, Path(min_length=3, max_length=160)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.children(profile_id, node_id, offset, limit)


@router.get("/search", response_model=PageResult[CatalogNode])
async def catalog_search(
    profile_id: str,
    q: Annotated[str, Query(min_length=1, max_length=200)],
    entity_type: Annotated[str | None, Query(max_length=64)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.search(profile_id, q, entity_type, offset, limit)
