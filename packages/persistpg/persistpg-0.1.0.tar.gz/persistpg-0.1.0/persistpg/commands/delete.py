from __future__ import annotations

from typing import Iterable

import asyncpg

__all__ = ["delete_keys"]


async def delete_keys(pool: asyncpg.Pool, keys: Iterable[str]) -> int:
    """Delete one or multiple keys.

    Args:
        pool: asyncpg connection pool.
        keys: Iterable of keys to delete.

    Returns:
        The number of deleted keys.
    """
    ks = tuple(keys)
    if not ks:
        return 0

    async with pool.acquire() as conn:
        if len(ks) == 1:
            deleted = await conn.fetchval(
                """
                WITH del AS (
                    DELETE FROM persistpg_kv WHERE k = $1 RETURNING 1
                ) SELECT COUNT(*) FROM del
                """,
                ks[0],
            )
        else:
            deleted = await conn.fetchval(
                """
                WITH del AS (
                    DELETE FROM persistpg_kv WHERE k = ANY($1::text[]) RETURNING 1
                ) SELECT COUNT(*) FROM del
                """,
                ks,
            )
    return int(deleted)