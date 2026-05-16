"""Package-local validation helpers for metric records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import InvalidMetricResultError, InvalidMetricSpecError

LEVELS = frozenset({"sample", "window", "record", "subject", "group", "dataset", "batch", "custom"})
MISSING_POLICIES = frozenset({"error", "allow"})
EMPTY_POLICIES = frozenset({"error", "allow"})
MIXED_LEVEL_POLICIES = frozenset({"error", "allow"})


def coerce_non_empty_string(value: object, *, owner: str, field: str, error_type):
    if isinstance(value, str) and value:
        return value
    raise error_type(
        f"{owner} {field} must be a non-empty string.",
        owner=owner,
        field=field,
        expected="non-empty string",
        actual=repr(value),
    )


def coerce_optional_string(value: object | None, *, owner: str, field: str, error_type):
    if value is None:
        return None
    return coerce_non_empty_string(value, owner=owner, field=field, error_type=error_type)


def coerce_mapping(value: Mapping[object, object] | None, *, owner: str, field: str, error_type):
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise error_type(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping with string keys",
            actual=type(value).__name__,
        )
    resolved: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise error_type(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                key=repr(key),
                expected="non-empty string",
                actual=type(key).__name__,
            )
        resolved[key] = item
    return MappingProxyType(resolved)


def coerce_level(value: str, *, owner: str, error_type):
    resolved = coerce_non_empty_string(value, owner=owner, field="level", error_type=error_type)
    if resolved not in LEVELS:
        raise error_type(
            f"{owner} level is not supported by the Stage 11 contract.",
            owner=owner,
            field="level",
            expected=sorted(LEVELS),
            actual=resolved,
        )
    return resolved


def coerce_key_tuple(values: Iterable[str], *, owner: str, field: str, error_type):
    try:
        keys = tuple(
            coerce_non_empty_string(value, owner=owner, field=field, error_type=error_type)
            for value in values
        )
    except TypeError as exc:
        raise error_type(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of strings",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise error_type(
            f"{owner} {field} must not contain duplicates.",
            owner=owner,
            field=field,
            duplicates=tuple(duplicates),
        )
    return keys


def coerce_missing_policy(value: str, *, owner: str):
    return coerce_policy(
        value,
        allowed=MISSING_POLICIES,
        owner=owner,
        field="missing_policy",
    )


def coerce_empty_policy(value: str, *, owner: str):
    return coerce_policy(
        value,
        allowed=EMPTY_POLICIES,
        owner=owner,
        field="empty_policy",
    )


def coerce_mixed_level_policy(value: str, *, owner: str):
    return coerce_policy(
        value,
        allowed=MIXED_LEVEL_POLICIES,
        owner=owner,
        field="mixed_level_policy",
    )


def coerce_policy(value: str, *, allowed: frozenset[str], owner: str, field: str):
    resolved = coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        error_type=InvalidMetricSpecError,
    )
    if resolved not in allowed:
        raise InvalidMetricSpecError(
            f"{owner} {field} is not supported by the Stage 11 contract.",
            owner=owner,
            field=field,
            expected=sorted(allowed),
            actual=resolved,
        )
    return resolved


def coerce_level_tuple(values: Iterable[str], *, owner: str, field: str, error_type):
    try:
        levels = tuple(
            coerce_level(value, owner=owner, error_type=error_type)
            for value in values
        )
    except TypeError as exc:
        raise error_type(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of metric levels",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({level for level in levels if levels.count(level) > 1})
    if duplicates:
        raise error_type(
            f"{owner} {field} must not contain duplicates.",
            owner=owner,
            field=field,
            duplicates=tuple(duplicates),
        )
    return levels


def coerce_locator(value: FieldLocator | str, *, owner: str, error_type):
    if isinstance(value, FieldLocator):
        return value
    if isinstance(value, str):
        return FieldLocator.parse(value)
    raise error_type(
        f"{owner} locator must be a FieldLocator or locator string.",
        owner=owner,
        field="locator",
        expected="FieldLocator | str",
        actual=type(value).__name__,
    )


def coerce_locator_tuple(values: Iterable[FieldLocator | str] | FieldLocator | str | None, *, owner: str):
    if values is None:
        return ()
    if isinstance(values, (FieldLocator, str)):
        values = (values,)
    try:
        locators = tuple(
            coerce_locator(value, owner=owner, error_type=InvalidMetricSpecError)
            for value in values
        )
    except TypeError as exc:
        raise InvalidMetricSpecError(
            f"{owner} writes must be iterable.",
            owner=owner,
            field="writes",
            expected="iterable of FieldLocator | str",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({str(locator) for locator in locators if locators.count(locator) > 1})
    if duplicates:
        raise InvalidMetricSpecError(
            f"{owner} writes must not contain duplicates.",
            owner=owner,
            field="writes",
            duplicates=tuple(duplicates),
        )
    return locators


def coerce_fields_patch(value: Mapping[FieldLocator | str, FieldValue] | None, *, declared_writes, owner: str):
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise InvalidMetricResultError(
            f"{owner} fields must be a mapping.",
            owner=owner,
            field="fields",
            expected="mapping of FieldLocator to FieldValue",
            actual=type(value).__name__,
        )
    resolved: dict[FieldLocator, FieldValue] = {}
    for locator, field_value in value.items():
        resolved_locator = coerce_locator(locator, owner=owner, error_type=InvalidMetricResultError)
        if not isinstance(field_value, FieldValue):
            raise InvalidMetricResultError(
                f"{owner} fields values must be FieldValue records.",
                owner=owner,
                field="fields",
                locator=str(resolved_locator),
                expected="FieldValue",
                actual=type(field_value).__name__,
            )
        resolved[resolved_locator] = field_value
    undeclared = tuple(locator for locator in resolved if locator not in declared_writes)
    if undeclared:
        raise InvalidMetricResultError(
            f"{owner} fields include undeclared patch locators.",
            owner=owner,
            field="fields",
            undeclared=tuple(str(locator) for locator in undeclared),
            declared=tuple(str(locator) for locator in declared_writes),
        )
    return MappingProxyType(resolved)
