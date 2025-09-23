from __future__ import annotations

from typing import Any, Optional

import os
import asyncio
import random
import asyncpg

from ..utils.serialization import dumps

__all__ = ["set_value"]

SET_LOCK_TIMEOUT_MS = int(os.getenv("PERSISTPG_SET_LOCK_TIMEOUT_MS", "200"))
SET_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_SET_STATEMENT_TIMEOUT_MS", "500"))
SET_MAX_RETRIES = int(os.getenv("PERSISTPG_SET_MAX_RETRIES", "2"))
SET_RETRY_BASE_MS = int(os.getenv("PERSISTPG_SET_RETRY_BASE_MS", "15"))
SET_SYNC_COMMIT = os.getenv("PERSISTPG_SET_SYNC_COMMIT", "on").lower()


async def set_value(pool: asyncpg.Pool, key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Store a key with a value and optional TTL.

    Args:
        pool: asyncpg connection pool.
        key: Key to set.
        value: JSON-serializable value.
        expire: Optional TTL in seconds.

    Returns:
        True if the value is stored.
    """
    payload = dumps(value)

    async def _execute(conn: asyncpg.Connection) -> None:
        # Timeouts and synchronous_commit are configured at session level via pool init.
        await conn.execute(
            """
            WITH params AS (
                SELECT CASE WHEN $3::int IS NULL THEN NULL ELSE NOW() + ($3::int || ' seconds')::interval END AS exp_ts
            )
            INSERT INTO persistpg_kv(k, v, exp)
            SELECT $1::text, $2::jsonb, p.exp_ts FROM params p
            ON CONFLICT (k) DO UPDATE SET
                v = EXCLUDED.v,
                exp = COALESCE(EXCLUDED.exp, persistpg_kv.exp)
            WHERE persistpg_kv.v IS DISTINCT FROM EXCLUDED.v
               OR COALESCE(EXCLUDED.exp, persistpg_kv.exp) IS DISTINCT FROM persistpg_kv.exp
            """,
            key,
            payload,
            expire,
        )

    for attempt in range(SET_MAX_RETRIES):
        try:
            async with pool.acquire() as conn:
                await _execute(conn)
            break
        except asyncpg.PostgresError as e:
            sqlstate = getattr(e, "sqlstate", None)
            if sqlstate in {"55P03", "40001", "40P01"} and attempt + 1 < SET_MAX_RETRIES:
                backoff_ms = SET_RETRY_BASE_MS * (2 ** attempt) + random.randint(0, SET_RETRY_BASE_MS)
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            raise

    return True