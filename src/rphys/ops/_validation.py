"""Private helpers for Stage 6 operation schema and record validation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

from rphys.errors import RemotePhysError

__all__ = []


ErrorType = type[RemotePhysError]


def coerce_non_empty_string(
    value: object,
    *,
    owner: str,
    field: str,
    expected: str,
    error_type: ErrorType,
) -> str:
    """Return a non-empty string value or raise ``error_type``."""

    if not isinstance(value, str):
        raise error_type(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected=expected,
            actual=type(value).__name__,
        )
    stripped = value.strip()
    if not stripped:
        raise error_type(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected=expected,
            actual=value,
        )
    return value


def coerce_type_expectation(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: ErrorType,
) -> type | tuple[type, ...] | None:
    """Return ``None``, a ``type``, or an immutable tuple of ``type`` values."""

    if value is None:
        return None
    if isinstance(value, type):
        return value
    if isinstance(value, tuple):
        return tuple(_coerce_type_member(item, owner=owner, field=field, error_type=error_type) for item in value)
    raise error_type(
        f"{owner} {field} must be None, a type, or a tuple of types.",
        owner=owner,
        field=field,
        expected="None, type, or tuple[type, ...]",
        actual=type(value).__name__,
    )


def _coerce_type_member(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: ErrorType,
) -> type:
    if not isinstance(value, type):
        raise error_type(
            f"{owner} {field} entries must all be types.",
            owner=owner,
            field=field,
            expected="type",
            actual=type(value).__name__,
            value_repr=repr(value),
        )
    return value


def coerce_string_sequence(
    values: Sequence[object] | None,
    *,
    owner: str,
    field: str,
    expected: str,
    error_type: ErrorType,
    allow_none: bool = True,
) -> tuple[str, ...]:
    """Return a tuple of unique non-empty strings."""

    if values is None:
        if allow_none:
            return ()
        raise error_type(
            f"{owner} {field} must be a sequence of non-empty strings.",
            owner=owner,
            field=field,
            expected=expected,
            actual=None,
        )

    if isinstance(values, (str, bytes)):
        raise error_type(
            f"{owner} {field} must be a sequence of non-empty strings.",
            owner=owner,
            field=field,
            expected=expected,
            actual=type(values).__name__,
        )

    if not isinstance(values, Sequence):
        raise error_type(
            f"{owner} {field} must be a sequence of non-empty strings.",
            owner=owner,
            field=field,
            expected=expected,
            actual=type(values).__name__,
        )

    coerced: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(values):
        text = coerce_non_empty_string(
            item,
            owner=owner,
            field=f"{field}[{index}]",
            expected=expected,
            error_type=error_type,
        )
        if text in seen:
            raise error_type(
                f"{owner} {field} entries must be unique.",
                owner=owner,
                field=field,
                expected="unique values",
                actual=text,
            )
        seen.add(text)
        coerced.append(text)

    return tuple(coerced)


def coerce_string_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
    error_type: ErrorType,
) -> MappingProxyType:
    """Copy and expose a read-only mapping with non-empty-string keys."""

    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise error_type(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, object]",
            actual=type(value).__name__,
        )

    copied: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise error_type(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                expected="non-empty string keys",
                actual=type(key).__name__,
                key=repr(key),
            )
        copied[key] = item

    return MappingProxyType(dict(copied))
