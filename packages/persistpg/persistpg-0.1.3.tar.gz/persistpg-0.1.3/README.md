# PersistPG

A fast, Redis-like key/value store built on PostgreSQL and asyncpg. PersistPG provides a familiar, minimalist API (inspired by redis-py) while storing values durably in PostgreSQL JSONB with excellent performance.

- Async-first client using asyncpg connection pooling
- JSON values with transparent serialization/deserialization
- TTL support, persist/unset TTL
- Atomic operations (INCR/DECR/SETNX) via single-statement upserts
- Bulk operations (MGET/MSET) optimized for minimal roundtrips
- Key search and scanning with glob patterns
- Simple namespacing for multi-tenant isolation
- Unique reservations (e.g., username/email uniqueness)
- Lightweight distributed locks
- Fixed-window rate limiter

No manual migrations required; the schema is ensured on first use.

## Table of Contents
- Requirements
- Installation
- Quick Start
- API Overview
- Namespaces
- Serialization Model
- TTL and Expiration Semantics
- Performance Notes
- Benchmarks
- Configuration (Environment Variables)
- Error Handling
- FAQ
- License

## Requirements
- Python >= 3.10
- PostgreSQL 12+ recommended (9.6+ may work)
- asyncpg (see requirements.txt)

Optional:
- orjson for faster JSON (fallback to built-in json if unavailable)

## Installation

Install from PyPI:

```bash
pip install persistpg
```

Or install directly from the repository:

```bash
pip install -r requirements.txt
```

Or install as a package after building locally:

```bash
pip install .
```

## Quick Start

Using context manager (recommended):

```python
import asyncio
from persistpg import PersistPGClient, By

DSN = "postgresql://user:password@localhost:5432/mydb"

async def main():
    async with PersistPGClient(DSN) as client:
        await client.set("greeting", {"msg": "hello"})
        print(await client.get("greeting"))  # {'msg': 'hello'}

        await client.expire("greeting", 60)
        print(await client.ttl("greeting"))

        print(await client.incr("counter"))       # 1
        print(await client.decr("counter", 2))    # -1

        # Bulk
        await client.mset({"a": 1, "b": 2})
        print(await client.mget("a", "b", "c"))  # [1, 2, None]

        # Search & scan
        print(await client.search(By.KEY, "g*"))
        print(await client.scan(pattern="*", limit=50))

        # Conditional set only if missing/expired
        await client.setnx("once", {"x": 1})

        # Namespaced operations
        ns = client.ns("tenant1")
        await ns.set("user:1", {"name": "Layla"})
        print(await ns.get("user:1"))

        # Unique reservation
        reserved = await client.unique_reserve("user", "username", "layla", key="user:1")
        if reserved:
            owner = await client.unique_get("user", "username", "layla")
            print("owner:", owner)
            await client.unique_release("user", "username", "layla", key="user:1")

        # Distributed lock
        token = await client.lock_acquire("job:cleanup", ttl_seconds=30)
        if token:
            try:
                # do work
                pass
            finally:
                await client.lock_release("job:cleanup", token)

        # Fixed-window rate limit
        allowed, remaining, reset = await client.rate_limit("api:ip:127.0.0.1", limit=100, window_seconds=60)
        print(allowed, remaining, reset)

asyncio.run(main())
```

Alternative explicit construction (non-context manager):

```python
import asyncio
from persistpg import PersistPGClient

async def main():
    db = PersistPGClient(url="postgresql://postgres:postgres@localhost:5432/mydb")
    try:
        # Ensure pool/schema on first use
        await db.set("k", {"v": 1})
        print(await db.get("k"))
    finally:
        await db.close()

asyncio.run(main())
```

## API Overview

Client methods (non-exhaustive):
- set(key, value, expire=None) -> bool
- get(key) -> Any | None
- delete(*keys) -> int
- exists(key) -> bool
- expire(key, seconds) -> bool
- ttl(key) -> int  (-1 no TTL, -2 missing)
- incr(key, amount=1) -> int
- decr(key, amount=1) -> int
- mset(dict, expire=None) -> int
- mget(*keys) -> list[Any | None]
- setnx(key, value, expire=None) -> bool  (set when missing or expired)
- search(By.KEY, pattern) -> list[str]
- search(By.VALUE, needle) -> list[str]
- scan(pattern="*", after=None, limit=100) -> list[str]
- find(collection, field, value) -> list[str]
- persist(key) -> bool
- unique_reserve(collection, field, value, key) -> bool
- unique_release(collection, field, value, key) -> bool
- unique_get(collection, field, value) -> str | None
- lock_acquire(key, ttl_seconds, owner=None) -> str | None
- lock_renew(key, owner, ttl_seconds) -> bool
- lock_release(key, owner) -> bool
- rate_limit(key, limit, window_seconds) -> tuple[bool, int, int]
+ rate_limit(key, limit, window_seconds) -> tuple[bool, int, int]
+ start_expiry_sweeper(interval_seconds=30.0, batch_size=1000) -> None
+ stop_expiry_sweeper() -> None
 
 See inline docstrings in persistpg/client.py for full parameter details.

## Namespaces

Use client.ns("namespace") to get a namespaced client whose methods automatically prefix keys with "namespace:". Helpful for multi-tenant isolation or separating subsystems.

## Serialization Model

- Values are stored as JSONB. The library serializes via persistpg.utils.serialization.dumps and deserializes with loads.
- If orjson is installed, dumps/loads will use it; otherwise they fall back to Python’s json module.
- Store only JSON-serializable data. For binary data, encode it (e.g., base64) before storing.

## TTL and Expiration Semantics

