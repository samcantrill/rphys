"""Package-local validation helpers for loss contract records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidLossContextError,
    InvalidLossResultError,
    InvalidLossSpecError,
)

ALLOWED_REDUCTIONS = frozenset({"none", "mean", "sum", "weighted_mean", "custom"})
ALLOWED_MISSING_POLICIES = frozenset({"error", "allow"})


def coerce_non_empty_string(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidLossSpecError | InvalidLossContextError | InvalidLossResultError],
) -> str:
    if isinstance(value, str) and value:
        return value
    raise error_type(
        f"{owner} {field} must be a non-empty string.",
        owner=owner,
        field=field,
        expected="non-empty string",
        actual=repr(value),
    )


def coerce_optional_non_empty_string(
    value: object | None,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidLossSpecError | InvalidLossContextError | InvalidLossResultError],
) -> str | None:
    if value is None:
        return None
    return coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        error_type=error_type,
    )


def coerce_string_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidLossSpecError | InvalidLossContextError | InvalidLossResultError],
) -> Mapping[str, object]:
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


def coerce_locator(
    value: FieldLocator | str,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidLossSpecError | InvalidLossResultError],
) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    if isinstance(value, str):
        return FieldLocator.parse(value)
    raise error_type(
        f"{owner} {field} must be a FieldLocator or locator string.",
        owner=owner,
        field=field,
        expected="FieldLocator | str",
        actual=type(value).__name__,
    )


def coerce_locator_tuple(
    values: Iterable[FieldLocator | str] | FieldLocator | str | None,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidLossSpecError],
) -> tuple[FieldLocator, ...]:
    if values is None:
        return ()
    if isinstance(values, (FieldLocator, str)):
        values = (values,)
    try:
        locators = tuple(
            coerce_locator(value, owner=owner, field=field, error_type=error_type)
            for value in values
        )
    except TypeError as exc:
        raise error_type(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of FieldLocator | str",
            actual=type(values).__name__,
        ) from exc
    duplicates = _duplicates(locators)
    if duplicates:
        raise error_type(
            f"{owner} {field} must not contain duplicate locators.",
            owner=owner,
            field=field,
            duplicates=tuple(str(locator) for locator in duplicates),
        )
    return locators


def coerce_reduction(
    value: str,
    *,
    owner: str,
    field: str = "reduction",
    error_type: type[InvalidLossSpecError | InvalidLossResultError] = InvalidLossSpecError,
) -> str:
    resolved = coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        error_type=error_type,
    )
    if resolved not in ALLOWED_REDUCTIONS:
        raise error_type(
            f"{owner} {field} is not supported by the Stage 11 contract.",
            owner=owner,
            field=field,
            expected=sorted(ALLOWED_REDUCTIONS),
            actual=resolved,
        )
    return resolved


def coerce_missing_policy(value: str, *, owner: str, field: str) -> str:
    resolved = coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        error_type=InvalidLossSpecError,
    )
    if resolved not in ALLOWED_MISSING_POLICIES:
        raise InvalidLossSpecError(
            f"{owner} {field} is not supported by the Stage 11 contract.",
            owner=owner,
            field=field,
            expected=sorted(ALLOWED_MISSING_POLICIES),
            actual=resolved,
        )
    return resolved


def coerce_fields_patch(
    value: Mapping[FieldLocator | str, FieldValue] | None,
    *,
    declared_writes: tuple[FieldLocator, ...],
    owner: str,
) -> Mapping[FieldLocator, FieldValue]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise InvalidLossResultError(
            f"{owner} fields must be a mapping.",
            owner=owner,
            field="fields",
            expected="mapping of FieldLocator to FieldValue",
            actual=type(value).__name__,
        )
    resolved: dict[FieldLocator, FieldValue] = {}
    for locator, field_value in value.items():
        resolved_locator = coerce_locator(
            locator,
            owner=owner,
            field="fields",
            error_type=InvalidLossResultError,
        )
        if resolved_locator in resolved:
            raise InvalidLossResultError(
                f"{owner} fields must not contain duplicate locators.",
                owner=owner,
                field="fields",
                locator=str(resolved_locator),
            )
        if not isinstance(field_value, FieldValue):
            raise InvalidLossResultError(
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
        raise InvalidLossResultError(
            f"{owner} fields include undeclared patch locators.",
            owner=owner,
            field="fields",
            undeclared=tuple(str(locator) for locator in undeclared),
            declared=tuple(str(locator) for locator in declared_writes),
        )
    return MappingProxyType(resolved)


def metadata_has_expected(
    field_value: FieldValue,
    expected: Mapping[str, object],
) -> tuple[str, ...]:
    available = {str(key): value for key, value in field_value.metadata.items()}
    return tuple(key for key, expected_value in expected.items() if available.get(key) != expected_value)


def is_empty_mask_payload(payload: object) -> bool:
    try:
        return len(payload) == 0  # type: ignore[arg-type]
    except TypeError:
        return False


def _duplicates(values: tuple[FieldLocator, ...]) -> tuple[FieldLocator, ...]:
    seen: set[FieldLocator] = set()
    duplicate: list[FieldLocator] = []
    for value in values:
        if value in seen and value not in duplicate:
            duplicate.append(value)
        seen.add(value)
    return tuple(duplicate)
