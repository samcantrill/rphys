"""Private helpers for lightweight method contract records."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import TypeAlias

from rphys.errors import RemotePhysMethodError

PrimitiveValue: TypeAlias = str | int | float | bool | None
PrimitiveMapping: TypeAlias = Mapping[str, PrimitiveValue]

_PRIMITIVE_TYPES = (str, int, float, bool)


def freeze_primitive_mapping(
    value: Mapping[str, object] | None,
    *,
    field: str,
) -> PrimitiveMapping:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise RemotePhysMethodError(
            "Method record field must be a mapping.",
            field=field,
            actual=type(value).__name__,
        )

    frozen: dict[str, PrimitiveValue] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise RemotePhysMethodError(
                "Method record mapping keys must be strings.",
                field=field,
                key=repr(key),
                actual=type(key).__name__,
            )
        if item is not None and not isinstance(item, _PRIMITIVE_TYPES):
            raise RemotePhysMethodError(
                "Method record mapping values must be primitive.",
                field=field,
                key=key,
                actual=type(item).__name__,
            )
        frozen[key] = item
    return MappingProxyType(frozen)
