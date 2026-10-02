from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import require_api_key
from app.models.api import NamedQueryRequest
from app.services.profile_manager import profiles
from app.services.query_service import query_service


router = APIRouter(
    prefix="/{profile_id}",
    tags=["Explorer"],
    dependencies=[Depends(require_api_key)],
)


def _profile(profile_id: str):
    try:
        return profiles.get(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _entity_cfg(profile_id: str, entity_type: str):
    profile = _profile(profile_id)
    cfg = profile.entities.get(entity_type)
    if not cfg:
        raise HTTPException(
            status_code=404,
            detail=f"Entity type '{entity_type}' is not configured.",
        )
    return profile, cfg


@router.get("/tree/root")
def tree_root(profile_id: str):
    p = _profile(profile_id)
    return query_service.execute(profile_id, p.hierarchy.root_query, {})


@router.get("/tree/children")
def tree_children(
    profile_id: str,
    node_type: str,
    node_id: str,
):
    p = _profile(profile_id)
    qname = p.hierarchy.children_queries.get(node_type)
    if not qname:
        raise HTTPException(
            status_code=404,
            detail=f"No tree child query configured for node_type='{node_type}'.",
        )
    return query_service.execute(
        profile_id,
        qname,
        {"node_id": node_id},
    )


@router.get("/entities/{entity_type}/{entity_id}")
def entity_detail(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.detail_query:
        raise HTTPException(status_code=404, detail="Detail query not configured.")
    result = query_service.execute(
        profile_id,
        cfg.detail_query,
        {"entity_id": entity_id},
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Entity not found.")
    return result


@router.get("/entities/{entity_type}/{entity_id}/children")
def entity_children(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.children_query:
        raise HTTPException(status_code=404, detail="Children query not configured.")
    return query_service.execute(
        profile_id,
        cfg.children_query,
        {"entity_id": entity_id},
    )


@router.get("/entities/{entity_type}/{entity_id}/signals")
def entity_signals(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.signals_query:
        raise HTTPException(status_code=404, detail="Signals query not configured.")
    return query_service.execute(
        profile_id,
        cfg.signals_query,
        {"entity_id": entity_id},
    )


@router.get("/entities/{entity_type}/{entity_id}/path")
def entity_path(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.path_query:
        raise HTTPException(status_code=404, detail="Path query not configured.")
    return query_service.execute(
        profile_id,
        cfg.path_query,
        {"entity_id": entity_id},
    )


@router.get("/entities/{entity_type}/{entity_id}/upstream")
def upstream(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.upstream_query:
        raise HTTPException(status_code=404, detail="Upstream query not configured.")
    return query_service.execute(
        profile_id,
        cfg.upstream_query,
        {"entity_id": entity_id},
    )


@router.get("/entities/{entity_type}/{entity_id}/downstream")
def downstream(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.downstream_query:
        raise HTTPException(status_code=404, detail="Downstream query not configured.")
    return query_service.execute(
        profile_id,
        cfg.downstream_query,
        {"entity_id": entity_id},
    )


@router.get("/topology/{entity_type}/{entity_id}")
def topology(
    profile_id: str,
    entity_type: str,
    entity_id: str,
):
    _, cfg = _entity_cfg(profile_id, entity_type)
    if not cfg.topology_query:
        raise HTTPException(status_code=404, detail="Topology query not configured.")
    return query_service.execute(
        profile_id,
        cfg.topology_query,
        {"entity_id": entity_id},
    )


@router.get("/search")
def search(
    profile_id: str,
    q: str = Query(min_length=1, max_length=200),
    entity_type: Optional[str] = None,
    limit: Optional[int] = None,
):
    p = _profile(profile_id)
    resolved_limit = limit or p.search.default_limit
    resolved_limit = max(1, min(resolved_limit, p.search.max_limit))

    params: Dict[str, Any] = {
        "q": q,
        "q_like": f"%{q.upper()}%",
        "limit": resolved_limit,
        "entity_type": entity_type,
    }

    qcfg = p.queries[p.search.query]
    params = {k: v for k, v in params.items() if k in qcfg.allowed_params}

    return query_service.execute(profile_id, p.search.query, params)


@router.post("/queries/{query_name}")
def named_query(
    profile_id: str,
    query_name: str,
    body: NamedQueryRequest,
):
    return query_service.execute(
        profile_id,
        query_name,
        body.params,
        require_exposed=True,
    )
