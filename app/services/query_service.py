from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import HTTPException, status

from app.db.registry import datasources
from app.services.cache import cache
from app.services.profile_manager import profiles


class QueryService:
    def execute(
        self,
        profile_id: str,
        query_name: str,
        params: Dict[str, Any] | None = None,
        *,
        require_exposed: bool = False,
    ):
        supplied_params = params or {}

        try:
            profile = profiles.get(profile_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        query = profile.queries.get(query_name)
        if not query:
            raise HTTPException(
                status_code=404,
                detail=f"Query '{query_name}' is not configured for profile "
                       f"'{profile_id}'.",
            )

        if require_exposed and not query.exposed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Query '{query_name}' is not exposed.",
            )

        extra = set(supplied_params) - set(query.allowed_params)
        if extra:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters: {sorted(extra)}",
            )

        missing = set(query.required_params) - set(supplied_params)
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required parameters: {sorted(missing)}",
            )

        params = {
            name: supplied_params.get(name)
            for name in query.allowed_params
        }

        cache_key = None
        if query.cache_ttl_seconds > 0:
            cache_key = (
                profile_id,
                query_name,
                json.dumps(params, sort_keys=True, default=str),
            )
            cached, found = cache.get(cache_key)
            if found:
                return cached

        try:
            pool = datasources.get(profile_id, query.source)
            result = pool.execute(
                query.sql,
                params=params,
                result=query.result,
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Datasource query failed.",
                    "profile": profile_id,
                    "query": query_name,
                    "source": query.source,
                    "error": str(exc),
                },
            ) from exc

        if cache_key:
            cache.set(cache_key, result, query.cache_ttl_seconds)

        return result


query_service = QueryService()
