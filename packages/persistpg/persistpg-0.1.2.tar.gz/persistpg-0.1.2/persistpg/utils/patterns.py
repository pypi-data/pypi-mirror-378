from __future__ import annotations

from typing import Final

__all__ = ["glob_to_like", "LIKE_ESCAPE"]

LIKE_ESCAPE: Final[str] = "\\"


def glob_to_like(pattern: str) -> str:
    """Convert a glob-style pattern to a SQL LIKE pattern.

    Supported glob tokens:
    - * => %
    - ? => _

    Also escapes existing %, _, and the escape char itself.

    Args:
        pattern: Glob-style pattern (e.g., "user:*", "a?c").

    Returns:
        SQL LIKE-compatible pattern string.
    """
    if pattern == "*":
        return "%"

    esc = LIKE_ESCAPE
    s = pattern
    # Escape escape-character first
    s = s.replace(esc, esc + esc)
    # Escape LIKE wildcards
    s = s.replace("%", esc + "%").replace("_", esc + "_")
    # Replace glob wildcards with LIKE
    s = s.replace("*", "%").replace("?", "_")
    return s