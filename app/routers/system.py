from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_api_key
from app.db.registry import datasources
from app.services.profile_manager import profiles
from app.services.cache import cache


router = APIRouter(tags=["System"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "profiles": len(profiles.list()),
    }


@router.get("/health/{profile_id}")
def profile_health(profile_id: str, _: None = Depends(require_api_key)):
    try:
        profile = profiles.get(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = {}
    for source_name in profile.datasources:
        try:
            datasources.get(profile_id, source_name).ping()
            result[source_name] = {"status": "ok"}
        except Exception as exc:
            result[source_name] = {
                "status": "error",
                "detail": str(exc),
            }

    return {
        "profile": profile_id,
        "datasources": result,
    }


@router.post("/admin/cache/clear")
def clear_cache(_: None = Depends(require_api_key)):
    cache.clear()
    return {"status": "ok"}
