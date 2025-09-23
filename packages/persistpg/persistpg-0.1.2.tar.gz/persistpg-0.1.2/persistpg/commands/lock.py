from __future__ import annotations

import uuid
from typing import Optional, Tuple

import asyncpg

__all__ = ["acquire_lock", "release_lock", "renew_lock"]


async def acquire_lock(
    pool: asyncpg.Pool, key: str, ttl_seconds: int, owner: Optional[str] = None
) -> Optional[str]:
    """Try to acquire a distributed lock.

    Returns owner token if acquired, None if someone else holds it.
    Expired locks are treated as free.

    Args:
        pool: asyncpg connection pool.
        key: Lock name.
        ttl_seconds: Lock TTL in seconds.
        owner: Optional owner token. If not provided a random UUID is used.

    Returns:
        The owner token if acquired, otherwise None.
    """
    token = owner or str(uuid.uuid4())
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO persistpg_locks(k, owner, until)
            VALUES ($1, $2, NOW() + ($3::int || ' seconds')::interval)
            ON CONFLICT (k) DO UPDATE SET
                owner = CASE WHEN persistpg_locks.until <= NOW() THEN EXCLUDED.owner ELSE persistpg_locks.owner END,
                until = CASE WHEN persistpg_locks.until <= NOW() THEN EXCLUDED.until ELSE persistpg_locks.until END
            RETURNING CASE WHEN until > NOW() AND owner = $2 THEN owner ELSE NULL END AS acquired_owner,
                      owner AS current_owner,
                      until
            """,
            key,
            token,
            ttl_seconds,
        )
    if row and row["acquired_owner"]:
        return token
    return None


async def renew_lock(pool: asyncpg.Pool, key: str, owner: str, ttl_seconds: int) -> bool:
    """Extend a lock if still held by the owner.

    Args:
        pool: asyncpg connection pool.
        key: Lock name.
        owner: Owner token that currently holds the lock.
        ttl_seconds: New TTL in seconds.

    Returns:
        True if renewed, False otherwise.
    """
    async with pool.acquire() as conn:
        ok = await conn.fetchval(
            """
            UPDATE persistpg_locks
            SET until = NOW() + ($3::int || ' seconds')::interval
            WHERE k = $1 AND owner = $2 AND until > NOW()
            RETURNING 1
            """,
            key,
            owner,
            ttl_seconds,
        )
    return bool(ok)


async def release_lock(pool: asyncpg.Pool, key: str, owner: str) -> bool:
    """Release a lock if held by the given owner.

    Args:
        pool: asyncpg connection pool.
        key: Lock name.
        owner: Owner token that holds the lock.

    Returns:
        True if released, False otherwise.
    """
    async with pool.acquire() as conn:
        ok = await conn.fetchval(
            """
            DELETE FROM persistpg_locks WHERE k = $1 AND owner = $2
            RETURNING 1
            """,
            key,
            owner,
        )
    return bool(ok)