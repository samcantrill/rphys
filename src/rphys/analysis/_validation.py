"""Private validation helpers for dependency-light analysis records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from rphys.errors import RemotePhysAnalysisError

__all__ = []


def coerce_non_empty_string(value: object, *, owner: str, field: str) -> str:
    if isinstance(value, str) and value:
        return value
    raise RemotePhysAnalysisError(
        f"{owner} {field} must be a non-empty string.",
        owner=owner,
        field=field,
        expected="non-empty string",
        actual=repr(value),
    )


def coerce_optional_string(value: object | None, *, owner: str, field: str) -> str | None:
    if value is None:
        return None
    return coerce_non_empty_string(value, owner=owner, field=field)


def coerce_string_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> Mapping[str, object]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise RemotePhysAnalysisError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping with string keys",
            actual=type(value).__name__,
        )
    resolved: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise RemotePhysAnalysisError(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                expected="non-empty string keys",
                actual=repr(key),
            )
        resolved[key] = item
    return MappingProxyType(resolved)


def coerce_string_tuple(values: Iterable[object], *, owner: str, field: str) -> tuple[str, ...]:
    try:
        resolved = tuple(coerce_non_empty_string(value, owner=owner, field=field) for value in values)
    except TypeError as exc:
        raise RemotePhysAnalysisError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of non-empty strings",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({value for value in resolved if resolved.count(value) > 1})
    if duplicates:
        raise RemotePhysAnalysisError(
            f"{owner} {field} must not contain duplicates.",
            owner=owner,
            field=field,
            duplicates=tuple(duplicates),
        )
    return resolved
