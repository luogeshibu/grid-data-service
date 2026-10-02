from __future__ import annotations

from contextlib import suppress
from typing import Any

import oracledb

from app.core.json import jsonable
from app.core.read_only import validate_read_only_sql
from app.models.profile import DataSourceConfig


class AsyncOracleDatabase:
    def __init__(self, config: DataSourceConfig, query_timeout_seconds: int = 30):
        self.config = config
        self.query_timeout_seconds = query_timeout_seconds
        self.pool: oracledb.AsyncConnectionPool | None = None

    def open(self) -> None:
        if self.pool is not None:
            return

        self.pool = oracledb.create_pool_async(
            user=self.config.user,
            password=self.config.password,
            dsn=self.config.dsn,
            min=self.config.pool.min,
            max=self.config.pool.max,
            increment=self.config.pool.increment,
            timeout=self.config.pool.timeout,
            wait_timeout=self.config.pool.wait_timeout_ms,
            getmode=oracledb.POOL_GETMODE_TIMEDWAIT,
        )

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def ping(self) -> None:
        self.open()
        assert self.pool is not None
        async with self.pool.acquire() as connection:
            await connection.ping()

    async def execute(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        result: str = "many",
    ) -> Any:
        validate_read_only_sql(sql)
        self.open()
        assert self.pool is not None

        async with self.pool.acquire() as connection:
            with suppress(Exception):
                connection.call_timeout = self.query_timeout_seconds * 1000

            await connection.rollback()

            try:
                async with connection.cursor() as cursor:
                    await cursor.execute("SET TRANSACTION READ ONLY")
                    await cursor.execute(sql, params or {})

                    if result == "scalar":
                        row = await cursor.fetchone()
                        return None if row is None else jsonable(row[0])

                    columns = [(item[0] or "").lower() for item in cursor.description]

                    if result == "one":
                        row = await cursor.fetchone()
                        return (
                            None
                            if row is None
                            else jsonable(dict(zip(columns, row, strict=False)))
                        )

                    rows = await cursor.fetchall()
                    return [jsonable(dict(zip(columns, row, strict=False))) for row in rows]
            finally:
                await connection.rollback()
