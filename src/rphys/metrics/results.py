"""Metric value, observation, collection, and result records."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from rphys.collections import CollectionItem
from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import InvalidMetricResultError, InvalidMetricSpecError

from ._validation import (
    coerce_fields_patch,
    coerce_level,
    coerce_mapping,
    coerce_non_empty_string,
    coerce_optional_string,
)
from .specs import GroupBySpec, MetricContract

__all__ = [
    "MetricObservation",
    "MetricObservationCollection",
    "MetricResult",
    "MetricValue",
]


@dataclass(frozen=True, init=False, slots=True)
class MetricValue:
    """Detached metric value plus backend-neutral metadata."""

    value: object
    backend: str | None
    detached: bool
    differentiable: bool
    unit: str | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        value: object,
        *,
        backend: str | None = None,
        detached: bool = True,
        differentiable: bool = False,
        unit: str | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if value is None:
            raise InvalidMetricResultError(
                "MetricValue value must preserve a detached backend-native value.",
                owner="MetricValue",
                field="value",
                expected="backend-native value",
                actual="None",
            )
        if not isinstance(detached, bool) or not isinstance(differentiable, bool):
            raise InvalidMetricResultError(
                "MetricValue detached and differentiable flags must be booleans.",
                owner="MetricValue",
                field="detachment",
                expected="bool flags",
                actual=f"{type(detached).__name__}/{type(differentiable).__name__}",
            )
        if not detached or differentiable:
            raise InvalidMetricResultError(
                "MetricValue must be detached and non-differentiable in Stage 11.",
                owner="MetricValue",
                field="detachment",
                detached=detached,
                differentiable=differentiable,
            )
        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "backend",
            coerce_optional_string(
                backend,
                owner="MetricValue",
                field="backend",
                error_type=InvalidMetricResultError,
            ),
        )
        object.__setattr__(self, "detached", detached)
        object.__setattr__(self, "differentiable", differentiable)
        object.__setattr__(
            self,
            "unit",
            coerce_optional_string(
                unit,
                owner="MetricValue",
                field="unit",
                error_type=InvalidMetricResultError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(metadata, owner="MetricValue", field="metadata", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_mapping(diagnostics, owner="MetricValue", field="diagnostics", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(provenance, owner="MetricValue", field="provenance", error_type=InvalidMetricResultError),
        )


@dataclass(frozen=True, init=False, slots=True)
class MetricObservation:
    """Row-like metric observation with level and grouping metadata."""

    name: str
    value: MetricValue
    level: str
    groups: Mapping[str, object]
    window: Mapping[str, object]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        value: MetricValue,
        *,
        level: str = "sample",
        groups: Mapping[object, object] | None = None,
        window: Mapping[object, object] | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(value, MetricValue):
            raise InvalidMetricResultError(
                "MetricObservation value must be a MetricValue.",
                owner="MetricObservation",
                field="value",
                expected="MetricValue",
                actual=type(value).__name__,
            )
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="MetricObservation",
                field="name",
                error_type=InvalidMetricResultError,
            ),
        )
        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "level",
            coerce_level(level, owner="MetricObservation", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "groups",
            coerce_mapping(groups, owner="MetricObservation", field="groups", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "window",
            coerce_mapping(window, owner="MetricObservation", field="window", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(metadata, owner="MetricObservation", field="metadata", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(provenance, owner="MetricObservation", field="provenance", error_type=InvalidMetricResultError),
        )


@dataclass(frozen=True, init=False, slots=True)
class MetricObservationCollection:
    """Immutable collection of row-like metric observations."""

    _entries: tuple[CollectionItem[MetricObservation], ...]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        observations: Iterable[MetricObservation | CollectionItem[MetricObservation]],
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "_entries", _coerce_entries(observations))
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(metadata, owner="MetricObservationCollection", field="metadata", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(provenance, owner="MetricObservationCollection", field="provenance", error_type=InvalidMetricResultError),
        )

    @property
    def entries(self) -> Sequence[CollectionItem[MetricObservation]]:
        return self._entries

    def __iter__(self) -> Iterator[MetricObservation]:
        for entry in self._entries:
            yield entry.value

    def __len__(self) -> int:
        return len(self._entries)

    def __getitem__(self, index: int) -> MetricObservation:
        return self._entries[index].value

    def combine(self, other: "MetricObservationCollection") -> "MetricObservationCollection":
        if not isinstance(other, MetricObservationCollection):
            raise InvalidMetricResultError(
                "MetricObservationCollection can only combine with another collection.",
                owner="MetricObservationCollection",
                field="other",
                expected="MetricObservationCollection",
                actual=type(other).__name__,
            )
        return MetricObservationCollection(
            (*self.entries, *other.entries),
            metadata={**self.metadata, **other.metadata},
            provenance={"sources": (self.provenance, other.provenance)},
        )

    def grouped(self, spec: GroupBySpec) -> Mapping[tuple[object, ...], "MetricObservationCollection"]:
        if not isinstance(spec, GroupBySpec):
            raise InvalidMetricSpecError(
                "MetricObservationCollection.grouped requires a GroupBySpec.",
                owner="MetricObservationCollection",
                field="spec",
                expected="GroupBySpec",
                actual=type(spec).__name__,
            )
        groups: dict[tuple[object, ...], list[CollectionItem[MetricObservation]]] = {}
        for entry in self.entries:
            missing = tuple(key for key in spec.keys if key not in entry.value.groups)
            if missing and spec.missing_policy == "error":
                raise InvalidMetricResultError(
                    "MetricObservation is missing required grouping metadata.",
                    owner="MetricObservationCollection",
                    field="groups",
                    missing=missing,
                )
            key = tuple(entry.value.groups.get(group_key) for group_key in spec.keys)
            groups.setdefault(key, []).append(entry)
        return MappingProxyType(
            {
                key: MetricObservationCollection(
                    grouped_entries,
                    metadata={**self.metadata, "group_by": spec.keys, "level": spec.level},
                    provenance=self.provenance,
                )
                for key, grouped_entries in groups.items()
            }
        )


@dataclass(frozen=True, init=False, slots=True)
class MetricResult:
    """Metric call result with observations and optional immutable field patches."""

    observations: MetricObservationCollection
    fields: Mapping[FieldLocator, FieldValue]
    contract: MetricContract | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        observations: MetricObservationCollection,
        *,
        fields: Mapping[FieldLocator | str, FieldValue] | None = None,
        contract: MetricContract | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(observations, MetricObservationCollection):
            raise InvalidMetricResultError(
                "MetricResult observations must be a MetricObservationCollection.",
                owner="MetricResult",
                field="observations",
                expected="MetricObservationCollection",
                actual=type(observations).__name__,
            )
        if contract is not None and not isinstance(contract, MetricContract):
            raise InvalidMetricResultError(
                "MetricResult contract must be a MetricContract when provided.",
                owner="MetricResult",
                field="contract",
                expected="MetricContract | None",
                actual=type(contract).__name__,
            )
        if fields and contract is None:
            raise InvalidMetricResultError(
                "MetricResult fields patches require a contract with declared writes.",
                owner="MetricResult",
                field="fields",
            )
        object.__setattr__(self, "observations", observations)
        object.__setattr__(
            self,
            "fields",
            coerce_fields_patch(
                fields,
                declared_writes=() if contract is None else contract.writes,
                owner="MetricResult",
            ),
        )
        object.__setattr__(self, "contract", contract)
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(metadata, owner="MetricResult", field="metadata", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_mapping(diagnostics, owner="MetricResult", field="diagnostics", error_type=InvalidMetricResultError),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(provenance, owner="MetricResult", field="provenance", error_type=InvalidMetricResultError),
        )


def _coerce_entries(values):
    try:
        entries = tuple(_coerce_entry(value) for value in values)
    except TypeError as exc:
        raise InvalidMetricResultError(
            "MetricObservationCollection observations must be iterable.",
            owner="MetricObservationCollection",
            field="observations",
            expected="iterable of MetricObservation | CollectionItem[MetricObservation]",
            actual=type(values).__name__,
        ) from exc
    names = [(entry.value.name, tuple(entry.value.groups.items()), entry.value.level) for entry in entries]
    duplicates = [name for name in names if names.count(name) > 1]
    if duplicates:
        raise InvalidMetricResultError(
            "MetricObservationCollection observations must not duplicate name/group/level.",
            owner="MetricObservationCollection",
            field="observations",
        )
    return entries


def _coerce_entry(value):
    if isinstance(value, CollectionItem):
        if not isinstance(value.value, MetricObservation):
            raise InvalidMetricResultError(
                "Metric observation collection entries must wrap MetricObservation values.",
                owner="MetricObservationCollection",
                field="observations",
                expected="MetricObservation",
                actual=type(value.value).__name__,
            )
        return value
    if isinstance(value, MetricObservation):
        return CollectionItem(value, metadata={"level": value.level, **value.groups})
    raise InvalidMetricResultError(
        "Metric observation collection entries must be observations or CollectionItem records.",
        owner="MetricObservationCollection",
        field="observations",
        expected="MetricObservation | CollectionItem[MetricObservation]",
        actual=type(value).__name__,
    )


MetricValue.__hash__ = None  # type: ignore[assignment]
MetricObservation.__hash__ = None  # type: ignore[assignment]
MetricObservationCollection.__hash__ = None  # type: ignore[assignment]
MetricResult.__hash__ = None  # type: ignore[assignment]
