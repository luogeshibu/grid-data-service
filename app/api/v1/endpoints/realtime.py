from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_query_service
from app.schemas.api import RealtimeBatchRequest
from app.services.query_service import QueryService

router = APIRouter(prefix="/{profile_id}/realtime", tags=["Realtime"])


@router.get("/signals/{signal_id}")
async def signal_value(
    profile_id: str,
    signal_id: str,
    service: QueryService = Depends(get_query_service),
):
    profile = service.profile(profile_id)
    if not profile.realtime.enabled or not profile.realtime.signal_query:
        raise KeyError("Realtime signal access is disabled")

    return await service.execute(
        profile_id,
        profile.realtime.signal_query,
        {"signal_id": signal_id},
    )


@router.post("/batch")
async def batch_values(
    profile_id: str,
    body: RealtimeBatchRequest,
    service: QueryService = Depends(get_query_service),
):
    profile = service.profile(profile_id)

    if not profile.realtime.enabled or not profile.realtime.batch_query:
        raise KeyError("Realtime batch access is disabled")

    if len(body.point_ids) > profile.realtime.max_batch_size:
        raise ValueError(f"Batch too large: max={profile.realtime.max_batch_size}")

    return await service.execute(
        profile_id,
        profile.realtime.batch_query,
        {"point_ids_csv": ",".join(body.point_ids)},
    )
