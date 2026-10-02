from __future__ import annotations

import json
from typing import Any

from app.models.profile import ProfileConfig
from app.repositories.query_repository import QueryRepository
from app.services.cache import TTLCache


class QueryNotFoundError(KeyError):
    pass


class QueryParameterError(ValueError):
    pass


class QueryAccessError(PermissionError):
    pass


class QueryService:
    def __init__(
        self,
        profiles: dict[str, ProfileConfig],
        repository: QueryRepository,
        cache: TTLCache,
    ):
        self.profiles = profiles
        self.repository = repository
        self.cache = cache

    def profile(self, profile_id: str) -> ProfileConfig:
        try:
            return self.profiles[profile_id]
        except KeyError as exc:
            raise QueryNotFoundError(f"Unknown profile: {profile_id}") from exc

    async def execute(
        self,
        profile_id: str,
        query_name: str,
        supplied_params: dict[str, Any] | None = None,
        *,
        require_exposed: bool = False,
    ) -> Any:
        profile = self.profile(profile_id)

        query = profile.queries.get(query_name)
        if query is None:
            raise QueryNotFoundError(
                f"Query '{query_name}' is not configured for profile '{profile_id}'."
            )

        if require_exposed and not query.exposed:
            raise QueryAccessError(f"Query '{query_name}' is not exposed.")

        supplied_params = supplied_params or {}

        unexpected = set(supplied_params) - set(query.allowed_params)
        if unexpected:
            raise QueryParameterError(f"Unexpected parameters: {sorted(unexpected)}")

        missing = set(query.required_params) - set(supplied_params)
        if missing:
            raise QueryParameterError(f"Missing required parameters: {sorted(missing)}")

        params = {name: supplied_params.get(name) for name in query.allowed_params}

        cache_key = (
            profile_id,
            query_name,
            json.dumps(params, sort_keys=True, default=str),
        )

        if query.cache_ttl_seconds:
            cached, found = self.cache.get(cache_key)
            if found:
                return cached

        result = await self.repository.execute(
            profile_id=profile_id,
            query_name=query_name,
            params=params,
        )

        self.cache.set(cache_key, result, query.cache_ttl_seconds)
        return result
