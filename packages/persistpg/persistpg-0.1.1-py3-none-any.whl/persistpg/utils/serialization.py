from __future__ import annotations

from typing import Any

try:
    import orjson  # type: ignore
except Exception:  # pragma: no cover
    orjson = None  # type: ignore

__all__ = ["dumps", "loads"]


def dumps(value: Any) -> str:
    """Serialize a Python object to a compact JSON string.

    Uses orjson if available for speed; falls back to stdlib json.
    """
    if orjson is not None:
        return orjson.dumps(value, option=orjson.OPT_OMIT_MICROSECONDS | orjson.OPT_NON_STR_KEYS).decode()
    # Fallback
    import json
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def loads(data: str) -> Any:
    """Deserialize a JSON string into a Python object.

    Uses orjson if available for speed; falls back to stdlib json.
    """
    if orjson is not None:
        return orjson.loads(data)
    # Fallback
    import json
    return json.loads(data)