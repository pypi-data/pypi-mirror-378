from __future__ import annotations

from typing import Any, Optional

import os
import asyncio
import random
import asyncpg

from ..utils.serialization import dumps

__all__ = ["setnx_key"]

SETNX_LOCK_TIMEOUT_MS = int(os.getenv("PERSISTPG_SETNX_LOCK_TIMEOUT_MS", "200"))
SETNX_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_SETNX_STATEMENT_TIMEOUT_MS", "500"))
SETNX_MAX_RETRIES = int(os.getenv("PERSISTPG_SETNX_MAX_RETRIES", "2"))
SETNX_RETRY_BASE_MS = int(os.getenv("PERSISTPG_SETNX_RETRY_BASE_MS", "15"))
SETNX_SYNC_COMMIT = os.getenv("PERSISTPG_SETNX_SYNC_COMMIT", "on").lower()


async def setnx_key(pool: asyncpg.Pool, key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Set key only if it does not already exist or is expired, with optional TTL.

    Args:
        pool: asyncpg connection pool.
        key: Key to set.
        value: JSON-serializable value.
        expire: Optional TTL in seconds.

    Returns:
        True if the key was set, False if it already existed and was not expired.
    """
    payload = dumps(value)

    async def _execute(conn: asyncpg.Connection) -> bool:
        changed = await conn.fetchval(
            """
            WITH params AS (
                SELECT CASE WHEN $3::int IS NULL THEN NULL ELSE NOW() + ($3::int || ' seconds')::interval END AS exp_ts
            )
            INSERT INTO persistpg_kv(k, v, exp)
            SELECT $1::text, $2::jsonb, p.exp_ts FROM params p
            ON CONFLICT (k) DO UPDATE SET
                v = EXCLUDED.v,
                exp = EXCLUDED.exp
            WHERE persistpg_kv.exp IS NOT NULL AND persistpg_kv.exp <= NOW()
            RETURNING 1
            """,
            key,
            payload,
            expire,
        )
        return bool(changed)

    for attempt in range(SETNX_MAX_RETRIES):
        try:
            async with pool.acquire() as conn:
                return await _execute(conn)
        except asyncpg.PostgresError as e:
            sqlstate = getattr(e, "sqlstate", None)
            if sqlstate in {"55P03", "40001", "40P01"} and attempt + 1 < SETNX_MAX_RETRIES:
                backoff_ms = SETNX_RETRY_BASE_MS * (2 ** attempt) + random.randint(0, SETNX_RETRY_BASE_MS)
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            raise

    return False