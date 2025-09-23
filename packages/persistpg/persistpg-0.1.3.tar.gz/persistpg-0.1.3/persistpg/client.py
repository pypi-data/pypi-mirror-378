from __future__ import annotations

import asyncio
import atexit
from weakref import WeakSet
from typing import Any, List, Optional

import asyncpg
from enum import Enum

from .connection import create_pool, ensure_schema
from .commands.set import set_value
from .commands.get import get_value
from .commands.delete import delete_keys
from .commands.exists import exists_key
from .commands.setnx import setnx_key
# list_keys removed; use search_by_key instead
from .commands.expire import expire_key
from .commands.ttl import ttl_key
from .commands.incr import incr_key
from .commands.decr import decr_key
from .commands.flushall import flush_all
from .commands.search import search_by_key, search_by_value
from .commands.find import find_keys_by_field
from .commands.mget import mget_values
from .commands.mset import mset_values
from .commands.namespace import prefix_key
from .commands.lock import acquire_lock, renew_lock, release_lock
from .commands.unique import reserve_unique, release_unique, get_unique_key
from .commands.scan import scan_keys
from .commands.persist import persist_key
from .commands.rate_limit import rate_limit_take
from .commands.cleanup import sweep_expired

__all__ = ["PersistPGClient", "By"]


# Track live clients to close pools automatically at process exit.
_CLIENTS: "WeakSet[PersistPGClient]" = WeakSet()


class By(Enum):
    KEY = "key"
    VALUE = "value"


