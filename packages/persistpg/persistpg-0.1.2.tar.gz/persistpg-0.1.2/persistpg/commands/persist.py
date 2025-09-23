from __future__ import annotations

import asyncpg

__all__ = ["persist_key"]


async def persist_key(pool: asyncpg.Pool, key: str) -> bool:
    """Remove the TTL from a key (make it persistent)."""
    async with pool.acquire() as conn:
        changed = await conn.fetchval(
            """
            WITH upd AS (
                UPDATE persistpg_kv
                SET exp = NULL
                WHERE k = $1 AND (exp IS NOT NULL AND exp > NOW())
                RETURNING 1
            ) SELECT COUNT(*) FROM upd
            """,
            key,
        )
    return bool(changed)