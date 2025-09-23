from __future__ import annotations

import asyncpg

from .incr import incr_key

__all__ = ["decr_key"]


async def decr_key(pool: asyncpg.Pool, key: str, amount: int = 1) -> int:
    """Atomically decrement an integer value stored at key.

    Args:
        pool: asyncpg connection pool.
        key: Key to decrement.
        amount: Amount to subtract (default 1).

    Returns:
        The new integer value after decrement.
    """
    # Reuse increment logic with negative amount for minimal overhead.
    return await incr_key(pool, key, -abs(amount))