- Expired keys are filtered out on reads; there is no background deletion job.
- ttl(key) returns seconds until expiration, -1 if persistent, -2 if missing.
- persist(key) removes TTL.

+### Expiry Sweeper
+
+- Auto-starts by default in both usage modes (context manager and explicit) immediately after the connection pool is initialized.
+- Configure via constructor parameters: sweeper_interval_seconds (default 30.0s) and sweeper_batch_size (default 1000).
+- Disable auto-start with auto_start_sweeper=False, and start manually via start_expiry_sweeper(...). You can call start_expiry_sweeper again to change settings; it restarts immediately to apply the new interval/batch.
+
+Examples
+
+Context manager (auto-start with custom settings):
+
+```python
+async with PersistPGClient(
+    "postgresql://user:password@localhost:5432/mydb",
+    sweeper_interval_seconds=0.5,
+    sweeper_batch_size=200,
+) as client:
+    ...
+```
+
+Explicit usage (auto-start enabled by default):
+
+```python
+db = PersistPGClient(
+    url="postgresql://postgres:postgres@localhost:5432/mydb",
+    sweeper_interval_seconds=1.0,
+    sweeper_batch_size=500,
+)
+# First operation will initialize the pool and auto-start the sweeper
+await db.set("k", {"v": 1}, expire=10)
+```
+
+Explicit usage with manual control:
+
+```python
+db = PersistPGClient(
+    url="postgresql://postgres:postgres@localhost:5432/mydb",
+    auto_start_sweeper=False,
+)
+await db.start_expiry_sweeper(interval_seconds=0.5, batch_size=200)
+...
+await db.stop_expiry_sweeper()
+await db.close()
+```

## Performance Notes

- Bulk writes (mset) choose an optimized path:
  - Small batches: minimal roundtrips without explicit transactions to reduce tail latency.
  - Large batches: use a temporary table + COPY within a single transaction.
- Single-statement SQL with ON CONFLICT for atomic operations (set, incr/decr, setnx).
- Session-level timeouts (lock_timeout, statement_timeout, synchronous_commit) are applied once per connection for efficiency.

## Benchmarks

Command: `python bench.py --duration 2 --concurrency 10 --keys 1000 --batch 5 --client both`

| Case           | ops/s | avg (ms) | p50 (ms) | p95 (ms) | p99 (ms) | success | errors | duration |
|----------------|------:|---------:|---------:|---------:|---------:|--------:|-------:|---------:|
| persistpg:set  |  3098 |     3.23 |     3.12 |     4.07 |     5.52 |    6202 |      0 |   2.00s  |
| persistpg:get  |  5061 |     1.97 |     1.96 |     2.35 |     2.59 |   10128 |      0 |   2.00s  |
| persistpg:mset |  3001 |     3.33 |     3.18 |     4.58 |     5.62 |    6008 |      0 |   2.00s  |
| persistpg:mget |  4692 |     2.13 |     2.12 |     2.53 |     2.78 |    9389 |      0 |   2.00s  |
| persistpg:incr |  3205 |     3.12 |     3.04 |     3.87 |     4.68 |    6416 |      0 |   2.00s  |
| asyncpg:set    |  3300 |     3.03 |     3.00 |     3.54 |     3.96 |    6607 |      0 |   2.00s  |
| asyncpg:get    |  5106 |     1.96 |     1.94 |     2.41 |     2.59 |   10217 |      0 |   2.00s  |
| asyncpg:mset   |  3047 |     3.28 |     3.14 |     4.55 |     5.53 |    6104 |      0 |   2.00s  |
| asyncpg:mget   |  4832 |     2.07 |     2.05 |     2.49 |     2.84 |    9671 |      0 |   2.00s  |
| asyncpg:incr   |  3257 |     3.07 |     3.02 |     3.62 |     4.15 |    6524 |      0 |   2.00s  |

Notes:
- Benchmarks executed on the same machine and DSN for fair comparison.
- Throughput and latency are comparable to raw asyncpg, with minor overhead for JSON handling and TTL logic.
- Real-world performance depends on hardware, network, indexes, and workload patterns.

## Configuration (Environment Variables)

Session defaults (applied once per connection):
- PERSISTPG_SESSION_LOCK_TIMEOUT_MS (default 200)
- PERSISTPG_SESSION_STATEMENT_TIMEOUT_MS (default 500)
- PERSISTPG_SESSION_SYNC_COMMIT ("on" or "off")

Operation-specific tuning (some highlights; see code for full list):
- PERSISTPG_SET_MAX_RETRIES, PERSISTPG_SET_RETRY_BASE_MS
- PERSISTPG_INCR_MAX_RETRIES, PERSISTPG_INCR_RETRY_BASE_MS
- PERSISTPG_MGET_STATEMENT_TIMEOUT_MS, PERSISTPG_MSET_STATEMENT_TIMEOUT_MS
- PERSISTPG_KV_PARTITIONS (enable hash partitioning on first schema creation; requires empty table to migrate)

Pool tuning:
- PERSISTPG_STATEMENT_CACHE_SIZE (default 1000)
- PERSISTPG_POOL_MAX_QUERIES (default 50000)
- PERSISTPG_POOL_MAX_INACTIVE_LIFETIME (default 300s)

## Error Handling

- Database errors raise asyncpg exceptions.
- Methods return booleans/integers/lists that indicate success, counts, or new values.

## FAQ

- Does it require migrations? No; schema is ensured automatically on first use.
- Can I use this in production? Yes, but review your workload, indexes, and timeouts. Partitioning can be enabled via env var before first schema creation.
- What about JSON indexing? For advanced value queries, consider adding GIN indexes (not created by default to keep writes lean).