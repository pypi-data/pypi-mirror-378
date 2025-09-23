from __future__ import annotations

from typing import Tuple

import asyncpg

__all__ = ["rate_limit_take"]


async def rate_limit_take(pool: asyncpg.Pool, key: str, limit: int, window_seconds: int) -> Tuple[bool, int, int]:
    """Consume 1 token from a simple fixed-window rate limiter.

    Returns (allowed, remaining, reset_seconds).
    Uses the KV table: count stored as JSON number, exp used as window end.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO persistpg_kv(k, v, exp)
            VALUES (
                $1,
                to_jsonb(1),
                NOW() + ($2::int || ' seconds')::interval
            )
            ON CONFLICT (k) DO UPDATE SET
                v = to_jsonb(
                    CASE
                        WHEN persistpg_kv.exp IS NOT NULL AND persistpg_kv.exp > NOW() THEN ((persistpg_kv.v::text)::bigint + 1)
                        ELSE 1
                    END
                ),
                exp = CASE
                        WHEN persistpg_kv.exp IS NOT NULL AND persistpg_kv.exp > NOW() THEN persistpg_kv.exp
                        ELSE NOW() + ($2::int || ' seconds')::interval
                      END
            RETURNING (v::text)::bigint AS count,
                      EXTRACT(EPOCH FROM (exp - NOW()))::int AS reset
            """,
            key,
            window_seconds,
        )
    count = int(row["count"]) if row else 0
    reset = max(int(row["reset"]) if row else 0, 0)
    remaining = max(limit - count, 0)
    allowed = count <= limit
    return allowed, remaining, reset