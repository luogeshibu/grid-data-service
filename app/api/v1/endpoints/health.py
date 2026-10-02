from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_query_service
from app.services.query_service import QueryService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def live():
    return {"status": "ok"}


@router.get("/ready")
async def ready(service: QueryService = Depends(get_query_service)):
    results = {}

    for profile in service.profiles.values():
        profile_status = {}
        for source_name in profile.datasources:
            try:
                database = await service.repository.registry.get(profile.id, source_name)
                await database.ping()
                profile_status[source_name] = "ok"
            except Exception as exc:
                profile_status[source_name] = f"error: {exc}"

        results[profile.id] = profile_status

    ok = bool(results) and all(
        state == "ok" for profile_status in results.values() for state in profile_status.values()
    )

    body = {
        "status": "ok" if ok else "degraded",
        "datasources": results,
    }
    return body if ok else JSONResponse(status_code=503, content=body)


@router.get("")
async def health():
    return {
        "status": "ok",
        "service": "grid-data-service",
    }
