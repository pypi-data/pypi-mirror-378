from __future__ import annotations

import asyncpg

__all__ = ["expire_key"]


async def expire_key(pool: asyncpg.Pool, key: str, seconds: int) -> bool:
    """Set a TTL on a key.

    Args:
        pool: asyncpg connection pool.
        key: Key to expire.
        seconds: TTL in seconds.

    Returns:
        True if TTL was set, False otherwise.
    """
    async with pool.acquire() as conn:
        changed = await conn.fetchval(
            """
            WITH upd AS (
                UPDATE persistpg_kv
                SET exp = NOW() + ($2::int || ' seconds')::interval
                WHERE k = $1 AND (exp IS NULL OR exp > NOW())
                RETURNING 1
            ) SELECT COUNT(*) FROM upd
            """,
            key,
            seconds,
        )
    return bool(changed)