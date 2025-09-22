from __future__ import annotations

import asyncpg

__all__ = ["ttl_key"]


async def ttl_key(pool: asyncpg.Pool, key: str) -> int:
    """Get remaining TTL in seconds.

    Args:
        pool: asyncpg connection pool.
        key: Key to check.

    Returns:
        Remaining seconds, -1 if no TTL, -2 if key doesn't exist.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            SELECT exp,
                   CASE
                       WHEN exp IS NULL THEN -1
                       WHEN exp <= NOW() THEN -2
                       ELSE CEIL(EXTRACT(EPOCH FROM exp - NOW()))::int
                   END AS ttl
            FROM persistpg_kv
            WHERE k = $1
            """,
            key,
        )
    if result is None:
        return -2
    return int(result["ttl"])