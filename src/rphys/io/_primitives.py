"""Private primitive validation helpers for lazy IO descriptors."""

from __future__ import annotations

import math
from collections.abc import Mapping
from types import MappingProxyType
from typing import TypeAlias

from rphys.errors import RemotePhysError

Primitive: TypeAlias = str | int | float | bool | None | list["Primitive"] | dict[str, "Primitive"]
FrozenPrimitive: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | tuple["FrozenPrimitive", ...]
    | Mapping[str, "FrozenPrimitive"]
)


def freeze_primitive(
    value: object,
    *,
    error_type: type[RemotePhysError],
    field: str,
) -> FrozenPrimitive:
    """Return a detached immutable primitive value or raise ``error_type``."""

    if value is None or isinstance(value, str) or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise error_type(
                "Primitive descriptor values must be finite.",
                field=field,
                actual=value,
            )
        return value
    if isinstance(value, list):
        return tuple(
            freeze_primitive(item, error_type=error_type, field=field)
            for item in value
        )
    if isinstance(value, Mapping):
        copied: dict[str, FrozenPrimitive] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise error_type(
                    "Primitive descriptor mapping keys must be non-empty strings.",
                    field=field,
                    key=key,
                    actual=type(key).__name__,
                )
            copied[key] = freeze_primitive(item, error_type=error_type, field=field)
        return MappingProxyType(copied)

    raise error_type(
        "Descriptor values must be JSON-like primitives.",
        field=field,
        actual=type(value).__name__,
    )


def thaw_primitive(value: FrozenPrimitive) -> Primitive:
    """Convert an internal immutable primitive into plain serialized values."""

    if isinstance(value, tuple):
        return [thaw_primitive(item) for item in value]
    if isinstance(value, Mapping):
        return {key: thaw_primitive(item) for key, item in value.items()}
    return value


def copy_string_mapping(
    value: Mapping[str, object] | None,
    *,
    error_type: type[RemotePhysError],
    field: str,
) -> dict[str, FrozenPrimitive]:
    """Copy a string-keyed primitive mapping for descriptor storage."""

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise error_type(
            "Descriptor metadata must be a mapping.",
            field=field,
            actual=type(value).__name__,
        )

    copied: dict[str, FrozenPrimitive] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise error_type(
                "Descriptor mapping keys must be non-empty strings.",
                field=field,
                key=key,
                actual=type(key).__name__,
            )
        copied[key] = freeze_primitive(item, error_type=error_type, field=field)
    return copied


def require_mapping(
    value: object,
    *,
    error_type: type[RemotePhysError],
    field: str,
) -> Mapping[str, object]:
    """Require a primitive descriptor dictionary shape."""

    if not isinstance(value, Mapping):
        raise error_type(
            "Serialized descriptors must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def require_exact_keys(
    value: Mapping[str, object],
    keys: set[str],
    *,
    error_type: type[RemotePhysError],
    descriptor: str,
) -> None:
    """Fail if a serialized descriptor has missing or unexpected keys."""

    actual = set(value)
    if actual != keys:
        raise error_type(
            "Serialized descriptor keys do not match the Stage 3 schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )
