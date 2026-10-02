from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_catalog_service
from app.domain.models import CatalogNode, EquipmentSignal, PageResult
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/{profile_id}", tags=["Power Equipment Directory"])


@router.get("/substations", response_model=PageResult[CatalogNode])
async def substations(
    profile_id: str,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.list_nodes(profile_id, "substation", None, None, q, offset, limit)


@router.get("/bays", response_model=PageResult[CatalogNode])
async def bays(
    profile_id: str,
    substation_id: Annotated[int | None, Query(gt=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.list_nodes(profile_id, "bay", substation_id, None, q, offset, limit)


@router.get("/busbars", response_model=PageResult[CatalogNode])
async def busbars(
    profile_id: str,
    substation_id: Annotated[int | None, Query(gt=0)] = None,
    bay_id: Annotated[int | None, Query(gt=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.list_nodes(
        profile_id, "busbar_section", substation_id, bay_id, q, offset, limit
    )


@router.get("/feeders", response_model=PageResult[CatalogNode])
async def feeders(
    profile_id: str,
    substation_id: Annotated[int | None, Query(gt=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.list_nodes(profile_id, "feeder", substation_id, None, q, offset, limit)


@router.get("/equipment", response_model=PageResult[CatalogNode])
async def equipment(
    profile_id: str,
    entity_type: Annotated[
        str | None,
        Query(max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    ] = None,
    substation_id: Annotated[int | None, Query(gt=0)] = None,
    bay_id: Annotated[int | None, Query(gt=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.list_equipment(
        profile_id, entity_type, substation_id, bay_id, q, offset, limit
    )


@router.get("/signals", response_model=PageResult[EquipmentSignal])
async def signals(
    profile_id: str,
    substation_id: Annotated[int | None, Query(gt=0)] = None,
    entity_type: Annotated[
        str | None,
        Query(max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    ] = None,
    entity_id: Annotated[int | None, Query(gt=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.signal_list(
        profile_id, substation_id, entity_type, entity_id, q, offset, limit
    )

