from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_api_key
from app.services.profile_manager import profiles


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("")
def list_profiles(_: None = Depends(require_api_key)):
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "metadata": p.metadata,
        }
        for p in profiles.list()
    ]


@router.get("/{profile_id}/capabilities")
def capabilities(profile_id: str, _: None = Depends(require_api_key)):
    try:
        p = profiles.get(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "profile": p.id,
        "entity_types": sorted(p.entities.keys()),
        "tree_parent_types": sorted(p.hierarchy.children_queries.keys()),
        "realtime": {
            "enabled": p.realtime.enabled,
            "batch": bool(p.realtime.batch_query),
            "signal": bool(p.realtime.signal_query),
        },
        "named_queries": sorted(
            name for name, q in p.queries.items() if q.exposed
        ),
    }
