from __future__ import annotations

import asyncpg
import os

__all__ = ["create_pool", "ensure_schema"]

POOL_STATEMENT_CACHE_SIZE = int(os.getenv("PERSISTPG_STATEMENT_CACHE_SIZE", "1000"))
POOL_MAX_QUERIES = int(os.getenv("PERSISTPG_POOL_MAX_QUERIES", "50000"))
POOL_MAX_INACTIVE_CONN_LIFETIME = float(os.getenv("PERSISTPG_POOL_MAX_INACTIVE_LIFETIME", "300"))
KV_PARTITIONS = int(os.getenv("PERSISTPG_KV_PARTITIONS", "0"))

# Session-level defaults to reduce per-call SET LOCAL overhead
SESSION_LOCK_TIMEOUT_MS = int(os.getenv("PERSISTPG_SESSION_LOCK_TIMEOUT_MS", "200"))
SESSION_STMT_TIMEOUT_MS = int(os.getenv("PERSISTPG_SESSION_STATEMENT_TIMEOUT_MS", "500"))
SESSION_SYNC_COMMIT = os.getenv("PERSISTPG_SESSION_SYNC_COMMIT", "on").lower()


async def _init_connection(conn: asyncpg.Connection) -> None:
    # Apply session defaults once per connection
    if SESSION_LOCK_TIMEOUT_MS > 0:
        await conn.execute(f"SET lock_timeout = '{SESSION_LOCK_TIMEOUT_MS}ms'")
    if SESSION_STMT_TIMEOUT_MS > 0:
        await conn.execute(f"SET statement_timeout = '{SESSION_STMT_TIMEOUT_MS}ms'")
    if SESSION_SYNC_COMMIT in ("off", "false", "0"):
        await conn.execute("SET synchronous_commit = 'off'")
    else:
        await conn.execute("SET synchronous_commit = 'on'")


async def create_pool(url: str, *, min_size: int = 1, max_size: int = 10) -> asyncpg.Pool:
    """Create an asyncpg connection pool.

    Args:
        url: PostgreSQL connection URL.
        min_size: Minimum number of connections in the pool.
        max_size: Maximum number of connections in the pool.

    Returns:
        An initialized asyncpg.Pool instance.
    """
    return await asyncpg.create_pool(
        dsn=url,
        min_size=min_size,
        max_size=max_size,
        statement_cache_size=POOL_STATEMENT_CACHE_SIZE,
        max_queries=POOL_MAX_QUERIES,
        max_inactive_connection_lifetime=POOL_MAX_INACTIVE_CONN_LIFETIME,
        init=_init_connection,
    )


async def ensure_schema(pool: asyncpg.Pool) -> None:
    """Ensure the required schema (table and index) exists.

    Also applies performance-related storage parameters if possible.
    """
    async with pool.acquire() as conn:
        # If hash partitioning is requested and table doesn't exist, create partitioned parent
        if KV_PARTITIONS > 0:
            exists = await conn.fetchval("SELECT to_regclass('public.persistpg_kv') IS NOT NULL")
            if not exists:
                await conn.execute(
                    f"""
                    CREATE TABLE public.persistpg_kv (
                        k   TEXT NOT NULL,
                        v   JSONB NOT NULL,
                        exp TIMESTAMPTZ NULL,
                        PRIMARY KEY (k)
                    ) PARTITION BY HASH (k);
                    CREATE INDEX IF NOT EXISTS persistpg_kv_exp_idx ON public.persistpg_kv (exp);
                    """
                )
                for i in range(KV_PARTITIONS):
                    await conn.execute(
                        f"CREATE TABLE IF NOT EXISTS public.persistpg_kv_p{i} PARTITION OF public.persistpg_kv FOR VALUES WITH (MODULUS {KV_PARTITIONS}, REMAINDER {i});"
                    )
            else:
                # If table exists but is not partitioned and empty, migrate to partitioned table
                is_partitioned = await conn.fetchval(
                    """
                    SELECT c.relkind = 'p'
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'public' AND c.relname = 'persistpg_kv'
                    """
                )
                if not is_partitioned:
                    rowcount = await conn.fetchval("SELECT COUNT(*) FROM public.persistpg_kv")
                    if int(rowcount or 0) == 0:
                        # Safe to migrate by rename -> create partitioned -> drop old
                        await conn.execute("ALTER TABLE public.persistpg_kv RENAME TO persistpg_kv_old")
                        await conn.execute(
                            """
                            CREATE TABLE public.persistpg_kv (
                                k   TEXT NOT NULL,
                                v   JSONB NOT NULL,
                                exp TIMESTAMPTZ NULL,
                                PRIMARY KEY (k)
                            ) PARTITION BY HASH (k);
                            CREATE INDEX IF NOT EXISTS persistpg_kv_exp_idx ON public.persistpg_kv (exp);
                            """
                        )
                        for i in range(KV_PARTITIONS):
                            await conn.execute(
                                f"CREATE TABLE IF NOT EXISTS public.persistpg_kv_p{i} PARTITION OF public.persistpg_kv FOR VALUES WITH (MODULUS {KV_PARTITIONS}, REMAINDER {i});"
                            )
                        # Drop the old empty table
                        await conn.execute("DROP TABLE IF EXISTS public.persistpg_kv_old")
        # Ensure base tables exist if they weren't created above
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS persistpg_kv (
                k   TEXT PRIMARY KEY,
                v   JSONB NOT NULL,
                exp TIMESTAMPTZ NULL
            );
            CREATE INDEX IF NOT EXISTS persistpg_kv_exp_idx ON persistpg_kv (exp);

            -- Lightweight distributed locks table
            CREATE TABLE IF NOT EXISTS persistpg_locks (
                k     TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                until TIMESTAMPTZ NOT NULL
            );
            CREATE INDEX IF NOT EXISTS persistpg_locks_until_idx ON persistpg_locks (until);

            -- Uniqueness reservation table (for unique field helpers)
            CREATE TABLE IF NOT EXISTS persistpg_unique (
                collection TEXT NOT NULL,
                field      TEXT NOT NULL,
                value      TEXT NOT NULL,
                k          TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (collection, field, value)
            );
            """
        )
        # Apply fillfactor to reduce page splits and enable more HOT updates when possible
        # (No-op if already set to target value)
        await conn.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                    WHERE n.nspname = 'public' AND c.relname = 'persistpg_kv' AND c.relkind IN ('r','p')
                ) THEN
                    EXECUTE 'ALTER TABLE public.persistpg_kv SET (fillfactor = 90)';
                END IF;
                IF EXISTS (
                    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                    WHERE n.nspname = 'public' AND c.relname = 'persistpg_kv_pkey' AND c.relkind = 'i'
                ) THEN
                    EXECUTE 'ALTER INDEX public.persistpg_kv_pkey SET (fillfactor = 90)';
                END IF;
            END$$;
            """
        )