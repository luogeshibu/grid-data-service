from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import get_catalog_service
from app.domain.models import TopologyRelation
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/{profile_id}/topology", tags=["Topology"])


@router.get("/{entity_type}/{entity_id}", response_model=list[TopologyRelation])
async def equipment_topology(
    profile_id: str,
    entity_type: Annotated[str, Path(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")],
    entity_id: Annotated[int, Path(gt=0)],
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
    service: CatalogService = Depends(get_catalog_service),
):
    return await service.topology(profile_id, entity_type, entity_id, limit)
