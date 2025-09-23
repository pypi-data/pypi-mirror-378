from __future__ import annotations

from typing import Any, List

import asyncpg

from ..utils.patterns import glob_to_like, LIKE_ESCAPE

__all__ = ["find_keys_by_field"]


async def find_keys_by_field(pool: asyncpg.Pool, collection: str, field: str, value: Any) -> List[str]:
    """Find keys under a collection where JSON field equals the provided value.

    This assumes a key naming convention like "{collection}:{id}".

    Args:
        pool: asyncpg connection pool.
        collection: Logical collection/prefix (e.g., "user" maps to keys like "user:*").
        field: JSON field name to match.
        value: Value to match; compared using text form (v ->> field = value::text).

    Returns:
        List of keys matching the condition.
    """
    like = glob_to_like(f"{collection}:*")
    # Compare as text for broad compatibility; callers can pass strings (e.g., "42") for numeric equality too
    val_text = str(value)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT k FROM persistpg_kv
            WHERE (exp IS NULL OR exp > NOW())
              AND k LIKE $1 ESCAPE '{LIKE_ESCAPE}'
              AND v ->> $2 = $3
            ORDER BY k
            """,
            like,
            field,
            val_text,
        )
    return [r["k"] for r in rows]