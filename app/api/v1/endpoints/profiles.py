from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_catalog_service
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("")
async def list_profiles(service: CatalogService = Depends(get_catalog_service)):
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "metadata": p.metadata,
        }
        for p in service.profiles.values()
    ]


@router.get("/{profile_id}/capabilities")
async def capabilities(
    profile_id: str,
    service: CatalogService = Depends(get_catalog_service),
):
    profile = service.profile(profile_id)

    return {
        "profile": profile.id,
        "catalog": {
            "enabled": profile.catalog.enabled,
            "source": profile.catalog.source,
            "default_page_size": profile.catalog.default_page_size,
            "max_page_size": profile.catalog.max_page_size,
            "node_types": CatalogRepository.supported_entity_types(),
        },
        "entity_types": CatalogRepository.supported_entity_types(),
        "realtime": {
            "enabled": profile.realtime.enabled,
            "signal": bool(profile.realtime.signal_query),
            "batch": bool(profile.realtime.batch_query),
        },
    }
