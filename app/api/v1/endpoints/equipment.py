from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import get_catalog_service
from app.domain.models import EquipmentDetail, EquipmentSignal
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/{profile_id}/equipment", tags=["Equipment"])


@router.get("/{entity_type}/{entity_id}", response_model=EquipmentDetail)
async def equipment_detail(
    profile_id: str,
    entity_type: Annotated[str, Path(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")],
    entity_id: Annotated[int, Path(gt=0)],
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.detail(profile_id, entity_type, entity_id)


@router.get("/{entity_type}/{entity_id}/signals", response_model=list[EquipmentSignal])
async def equipment_signals(
    profile_id: str,
    entity_type: Annotated[str, Path(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")],
    entity_id: Annotated[int, Path(gt=0)],
    limit: Annotated[int, Query(ge=1, le=2000)] = 200,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.signals(profile_id, entity_type, entity_id, limit)
