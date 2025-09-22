from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

import os
import asyncio
from datetime import datetime, timedelta
import random

import asyncpg

from ..utils.serialization import dumps

__all__ = ["mset_values"]

# Tuning knobs for MSET contention and batching
MSET_LOCK_TIMEOUT_MS = int(os.getenv("PERSISTPG_MSET_LOCK_TIMEOUT_MS", "200"))  # per-tx lock timeout
MSET_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_MSET_STATEMENT_TIMEOUT_MS", "500"))  # optional per-tx statement timeout
MSET_MAX_RETRIES = int(os.getenv("PERSISTPG_MSET_MAX_RETRIES", "3"))
MSET_RETRY_BASE_MS = int(os.getenv("PERSISTPG_MSET_RETRY_BASE_MS", "25"))
MSET_COPY_THRESHOLD = int(os.getenv("PERSISTPG_MSET_COPY_THRESHOLD", "1000"))  # switch to TEMP+COPY when items exceed this
MSET_SYNC_COMMIT = os.getenv("PERSISTPG_MSET_SYNC_COMMIT", "on").lower()  # 'on' (default) or 'off'


async def mset_values(
    pool: asyncpg.Pool,
    items: Mapping[str, Any],
    expire: Optional[int] = None,
) -> int:
    """Set multiple key/value pairs in one roundtrip.

    Args:
        pool: asyncpg connection pool.
        items: Mapping of key->value.
        expire: Optional TTL (seconds) applied to all items; None keeps existing TTL per key.

    Returns:
        Count of keys written.
    """
    if not items:
        return 0

    keys = list(items.keys())
    # Keep JSON string payloads for consistent casting; avoids driver-side array type quirks
    values = [dumps(v) for v in items.values()]

    # We compute expiration timestamp once per statement on the server side using a CTE,
    # but we avoid per-row NOW()+interval cost by referencing a single exp_ts value.
    exp_seconds = expire  # may be None

    async def _execute(conn: asyncpg.Connection) -> None:
        if len(keys) >= MSET_COPY_THRESHOLD:
            # TEMP+COPY path for large batches
            await conn.execute(
                """
                CREATE TEMP TABLE IF NOT EXISTS tmp_mset (
                    k TEXT,
                    v_text TEXT,
                    exp TIMESTAMPTZ
                ) ON COMMIT DROP;
                TRUNCATE tmp_mset;
                """
            )
            # Build records: (k, json_text, exp_ts)
            # Compute exp_ts once in SQL to match server time; pass seconds and compute here
            exp_ts = None
            if exp_seconds is not None:
                # Use server time via NOW() + interval: compute once here by round-tripping
                exp_ts = await conn.fetchval(
                    "SELECT NOW() + ($1::int || ' seconds')::interval",
                    exp_seconds,
                )
            records = [(k, v, exp_ts) for k, v in zip(keys, values)]
            await conn.copy_records_to_table("tmp_mset", records=records)
            await conn.execute(
                """
                INSERT INTO persistpg_kv(k, v, exp)
                SELECT k, v_text::jsonb, exp FROM tmp_mset
                ON CONFLICT (k) DO UPDATE SET
                  v = EXCLUDED.v,
                  exp = COALESCE(EXCLUDED.exp, persistpg_kv.exp)
                WHERE persistpg_kv.v IS DISTINCT FROM EXCLUDED.v
                   OR COALESCE(EXCLUDED.exp, persistpg_kv.exp) IS DISTINCT FROM persistpg_kv.exp
                """
            )
        else:
            # UNNEST path for smaller batches
            await conn.execute(
                """
                WITH params AS (
                    SELECT CASE WHEN $3::int IS NULL THEN NULL ELSE NOW() + ($3::int || ' seconds')::interval END AS exp_ts
                ), data AS (
                    SELECT UNNEST($1::text[]) AS k, UNNEST($2::text[])::jsonb AS v
                )
                INSERT INTO persistpg_kv(k, v, exp)
                SELECT d.k, d.v, p.exp_ts
                FROM data d CROSS JOIN params p
                ON CONFLICT (k) DO UPDATE SET
                    v = EXCLUDED.v,
                    exp = COALESCE(EXCLUDED.exp, persistpg_kv.exp)
                WHERE persistpg_kv.v IS DISTINCT FROM EXCLUDED.v
                   OR COALESCE(EXCLUDED.exp, persistpg_kv.exp) IS DISTINCT FROM persistpg_kv.exp
                """,
                keys,
                values,
                exp_seconds,
            )

    # Retry on common concurrency errors to collapse p99
    for attempt in range(MSET_MAX_RETRIES):
        try:
            async with pool.acquire() as conn:
                if len(keys) >= MSET_COPY_THRESHOLD:
                    # Multi-statement path needs an explicit transaction
                    async with conn.transaction():
                        await _execute(conn)
                else:
                    # Single-statement path avoids extra BEGIN/COMMIT round-trips
                    await _execute(conn)
            break
        except asyncpg.PostgresError as e:
            # Lock not available, serialization failure, deadlock detected
            sqlstate = getattr(e, "sqlstate", None)
            if sqlstate in {"55P03", "40001", "40P01"} and attempt + 1 < MSET_MAX_RETRIES:
                backoff_ms = MSET_RETRY_BASE_MS * (2 ** attempt) + random.randint(0, MSET_RETRY_BASE_MS)
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            raise

    return len(keys)