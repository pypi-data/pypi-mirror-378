from __future__ import annotations

from typing import Any, Iterable, List, Optional

import os
import asyncpg

from ..utils.serialization import loads

__all__ = ["mget_values"]

MGET_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_MGET_STATEMENT_TIMEOUT_MS", "500"))


async def mget_values(pool: asyncpg.Pool, keys: Iterable[str]) -> List[Optional[Any]]:
    """Get multiple keys in one roundtrip, preserving input order.

    Args:
        pool: asyncpg connection pool.
        keys: Iterable of keys.

    Returns:
        List of values aligned with input order. Missing or expired keys yield None.
    """
    ks = list(keys)
    if not ks:
        return []

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT k, v::text AS payload
            FROM persistpg_kv
            WHERE k = ANY($1::text[]) AND (exp IS NULL OR exp > NOW())
            """,
            ks,
        )
    data_map = {r["k"]: r["payload"] for r in rows}
    out: List[Optional[Any]] = []
    for k in ks:
        payload = data_map.get(k)
        out.append(loads(payload) if payload is not None else None)
    return out