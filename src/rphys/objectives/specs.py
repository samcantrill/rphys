"""Objective aggregation descriptors and contracts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data.locators import FieldLocator
from rphys.errors import InvalidObjectiveSpecError

from ._validation import (
    coerce_locator_tuple,
    coerce_non_empty_string,
    coerce_reduction,
    coerce_string_mapping,
    coerce_weight,
)

__all__ = ["ObjectiveContract", "ObjectiveTermSpec"]


@dataclass(frozen=True, init=False, slots=True)
class ObjectiveTermSpec:
    """Declared optimizer-relevant component of an objective."""

    name: str
    source: str
    weight: float
    reduction: str
    schedule: Mapping[str, object]
    metadata: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        source: str,
        weight: float = 1.0,
        reduction: str = "weighted_sum",
        schedule: Mapping[object, object] | None = None,
        metadata: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="ObjectiveTermSpec",
                field="name",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "source",
            coerce_non_empty_string(
                source,
                owner="ObjectiveTermSpec",
                field="source",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "weight",
            coerce_weight(
                weight,
                owner="ObjectiveTermSpec",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "reduction",
            coerce_reduction(
                reduction,
                owner="ObjectiveTermSpec",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "schedule",
            coerce_string_mapping(
                schedule,
                owner="ObjectiveTermSpec",
                field="schedule",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="ObjectiveTermSpec",
                field="metadata",
                error_type=InvalidObjectiveSpecError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class ObjectiveContract:
    """Optimizer-facing objective contract with declared patch writes."""

    name: str
    terms: tuple[ObjectiveTermSpec, ...]
    writes: tuple[FieldLocator, ...]
    reduction: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        terms: Iterable[ObjectiveTermSpec],
        *,
        writes: Iterable[FieldLocator | str] | FieldLocator | str | None = None,
        reduction: str = "weighted_sum",
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="ObjectiveContract",
                field="name",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(self, "terms", _coerce_term_specs(terms))
        object.__setattr__(self, "writes", coerce_locator_tuple(writes, owner="ObjectiveContract"))
        object.__setattr__(
            self,
            "reduction",
            coerce_reduction(
                reduction,
                owner="ObjectiveContract",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="ObjectiveContract",
                field="metadata",
                error_type=InvalidObjectiveSpecError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="ObjectiveContract",
                field="provenance",
                error_type=InvalidObjectiveSpecError,
            ),
        )


def _coerce_term_specs(values: Iterable[ObjectiveTermSpec]) -> tuple[ObjectiveTermSpec, ...]:
    try:
        specs = tuple(values)
    except TypeError as exc:
        raise InvalidObjectiveSpecError(
            "ObjectiveContract terms must be iterable.",
            owner="ObjectiveContract",
            field="terms",
            expected="iterable of ObjectiveTermSpec",
            actual=type(values).__name__,
        ) from exc
    if not specs:
        raise InvalidObjectiveSpecError(
            "ObjectiveContract terms must not be empty.",
            owner="ObjectiveContract",
            field="terms",
        )
    for index, spec in enumerate(specs):
        if not isinstance(spec, ObjectiveTermSpec):
            raise InvalidObjectiveSpecError(
                "ObjectiveContract terms must contain ObjectiveTermSpec records.",
                owner="ObjectiveContract",
                field="terms",
                index=index,
                actual=type(spec).__name__,
            )
    names = [spec.name for spec in specs]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise InvalidObjectiveSpecError(
            "ObjectiveContract terms must not repeat names.",
            owner="ObjectiveContract",
            field="terms",
            duplicates=tuple(duplicates),
        )
    return specs


ObjectiveTermSpec.__hash__ = None  # type: ignore[assignment]
ObjectiveContract.__hash__ = None  # type: ignore[assignment]
