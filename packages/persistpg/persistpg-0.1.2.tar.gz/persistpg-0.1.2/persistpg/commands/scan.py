from __future__ import annotations

from typing import List, Optional

import asyncpg

from ..utils.patterns import glob_to_like, LIKE_ESCAPE

__all__ = ["scan_keys"]


async def scan_keys(
    pool: asyncpg.Pool,
    pattern: str = "*",
    after: Optional[str] = None,
    limit: int = 100,
) -> List[str]:
    """Lexicographically scan keys matching a pattern.

    Args:
        pool: asyncpg connection pool.
        pattern: Glob-style pattern (default "*").
        after: Exclusive start key; only return keys greater than this value.
        limit: Max number of keys to return.

    Returns:
        Up to `limit` keys, ordered by key ascending.
    """
    like = glob_to_like(pattern)
    async with pool.acquire() as conn:
        if after is None:
            rows = await conn.fetch(
                f"""
                SELECT k FROM persistpg_kv
                WHERE (exp IS NULL OR exp > NOW()) AND k LIKE $1 ESCAPE '{LIKE_ESCAPE}'
                ORDER BY k
                LIMIT $2
                """,
                like,
                limit,
            )
        else:
            rows = await conn.fetch(
                f"""
                SELECT k FROM persistpg_kv
                WHERE (exp IS NULL OR exp > NOW()) AND k > $2 AND k LIKE $1 ESCAPE '{LIKE_ESCAPE}'
                ORDER BY k
                LIMIT $3
                """,
                like,
                after,
                limit,
            )
    return [r["k"] for r in rows]