class PersistPGClient:
    """A very fast asynchronous wrapper for PostgreSQL key-value operations.

    This client uses asyncpg with connection pooling for minimal overhead and
    provides a simple API similar to the redis Python client.
    """

    def __init__(self, url: str, *, min_size: int = 1, max_size: int = 10,
                 sweeper_interval_seconds: float = 30.0,
                 sweeper_batch_size: int = 1000,
                 auto_start_sweeper: bool = True) -> None:
        """Initialize the client with a PostgreSQL connection URL.

        Args:
            url: PostgreSQL connection URL (local or external).
            min_size: Minimum number of connections for the pool.
            max_size: Maximum number of connections for the pool.
            sweeper_interval_seconds: Background sweeper interval in seconds (default 30.0).
            sweeper_batch_size: Background sweeper batch size per run (default 1000).
            auto_start_sweeper: If True, start expiry sweeper automatically after pool init.
        """
        self._url = url
        self._min_size = min_size
        self._max_size = max_size
        self._pool: Optional[asyncpg.Pool] = None
        self._init_lock = asyncio.Lock()
        self._initialized = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._sweeper_task: Optional[asyncio.Task] = None
        self._sweep_interval: float = float(sweeper_interval_seconds)
        self._sweep_batch: int = int(sweeper_batch_size)
        self._auto_start_sweeper: bool = bool(auto_start_sweeper)
        _CLIENTS.add(self)

    async def _ensure_pool(self) -> asyncpg.Pool:
        if self._initialized and self._pool is not None:
            return self._pool
        async with self._init_lock:
            if self._initialized and self._pool is not None:
                return self._pool
            # Capture the creating loop for safe shutdown
            self._loop = asyncio.get_running_loop()
            pool = await create_pool(self._url, min_size=self._min_size, max_size=self._max_size)
            await ensure_schema(pool)
            self._pool = pool
            self._initialized = True
            # Auto-start sweeper on first pool init if enabled (works for both usage modes)
            if self._auto_start_sweeper and (self._sweeper_task is None or self._sweeper_task.done()):
                await self.start_expiry_sweeper(interval_seconds=self._sweep_interval, batch_size=self._sweep_batch)
            return pool

    async def start_expiry_sweeper(self, *, interval_seconds: float = 30.0, batch_size: int = 1000) -> None:
        """Start a background task that periodically deletes expired keys.

        Safe to call multiple times; subsequent calls update the schedule.
        """
        self._sweep_interval = max(1.0, float(interval_seconds))
        self._sweep_batch = max(1, int(batch_size))
        pool = await self._ensure_pool()
        # If a task is already running, restart it to apply new settings immediately
        if self._sweeper_task and not self._sweeper_task.done():
            self._sweeper_task.cancel()
            try:
                await self._sweeper_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            self._sweeper_task = None
        loop = asyncio.get_running_loop()
        async def _run():
            try:
                while True:
                    try:
                        deleted = await sweep_expired(pool, batch_size=self._sweep_batch)
                        # If nothing deleted, we still sleep to avoid busy loop
                    except Exception:
                        # Suppress to keep background task resilient
                        pass
                    await asyncio.sleep(self._sweep_interval)
            except asyncio.CancelledError:
                return
        self._sweeper_task = loop.create_task(_run())

    async def stop_expiry_sweeper(self) -> None:
        """Stop the background sweeper if running."""
        task = self._sweeper_task
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                # Expected when awaiting a cancelled task
                pass
            except Exception:
                # Suppress unexpected errors to avoid impacting user code
                pass
        self._sweeper_task = None

    async def close(self) -> None:
        """Close the underlying connection pool."""
        if self._pool is not None:
            await self.stop_expiry_sweeper()
            await self._pool.close()
            self._pool = None
            self._initialized = False

    def _close_sync(self) -> None:
        """Synchronously close the pool for shutdown scenarios.

        Tries to close using the original loop if available and open; otherwise
        falls back to terminate() to avoid interacting with a closed loop.
        """
        pool = self._pool
        if pool is None:
            return
        # Mark as closed to avoid double-closing
        self._pool = None
        self._initialized = False
        try:
            loop = self._loop
            if loop is not None and not loop.is_closed():
                # Loop should not be running at interpreter exit; but if it is, skip
                if not loop.is_running():
                    loop.run_until_complete(pool.close())
                    return
            # Fallback: terminate without waiting (best-effort, sync)
            terminate = getattr(pool, "terminate", None)
            if callable(terminate):
                terminate()
        except Exception:
            # Best-effort at shutdown; suppress errors
            pass

    async def __aenter__(self) -> "PersistPGClient":
        await self._ensure_pool()
        # Sweeper auto-starts during pool init if enabled.
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop_expiry_sweeper()
        await self.close()

    # API Methods
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Store a key with a value.

        Args:
            key: Key to set.
            value: JSON-serializable value to store.
            expire: Optional TTL in seconds.

        Returns:
            True if stored.
        """
        pool = await self._ensure_pool()
        return await set_value(pool, key, value, expire)

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve the value of a key.

        Args:
            key: Key to fetch.

        Returns:
            The value if exists, else None.
        """
        pool = await self._ensure_pool()
        return await get_value(pool, key)

    async def delete(self, *keys: str) -> int:
        """Delete one or multiple keys.

        Args:
            *keys: One or more keys to delete.

        Returns:
            The number of deleted keys.
        """
        pool = await self._ensure_pool()
        return await delete_keys(pool, keys)

    async def exists(self, key: str) -> bool:
        """Check if a key exists.

        Args:
            key: Key to check.

        Returns:
            True if the key exists and is not expired, False otherwise.
        """
        pool = await self._ensure_pool()
        return await exists_key(pool, key)
    async def search(self, by: "By", query: str) -> List[str]:
        """Search for keys by key pattern or by value substring.

        Args:
            by: By.KEY for key-pattern search, By.VALUE for value substring search.
            query: The search pattern or substring. For By.KEY, supports glob tokens * and ?.

        Returns:
            List of matching keys.
        """
        pool = await self._ensure_pool()
        if by == By.KEY:
            return await search_by_key(pool, query)
        if by == By.VALUE:
            return await search_by_value(pool, query)
        raise ValueError("Unsupported search type")

    async def find(self, collection: str, field: str, value: Any) -> List[str]:
        """Find keys in a collection where JSON field equals the provided value.

        Example: await client.find("user", "email", "ahmed@example.com")

        Args:
            collection: Logical collection/prefix (e.g., "user" maps to keys like "user:*").
            field: JSON field name to match.
            value: Value to match (compared as text).

        Returns:
            List of matching keys.
        """
        pool = await self._ensure_pool()
        return await find_keys_by_field(pool, collection, field, value)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set TTL on a key.

        Args:
            key: Key to expire.
            seconds: TTL in seconds.

        Returns:
            True if TTL is set, False otherwise.
        """
        pool = await self._ensure_pool()
        return await expire_key(pool, key, seconds)

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key.

        Args:
            key: Key to check.

        Returns:
            Remaining seconds, -1 if no TTL, -2 if key doesn't exist.
        """
        pool = await self._ensure_pool()
        return await ttl_key(pool, key)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment an integer value.

        Args:
            key: Key to increment.
            amount: Amount to add (default 1).

        Returns:
            The new integer value.
        """
        pool = await self._ensure_pool()
        return await incr_key(pool, key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement an integer value.

        Args:
            key: Key to decrement.
            amount: Amount to subtract (default 1).

        Returns:
            The new integer value.
        """
        pool = await self._ensure_pool()
        return await decr_key(pool, key, amount)

    async def flushall(self) -> bool:
        """Remove all keys from storage (like Redis FLUSHALL)."""
        pool = await self._ensure_pool()
        return await flush_all(pool)

    async def mget(self, *keys: str) -> List[Optional[Any]]:
        """Get multiple keys in one roundtrip, preserving input order.

        Args:
            *keys: One or more keys to fetch.

        Returns:
            A list of values aligned with the given keys; missing or expired keys yield None.
        """
        pool = await self._ensure_pool()
        return await mget_values(pool, keys)

    async def mset(self, items: dict[str, Any], expire: Optional[int] = None) -> int:
        """Set multiple key/value pairs in one roundtrip.

        Args:
            items: Mapping of key -> value (values must be JSON-serializable).
            expire: Optional TTL in seconds to apply to all items. If None, existing TTLs are preserved for updates and new items are persistent.

        Returns:
            Count of keys written.
        """
        pool = await self._ensure_pool()
        return await mset_values(pool, items, expire)

    async def setnx(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set the value only if the key does not exist (or is expired).

        Args:
            key: Key to set if absent.
            value: JSON-serializable value to store.
            expire: Optional TTL in seconds for the key.

        Returns:
            True if the key was set, False otherwise.
        """
        pool = await self._ensure_pool()
        return await setnx_key(pool, key, value, expire)

    async def rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """Consume one token from a fixed-window rate limiter.

        Args:
            key: Identifier of the rate limit bucket.
            limit: Maximum number of allowed events per window.
            window_seconds: Window duration in seconds.

        Returns:
            A tuple (allowed, remaining, reset_seconds):
            - allowed: True if the event is allowed under the current window.
            - remaining: Remaining tokens in the window (never negative).
            - reset_seconds: Seconds until the window resets (>= 0).
        """
        pool = await self._ensure_pool()
        return await rate_limit_take(pool, key, limit, window_seconds)

    # Namespace helpers: simple prefixing for multi-tenant
    def ns(self, namespace: str) -> "PersistPGNamespaceClient":
        """Return a namespaced client that prefixes all keys with "namespace:".

        Use this to isolate tenants or subsystems: the returned client mirrors the
        same API but automatically prefixes every key.
        """
        return PersistPGNamespaceClient(self, namespace)

    # Locks API
    async def lock_acquire(self, key: str, ttl_seconds: int, owner: Optional[str] = None) -> Optional[str]:
        """Try to acquire a distributed lock.

        Args:
            key: Lock name.
            ttl_seconds: Lock TTL in seconds.
            owner: Optional owner token. If not provided, a UUID is generated.

        Returns:
            The owner token if acquired, or None if someone else holds the lock.
        """
        pool = await self._ensure_pool()
        return await acquire_lock(pool, key, ttl_seconds, owner)

    async def lock_renew(self, key: str, owner: str, ttl_seconds: int) -> bool:
        """Renew an existing lock if it is held by the given owner.

        Args:
            key: Lock name.
            owner: The owner token that currently holds the lock.
            ttl_seconds: New TTL to extend the lock.

        Returns:
            True if the lock was renewed, False otherwise.
        """
        pool = await self._ensure_pool()
        return await renew_lock(pool, key, owner, ttl_seconds)

    async def lock_release(self, key: str, owner: str) -> bool:
        """Release a lock held by the given owner.

        Args:
            key: Lock name.
            owner: Owner token that holds the lock.

        Returns:
            True if the lock was released, False otherwise.
        """
        pool = await self._ensure_pool()
        return await release_lock(pool, key, owner)

    async def scan(self, pattern: str = "*", after: Optional[str] = None, limit: int = 100) -> List[str]:
        """Lexicographically scan keys matching a glob-style pattern.

        Args:
            pattern: Glob-style pattern (e.g., "user:*").
            after: Exclusive start key; only return keys greater than this value.
            limit: Maximum number of keys to return.

        Returns:
            Up to `limit` keys ordered ascending.
        """
        pool = await self._ensure_pool()
        return await scan_keys(pool, pattern, after, limit)

    # Unique helpers
    async def unique_reserve(self, collection: str, field: str, value: str, key: str) -> bool:
        """Reserve a unique (collection, field, value) mapping for a key.

        Args:
            collection: Logical collection or index name.
            field: Logical field name.
            value: Field value to reserve.
            key: The key that claims the uniqueness.

        Returns:
            True if reserved by this key, False if the triplet is taken by someone else.
        """
        pool = await self._ensure_pool()
        return await reserve_unique(pool, collection, field, value, key)

    async def unique_release(self, collection: str, field: str, value: str, key: str) -> bool:
        """Release a previously reserved unique triplet for the given key.

        Args:
            collection: Collection name.
            field: Field name.
            value: Field value.
            key: The key that previously reserved the triplet.

        Returns:
            True if released, False otherwise.
        """
        pool = await self._ensure_pool()
        return await release_unique(pool, collection, field, value, key)

    async def unique_get(self, collection: str, field: str, value: str) -> Optional[str]:
        """Get the key that currently holds the (collection, field, value) reservation.

        Args:
            collection: Collection name.
            field: Field name.
            value: Field value.

        Returns:
            The key if present, otherwise None.
        """
        pool = await self._ensure_pool()
        return await get_unique_key(pool, collection, field, value)

    async def persist(self, key: str) -> bool:
        """Remove the TTL from a key (make it persistent)."""
        pool = await self._ensure_pool()
        return await persist_key(pool, key)


class PersistPGNamespaceClient:
    """Namespace view over a base PersistPGClient.

    All methods mirror PersistPGClient, but automatically prefix keys with
    "<namespace>:" to provide multi-tenancy or scoped separation.
    """
    def __init__(self, base: PersistPGClient, namespace: str) -> None:
        self._base = base
        self._ns = namespace

    def _k(self, key: str) -> str:
        # Avoid double-prefixing: if the key already starts with the namespace,
        # return it unchanged; otherwise apply the namespace.
        ns_prefix = f"{self._ns}:"
        return key if key.startswith(ns_prefix) else prefix_key(self._ns, key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Namespaced variant of set()."""
        return await self._base.set(self._k(key), value, expire)

    async def get(self, key: str) -> Optional[Any]:
        """Namespaced variant of get()."""
        return await self._base.get(self._k(key))

    async def delete(self, *keys: str) -> int:
        """Namespaced variant of delete()."""
        return await self._base.delete(*(self._k(k) for k in keys))

    async def exists(self, key: str) -> bool:
        """Namespaced variant of exists()."""
        return await self._base.exists(self._k(key))

    async def search(self, by: "By", query: str) -> List[str]:
        """Namespaced variant of search(). For By.KEY, the namespace is applied to the pattern."""
        if by == By.KEY:
            return [k for k in await self._base.search(By.KEY, prefix_key(self._ns, query))]
        return await self._base.search(by, query)

    async def find(self, collection: str, field: str, value: Any) -> List[str]:
        """Namespaced variant of find(); namespace is applied to the collection/prefix."""
        # collection is a prefix; apply namespace
        return await self._base.find(prefix_key(self._ns, collection), field, value)

    async def expire(self, key: str, seconds: int) -> bool:
        """Namespaced variant of expire()."""
        return await self._base.expire(self._k(key), seconds)

    async def ttl(self, key: str) -> int:
        """Namespaced variant of ttl()."""
        return await self._base.ttl(self._k(key))

    async def incr(self, key: str, amount: int = 1) -> int:
        """Namespaced variant of incr()."""
        return await self._base.incr(self._k(key), amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """Namespaced variant of decr()."""
        return await self._base.decr(self._k(key), amount)

    async def flushall(self) -> bool:
        """Delegates to base flushall() (global). Use with caution."""
        # Namespaced flushall is dangerous; keeping consistent with base means global flush
        return await self._base.flushall()

    async def mget(self, *keys: str) -> List[Optional[Any]]:
        """Namespaced variant of mget(); preserves input order.

        Accepts either raw keys (e.g., "user:1") or fully-qualified keys
        (e.g., "<namespace>:user:1") and avoids double-prefixing.
        """
        return await self._base.mget(*(self._k(k) for k in keys))

    async def mset(self, items: dict[str, Any], expire: Optional[int] = None) -> int:
        """Namespaced variant of mset(); applies namespace to each key."""
        namespaced = {self._k(k): v for k, v in items.items()}
        return await self._base.mset(namespaced, expire)

    async def scan(self, pattern: str = "*", after: Optional[str] = None, limit: int = 100) -> List[str]:
        """Namespaced variant of scan(); applies namespace to the pattern."""
        return await self._base.scan(prefix_key(self._ns, pattern), after, limit)

    async def setnx(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Namespaced variant of setnx()."""
        return await self._base.setnx(self._k(key), value, expire)

    async def rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """Namespaced variant of rate_limit(); uses a namespaced bucket key."""
        return await self._base.rate_limit(self._k(key), limit, window_seconds)


# Register an atexit hook to close all remaining client pools automatically

def _atexit_cleanup() -> None:
    for client in list(_CLIENTS):
        try:
            client._close_sync()
        except Exception:
            pass


atexit.register(_atexit_cleanup)