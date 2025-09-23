from __future__ import annotations

import os
import asyncio
import random
import asyncpg

__all__ = ["incr_key"]

INCR_LOCK_TIMEOUT_MS = int(os.getenv("PERSISTPG_INCR_LOCK_TIMEOUT_MS", "200"))
INCR_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_INCR_STATEMENT_TIMEOUT_MS", "500"))
INCR_MAX_RETRIES = int(os.getenv("PERSISTPG_INCR_MAX_RETRIES", "2"))
INCR_RETRY_BASE_MS = int(os.getenv("PERSISTPG_INCR_RETRY_BASE_MS", "15"))
INCR_SYNC_COMMIT = os.getenv("PERSISTPG_INCR_SYNC_COMMIT", "on").lower()


async def incr_key(pool: asyncpg.Pool, key: str, amount: int = 1) -> int:
    """Atomically increment an integer value stored at key.

    If the key does not exist or holds a non-numeric value, it is treated as 0 before the operation.
    Expired keys are treated as non-existent.

    Args:
        pool: asyncpg connection pool.
        key: Key to increment.
        amount: Amount to add (default 1).

    Returns:
        The new integer value after increment.
    """

    async def _execute(conn: asyncpg.Connection) -> int:
        new_value = await conn.fetchval(
            """
            INSERT INTO persistpg_kv(k, v, exp)
            VALUES ($1, to_jsonb($2::bigint), NULL)
            ON CONFLICT (k) DO UPDATE SET
                v = to_jsonb(
                    (
                        CASE
                            WHEN persistpg_kv.exp IS NOT NULL AND persistpg_kv.exp <= NOW() THEN 0
                            WHEN jsonb_typeof(persistpg_kv.v) = 'number' THEN (persistpg_kv.v::text)::bigint
                            ELSE 0
                        END
                    ) + $2::bigint
                ),
                exp = CASE
                          WHEN persistpg_kv.exp IS NOT NULL AND persistpg_kv.exp <= NOW() THEN NULL
                          ELSE persistpg_kv.exp
                      END
            RETURNING (v::text)::bigint
            """,
            key,
            amount,
        )
        return int(new_value)

    for attempt in range(INCR_MAX_RETRIES):
        try:
            async with pool.acquire() as conn:
                return await _execute(conn)
        except asyncpg.PostgresError as e:
            sqlstate = getattr(e, "sqlstate", None)
            if sqlstate in {"55P03", "40001", "40P01"} and attempt + 1 < INCR_MAX_RETRIES:
                backoff_ms = INCR_RETRY_BASE_MS * (2 ** attempt) + random.randint(0, INCR_RETRY_BASE_MS)
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            raise

    # Should not reach here
    raise RuntimeError("incr_key retries exhausted without success")