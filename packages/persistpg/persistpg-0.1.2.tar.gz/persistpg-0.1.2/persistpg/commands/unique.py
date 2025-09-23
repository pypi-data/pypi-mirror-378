from __future__ import annotations

from typing import Optional

import asyncpg

__all__ = ["reserve_unique", "release_unique", "get_unique_key"]


async def reserve_unique(
    pool: asyncpg.Pool,
    collection: str,
    field: str,
    value: str,
    key: str,
) -> bool:
    """Reserve a unique (collection, field, value) mapping to a key.

    Returns True if reserved, False if already taken by a different key.

    Args:
        pool: asyncpg connection pool.
        collection: Logical collection/index name.
        field: Field name inside the collection.
        value: Field value to reserve.
        key: The key that claims the unique triplet.

    Returns:
        True if the reservation is owned by this key, False otherwise.
    """
    async with pool.acquire() as conn:
        ok = await conn.fetchval(
            """
            INSERT INTO persistpg_unique(collection, field, value, k)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (collection, field, value) DO UPDATE SET k = persistpg_unique.k
            RETURNING CASE WHEN k = $4 THEN 1 ELSE NULL END
            """,
            collection,
            field,
            value,
            key,
        )
    return bool(ok)


async def release_unique(pool: asyncpg.Pool, collection: str, field: str, value: str, key: str) -> bool:
    """Release a unique reservation owned by the given key."""
    async with pool.acquire() as conn:
        ok = await conn.fetchval(
            """
            DELETE FROM persistpg_unique WHERE collection = $1 AND field = $2 AND value = $3 AND k = $4
            RETURNING 1
            """,
            collection,
            field,
            value,
            key,
        )
    return bool(ok)


async def get_unique_key(pool: asyncpg.Pool, collection: str, field: str, value: str) -> Optional[str]:
    """Return the key that currently holds the (collection, field, value) reservation, or None."""
    async with pool.acquire() as conn:
        k = await conn.fetchval(
            """
            SELECT k FROM persistpg_unique WHERE collection = $1 AND field = $2 AND value = $3
            """,
            collection,
            field,
            value,
        )
    return k