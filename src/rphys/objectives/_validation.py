"""Package-local validation helpers for objective records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidObjectiveContextError,
    InvalidObjectiveResultError,
    InvalidObjectiveSpecError,
)

ALLOWED_REDUCTIONS = frozenset({"none", "mean", "sum", "weighted_sum", "custom"})


def coerce_non_empty_string(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[
        InvalidObjectiveSpecError | InvalidObjectiveContextError | InvalidObjectiveResultError
    ],
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
    error_type: type[
        InvalidObjectiveSpecError | InvalidObjectiveContextError | InvalidObjectiveResultError
    ],
) -> str | None:
    if value is None:
        return None
    return coerce_non_empty_string(value, owner=owner, field=field, error_type=error_type)


def coerce_string_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
    error_type: type[
        InvalidObjectiveSpecError | InvalidObjectiveContextError | InvalidObjectiveResultError
    ],
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


def coerce_weight(value: object, *, owner: str, error_type: type[InvalidObjectiveSpecError | InvalidObjectiveResultError]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise error_type(
            f"{owner} weight must be numeric.",
            owner=owner,
            field="weight",
            expected="int | float",
            actual=type(value).__name__,
        )
    resolved = float(value)
    if resolved < 0:
        raise error_type(
            f"{owner} weight must not be negative.",
            owner=owner,
            field="weight",
            expected="non-negative number",
            actual=resolved,
        )
    return resolved


def coerce_reduction(
    value: str,
    *,
    owner: str,
    error_type: type[InvalidObjectiveSpecError | InvalidObjectiveResultError],
) -> str:
    resolved = coerce_non_empty_string(
        value,
        owner=owner,
        field="reduction",
        error_type=error_type,
    )
    if resolved not in ALLOWED_REDUCTIONS:
        raise error_type(
            f"{owner} reduction is not supported by the Stage 11 contract.",
            owner=owner,
            field="reduction",
            expected=sorted(ALLOWED_REDUCTIONS),
            actual=resolved,
        )
    return resolved


def coerce_locator(value: FieldLocator | str, *, owner: str, error_type: type[InvalidObjectiveSpecError | InvalidObjectiveResultError]) -> FieldLocator:
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


def coerce_locator_tuple(
    values: Iterable[FieldLocator | str] | FieldLocator | str | None,
    *,
    owner: str,
) -> tuple[FieldLocator, ...]:
    if values is None:
        return ()
    if isinstance(values, (FieldLocator, str)):
        values = (values,)
    try:
        locators = tuple(
            coerce_locator(value, owner=owner, error_type=InvalidObjectiveSpecError)
            for value in values
        )
    except TypeError as exc:
        raise InvalidObjectiveSpecError(
            f"{owner} writes must be iterable.",
            owner=owner,
            field="writes",
            expected="iterable of FieldLocator | str",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({str(locator) for locator in locators if locators.count(locator) > 1})
    if duplicates:
        raise InvalidObjectiveSpecError(
            f"{owner} writes must not contain duplicate locators.",
            owner=owner,
            field="writes",
            duplicates=tuple(duplicates),
        )
    return locators


def coerce_fields_patch(
    value: Mapping[FieldLocator | str, FieldValue] | None,
    *,
    declared_writes: tuple[FieldLocator, ...],
    owner: str,
) -> Mapping[FieldLocator, FieldValue]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise InvalidObjectiveResultError(
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
            error_type=InvalidObjectiveResultError,
        )
        if resolved_locator in resolved:
            raise InvalidObjectiveResultError(
                f"{owner} fields must not contain duplicate locators.",
                owner=owner,
                field="fields",
                locator=str(resolved_locator),
            )
        if not isinstance(field_value, FieldValue):
            raise InvalidObjectiveResultError(
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
        raise InvalidObjectiveResultError(
            f"{owner} fields include undeclared patch locators.",
            owner=owner,
            field="fields",
            undeclared=tuple(str(locator) for locator in undeclared),
            declared=tuple(str(locator) for locator in declared_writes),
        )
    return MappingProxyType(resolved)
