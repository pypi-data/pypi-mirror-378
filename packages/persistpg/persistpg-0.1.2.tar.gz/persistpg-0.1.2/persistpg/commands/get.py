from __future__ import annotations

from typing import Any, Optional

import os
import asyncpg

from ..utils.serialization import loads

__all__ = ["get_value"]

GET_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_GET_STATEMENT_TIMEOUT_MS", "500"))


async def get_value(pool: asyncpg.Pool, key: str) -> Optional[Any]:
    """Retrieve the value of a key if it exists and hasn't expired.

    Args:
        pool: asyncpg connection pool.
        key: Key to fetch.

    Returns:
        The value if exists, otherwise None.
    """
    async with pool.acquire() as conn:
        data = await conn.fetchval(
            """
            SELECT v::text
            FROM persistpg_kv
            WHERE k = $1 AND (exp IS NULL OR exp > NOW())
            """,
            key,
        )
    return loads(data) if data is not None else None