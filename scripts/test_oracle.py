from __future__ import annotations

import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import ConfigStore
from app.db.oracle import AsyncOracleDatabase


async def run() -> int:
    store = ConfigStore(ROOT / "config")
    store.load()
    profile = store.get_profile("jeddah")
    source = profile.datasources["model"]

    database = AsyncOracleDatabase(
        source,
        query_timeout_seconds=store.application.runtime.query_timeout_seconds,
    )

    try:
        result = await database.execute(
            """
            SELECT
                SYS_CONTEXT('USERENV', 'DB_NAME') AS db_name,
                SYS_CONTEXT('USERENV', 'SERVICE_NAME') AS service_name,
                SYS_CONTEXT('USERENV', 'CURRENT_USER') AS current_user,
                SYSDATE AS db_time
            FROM dual
            """,
            result="one",
        )

        print("Oracle connection: OK")
        print("DB Name     :", result.get("db_name"))
        print("Service Name:", result.get("service_name"))
        print("Current User:", result.get("current_user"))
        print("DB Time     :", result.get("db_time"))
        print("Mode        : READ ONLY")
        return 0
    finally:
        await database.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
