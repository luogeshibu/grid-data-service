from __future__ import annotations

import asyncio
from contextlib import suppress

from app.db.oracle import AsyncOracleDatabase
from app.models.profile import ProfileConfig


class DatabaseRegistry:
    def __init__(self, query_timeout_seconds: int = 30):
        self.query_timeout_seconds = query_timeout_seconds
        self._configs: dict[tuple[str, str], object] = {}
        self._databases: dict[tuple[str, str], AsyncOracleDatabase] = {}
        self._lock = asyncio.Lock()

    def register_profile(self, profile: ProfileConfig) -> None:
        for source_name, source_config in profile.datasources.items():
            self._configs[(profile.id, source_name)] = source_config

    async def get(self, profile_id: str, source_name: str) -> AsyncOracleDatabase:
        key = (profile_id, source_name)

        if key in self._databases:
            return self._databases[key]

        async with self._lock:
            if key in self._databases:
                return self._databases[key]

            config = self._configs.get(key)
            if config is None:
                raise KeyError(
                    f"Datasource not configured: profile={profile_id}, source={source_name}"
                )

            db = AsyncOracleDatabase(
                config=config,
                query_timeout_seconds=self.query_timeout_seconds,
            )
            db.open()
            self._databases[key] = db
            return db

    async def close_all(self) -> None:
        for db in list(self._databases.values()):
            with suppress(Exception):
                await db.close()
        self._databases.clear()
