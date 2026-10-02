from __future__ import annotations

from threading import RLock
from typing import Dict, Tuple

from app.db.oracle import OraclePool
from app.models.profile import DataSourceConfig, ProfileConfig


class DataSourceRegistry:
    """
    Datasources are registered at startup but Oracle pools are created lazily.

    This matters for reusable profiles:
    - the server can start even if an optional realtime datasource is offline;
    - a disabled realtime feature does not create an unnecessary DB connection;
    - only datasources actually used by an API request allocate pools.
    """

    def __init__(self):
        self._configs: Dict[Tuple[str, str], DataSourceConfig] = {}
        self._pools: Dict[Tuple[str, str], OraclePool] = {}
        self._lock = RLock()

    def initialize_profile(self, profile: ProfileConfig):
        with self._lock:
            for source_name, source_cfg in profile.datasources.items():
                self._configs[(profile.id, source_name)] = source_cfg

    def get(self, profile_id: str, source_name: str) -> OraclePool:
        key = (profile_id, source_name)

        with self._lock:
            if key not in self._configs:
                raise KeyError(
                    f"Datasource is not configured: "
                    f"profile={profile_id}, source={source_name}"
                )

            pool = self._pools.get(key)
            if pool is None:
                pool = OraclePool(self._configs[key])
                self._pools[key] = pool

            return pool

    def close_all(self):
        with self._lock:
            for pool in self._pools.values():
                try:
                    pool.close()
                except Exception:
                    pass

            self._pools.clear()
            self._configs.clear()


datasources = DataSourceRegistry()
