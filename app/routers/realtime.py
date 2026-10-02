from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_api_key
from app.models.api import RealtimeBatchRequest
from app.services.profile_manager import profiles
from app.services.query_service import query_service


router = APIRouter(
    prefix="/{profile_id}/realtime",
    tags=["Realtime"],
    dependencies=[Depends(require_api_key)],
)


def _profile(profile_id: str):
    try:
        p = profiles.get(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not p.realtime.enabled:
        raise HTTPException(
            status_code=404,
            detail="Realtime access is disabled for this profile.",
        )
    return p


@router.get("/signals/{signal_id}")
def realtime_signal(profile_id: str, signal_id: str):
    p = _profile(profile_id)
    if not p.realtime.signal_query:
        raise HTTPException(
            status_code=404,
            detail="Realtime signal query is not configured.",
        )
    return query_service.execute(
        profile_id,
        p.realtime.signal_query,
        {"signal_id": signal_id},
    )


@router.post("/batch")
def realtime_batch(profile_id: str, body: RealtimeBatchRequest):
    p = _profile(profile_id)

    if not p.realtime.batch_query:
        raise HTTPException(
            status_code=404,
            detail="Realtime batch query is not configured.",
        )

    if len(body.point_ids) > p.realtime.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch is too large. Max={p.realtime.max_batch_size}.",
        )

    return query_service.execute(
        profile_id,
        p.realtime.batch_query,
        {"point_ids_csv": ",".join(body.point_ids)},
    )
