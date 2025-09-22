from __future__ import annotations

import asyncpg

__all__ = ["flush_all"]


async def flush_all(pool: asyncpg.Pool) -> bool:
    """Remove all keys from storage (like Redis FLUSHALL).

    Args:
        pool: asyncpg connection pool.

    Returns:
        True if operation succeeds.
    """
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE persistpg_kv")
    return True