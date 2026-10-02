from __future__ import annotations

from typing import Any

from app.db.registry import DatabaseRegistry
from app.models.profile import ProfileConfig


class QueryRepository:
    def __init__(
        self,
        registry: DatabaseRegistry,
        profiles: dict[str, ProfileConfig],
    ):
        self.registry = registry
        self.profiles = profiles

    async def execute(
        self,
        profile_id: str,
        query_name: str,
        params: dict[str, Any],
    ) -> Any:
        profile = self.profiles[profile_id]
        query = profile.queries[query_name]
        database = await self.registry.get(profile_id, query.source)

        return await database.execute(
            sql=query.sql,
            params=params,
            result=query.result,
        )
