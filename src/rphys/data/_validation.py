"""Private lexical checks shared by Stage 1 data vocabulary modules."""

from __future__ import annotations

import re
from collections.abc import Iterable

ASCII_TOKEN_PATTERN = r"[a-z][a-z0-9_]*"
ASCII_TOKEN_RE = re.compile(rf"{ASCII_TOKEN_PATTERN}\Z")


def is_ascii_token(value: str) -> bool:
    """Return whether ``value`` is one lowercase ASCII vocabulary token."""

    return bool(ASCII_TOKEN_RE.fullmatch(value))


def dotted_tokens(value: str) -> tuple[str, ...] | None:
    """Return validated dotted tokens, or ``None`` when lexical checks fail."""

    if not value:
        return None
    tokens = tuple(value.split("."))
    if all(is_ascii_token(token) for token in tokens):
        return tokens
    return None


def single_token(value: str) -> bool:
    """Return whether ``value`` is exactly one lowercase ASCII token."""

    return is_ascii_token(value)


def contains_forbidden_separator(value: str, separators: Iterable[str]) -> bool:
    """Return whether ``value`` contains a separator outside the local grammar."""

    return any(separator in value for separator in separators)
