from __future__ import annotations

from typing import Any, Dict

import oracledb

from app.core.read_only import validate_read_only_sql
from app.core.utils import to_jsonable
from app.models.profile import DataSourceConfig


class OraclePool:
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.pool = oracledb.create_pool(
            user=config.user,
            password=config.password,
            dsn=config.dsn,
            min=config.pool.min,
            max=config.pool.max,
            increment=config.pool.increment,
            timeout=config.pool.timeout,
        )

    def close(self):
        self.pool.close()

    def execute(
        self,
        sql: str,
        params: Dict[str, Any] | None = None,
        result: str = "many",
    ):
        validate_read_only_sql(sql)
        params = params or {}

        with self.pool.acquire() as conn:
            try:
                conn.call_timeout = 30_000
            except Exception:
                pass

            with conn.cursor() as cursor:
                cursor.execute(sql, params)

                if result == "scalar":
                    row = cursor.fetchone()
                    return None if row is None else to_jsonable(row[0])

                columns = [
                    (desc[0] or "").lower()
                    for desc in cursor.description
                ]

                if result == "one":
                    row = cursor.fetchone()
                    if row is None:
                        return None
                    return to_jsonable(dict(zip(columns, row)))

                rows = cursor.fetchall()
                return [
                    to_jsonable(dict(zip(columns, row)))
                    for row in rows
                ]

    def ping(self) -> bool:
        with self.pool.acquire() as conn:
            conn.ping()
        return True
