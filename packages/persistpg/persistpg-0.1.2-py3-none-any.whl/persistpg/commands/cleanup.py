from __future__ import annotations

from typing import Optional

import asyncpg

__all__ = ["sweep_expired"]


async def sweep_expired(pool: asyncpg.Pool, *, batch_size: int = 1000) -> int:
    """Delete a batch of expired keys.

    This function deletes up to `batch_size` rows whose exp <= NOW(). It
    uses the primary key for deletion to work with both regular and
    partitioned tables.

    Returns the number of deleted rows in this batch.
    """
    async with pool.acquire() as conn:
        # Select a batch of expired keys ordered by oldest expiration first
        rows = await conn.fetch(
            """
            SELECT k
            FROM persistpg_kv
            WHERE exp IS NOT NULL AND exp <= NOW()
            ORDER BY exp
            LIMIT $1
            """,
            batch_size,
        )
        if not rows:
            return 0
        keys = [r["k"] for r in rows]
        # Delete using primary key; return number of deleted rows
        deleted = await conn.fetchval(
            """
            WITH del AS (
                DELETE FROM persistpg_kv WHERE k = ANY($1::text[])
                RETURNING 1
            )
            SELECT COUNT(*) FROM del
            """,
            keys,
        )
        return int(deleted)