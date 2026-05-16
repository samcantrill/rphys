"""Private validation helpers for learner contract records."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import TypeAlias

from rphys.errors import RemotePhysLearningError

PrimitiveValue: TypeAlias = str | int | float | bool | None
PrimitiveMapping: TypeAlias = Mapping[str, PrimitiveValue]

_PRIMITIVE_TYPES = (str, int, float, bool)


def freeze_primitive_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> PrimitiveMapping:
    """Return an immutable string-keyed primitive mapping."""

    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise RemotePhysLearningError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )

    frozen: dict[str, PrimitiveValue] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise RemotePhysLearningError(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                key=repr(key),
                actual=type(key).__name__,
            )
        if item is not None and not isinstance(item, _PRIMITIVE_TYPES):
            raise RemotePhysLearningError(
                f"{owner} {field} values must be primitive.",
                owner=owner,
                field=field,
                key=key,
                actual=type(item).__name__,
            )
        frozen[key] = item
    return MappingProxyType(frozen)


def coerce_non_negative_index(
    value: int | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    """Validate an optional zero-based loop index."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RemotePhysLearningError(
            f"{owner} {field} must be a non-negative integer when provided.",
            owner=owner,
            field=field,
            expected="non-negative integer | None",
            actual=type(value).__name__,
            value=value,
        )
    return value


def coerce_optional_label(
    value: str | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    """Validate an optional non-empty string label."""

    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise RemotePhysLearningError(
            f"{owner} {field} must be a non-empty string when provided.",
            owner=owner,
            field=field,
            expected="non-empty string | None",
            actual=type(value).__name__,
        )
    return value
