from __future__ import annotations

from typing import List

import asyncpg

from ..utils.patterns import glob_to_like, LIKE_ESCAPE

__all__ = ["search_by_key", "search_by_value"]


async def search_by_key(pool: asyncpg.Pool, pattern: str = "*") -> List[str]:
    """Search keys by glob-style pattern, excluding expired keys.

    Args:
        pool: asyncpg connection pool.
        pattern: Glob-style key pattern (e.g., "user:*").

    Returns:
        List of matching keys.
    """
    like = glob_to_like(pattern)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT k FROM persistpg_kv
            WHERE (exp IS NULL OR exp > NOW()) AND k LIKE $1 ESCAPE '{LIKE_ESCAPE}'
            ORDER BY k
            """,
            like,
        )
    return [r["k"] for r in rows]


async def search_by_value(pool: asyncpg.Pool, needle: str) -> List[str]:
    """Search keys whose JSON value contains the given text (case-insensitive).

    This performs a substring search on the serialized JSON text. It's simple
    and works across PostgreSQL versions. For exact field matches, consider
    higher-level helpers (e.g., client.find(collection, field, value)).

    Args:
        pool: asyncpg connection pool.
        needle: Substring to search for within the JSON value.

    Returns:
        List of keys whose values contain the substring.
    """
    # Escape LIKE wildcards to ensure literal match and wrap with % for substring search
    esc = LIKE_ESCAPE
    pattern = "%" + needle.replace(esc, esc + esc).replace("%", esc + "%").replace("_", esc + "_") + "%"
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT k FROM persistpg_kv
            WHERE (exp IS NULL OR exp > NOW()) AND v::text ILIKE $1 ESCAPE '{LIKE_ESCAPE}'
            ORDER BY k
            """,
            pattern,
        )
    return [r["k"] for r in rows]