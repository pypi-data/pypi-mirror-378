from __future__ import annotations

import asyncpg

__all__ = ["exists_key"]


async def exists_key(pool: asyncpg.Pool, key: str) -> bool:
    """Check if a key exists and hasn't expired.

    Args:
        pool: asyncpg connection pool.
        key: Key to check.

    Returns:
        True if exists and not expired, False otherwise.
    """
    async with pool.acquire() as conn:
        exists = await conn.fetchval(
            """
            SELECT EXISTS(
                SELECT 1 FROM persistpg_kv WHERE k = $1 AND (exp IS NULL OR exp > NOW())
            )
            """,
            key,
        )
    return bool(exists)