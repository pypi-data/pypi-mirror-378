from __future__ import annotations

import asyncpg

__all__ = ["prefix_key", "with_namespace"]


def prefix_key(namespace: str, key: str) -> str:
    """Prefix a key with a namespace if provided.

    This helper composes keys in the form "<namespace>:<key>". If namespace is
    an empty string or None, the original key is returned unchanged.

    Args:
        namespace: Namespace/prefix to apply (e.g., "tenant1").
        key: Raw key (e.g., "user:42").

    Returns:
        The namespaced key if namespace is truthy, otherwise the original key.
    """
    if not namespace:
        return key
    return f"{namespace}:{key}"


async def with_namespace(pool: asyncpg.Pool, namespace: str) -> asyncpg.Pool:
    """No-op kept for symmetry; client stores namespace and calls prefix_key.

    This function exists to keep the commands layer decoupled if needed later.
    """
    return pool