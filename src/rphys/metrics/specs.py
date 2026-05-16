"""Metric descriptors, contracts, grouping specs, and observation view plans."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data.locators import FieldLocator
from rphys.errors import InvalidMetricSpecError

from ._validation import (
    coerce_key_tuple,
    coerce_empty_policy,
    coerce_level,
    coerce_level_tuple,
    coerce_locator,
    coerce_locator_tuple,
    coerce_mapping,
    coerce_missing_policy,
    coerce_mixed_level_policy,
    coerce_non_empty_string,
)

__all__ = ["GroupBySpec", "MetricContract", "MetricInputSpec", "MetricObservationViewPlan"]


@dataclass(frozen=True, init=False, slots=True)
class MetricInputSpec:
    """Declared field consumed by a metric."""

    locator: FieldLocator
    role: str
    required: bool
    expected_metadata: Mapping[str, object]

    def __init__(
        self,
        locator: FieldLocator | str,
        *,
        role: str,
        required: bool = True,
        expected_metadata: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "locator",
            coerce_locator(locator, owner="MetricInputSpec", error_type=InvalidMetricSpecError),
        )
        object.__setattr__(
            self,
            "role",
            coerce_non_empty_string(
                role,
                owner="MetricInputSpec",
                field="role",
                error_type=InvalidMetricSpecError,
            ),
        )
        if not isinstance(required, bool):
            raise InvalidMetricSpecError(
                "MetricInputSpec required must be a boolean.",
                owner="MetricInputSpec",
                field="required",
                expected="bool",
                actual=type(required).__name__,
            )
        object.__setattr__(self, "required", required)
        object.__setattr__(
            self,
            "expected_metadata",
            coerce_mapping(
                expected_metadata,
                owner="MetricInputSpec",
                field="expected_metadata",
                error_type=InvalidMetricSpecError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class GroupBySpec:
    """Caller-supplied grouping descriptor for metric observations."""

    keys: tuple[str, ...]
    level: str
    missing_policy: str
    metadata: Mapping[str, object]

    def __init__(
        self,
        keys: Iterable[str],
        *,
        level: str = "group",
        missing_policy: str = "error",
        metadata: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "keys",
            coerce_key_tuple(keys, owner="GroupBySpec", field="keys", error_type=InvalidMetricSpecError),
        )
        object.__setattr__(
            self,
            "level",
            coerce_level(level, owner="GroupBySpec", error_type=InvalidMetricSpecError),
        )
        object.__setattr__(
            self,
            "missing_policy",
            coerce_missing_policy(missing_policy, owner="GroupBySpec"),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(
                metadata,
                owner="GroupBySpec",
                field="metadata",
                error_type=InvalidMetricSpecError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class MetricObservationViewPlan:
    """Descriptor for grouping or projecting metric observations.

    A view plan is configuration only. ``PlannedMetricObservationView`` uses an
    injected projector to produce coarser or differently grouped observations;
    Stage 11 does not define concrete reduction algorithms, streaming state,
    distributed synchronization, or a separate view-result family.
    """

    name: str
    group_keys: tuple[str, ...]
    output_level: str
    source_levels: tuple[str, ...]
    missing_policy: str
    empty_policy: str
    mixed_level_policy: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        group_keys: Iterable[str] = (),
        output_level: str = "group",
        source_levels: Iterable[str] = (),
        missing_policy: str = "error",
        empty_policy: str = "error",
        mixed_level_policy: str = "error",
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="MetricObservationViewPlan",
                field="name",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "group_keys",
            coerce_key_tuple(
                group_keys,
                owner="MetricObservationViewPlan",
                field="group_keys",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "output_level",
            coerce_level(
                output_level,
                owner="MetricObservationViewPlan",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "source_levels",
            coerce_level_tuple(
                source_levels,
                owner="MetricObservationViewPlan",
                field="source_levels",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "missing_policy",
            coerce_missing_policy(missing_policy, owner="MetricObservationViewPlan"),
        )
        object.__setattr__(
            self,
            "empty_policy",
            coerce_empty_policy(empty_policy, owner="MetricObservationViewPlan"),
        )
        object.__setattr__(
            self,
            "mixed_level_policy",
            coerce_mixed_level_policy(mixed_level_policy, owner="MetricObservationViewPlan"),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(
                metadata,
                owner="MetricObservationViewPlan",
                field="metadata",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(
                provenance,
                owner="MetricObservationViewPlan",
                field="provenance",
                error_type=InvalidMetricSpecError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class MetricContract:
    """Backend-neutral metric contract."""

    name: str
    inputs: tuple[MetricInputSpec, ...]
    level: str
    writes: tuple[FieldLocator, ...]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        inputs: Iterable[MetricInputSpec] = (),
        *,
        level: str = "sample",
        writes: Iterable[FieldLocator | str] | FieldLocator | str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="MetricContract",
                field="name",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(self, "inputs", _coerce_inputs(inputs))
        object.__setattr__(
            self,
            "level",
            coerce_level(level, owner="MetricContract", error_type=InvalidMetricSpecError),
        )
        object.__setattr__(self, "writes", coerce_locator_tuple(writes, owner="MetricContract"))
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(
                metadata,
                owner="MetricContract",
                field="metadata",
                error_type=InvalidMetricSpecError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(
                provenance,
                owner="MetricContract",
                field="provenance",
                error_type=InvalidMetricSpecError,
            ),
        )


def _coerce_inputs(values: Iterable[MetricInputSpec]) -> tuple[MetricInputSpec, ...]:
    try:
        inputs = tuple(values)
    except TypeError as exc:
        raise InvalidMetricSpecError(
            "MetricContract inputs must be iterable.",
            owner="MetricContract",
            field="inputs",
            expected="iterable of MetricInputSpec",
            actual=type(values).__name__,
        ) from exc
    for index, input_spec in enumerate(inputs):
        if not isinstance(input_spec, MetricInputSpec):
            raise InvalidMetricSpecError(
                "MetricContract inputs must contain MetricInputSpec records.",
                owner="MetricContract",
                field="inputs",
                index=index,
                actual=type(input_spec).__name__,
            )
    locators = [input_spec.locator for input_spec in inputs]
    duplicates = sorted({str(locator) for locator in locators if locators.count(locator) > 1})
    if duplicates:
        raise InvalidMetricSpecError(
            "MetricContract inputs must not repeat locators.",
            owner="MetricContract",
            field="inputs",
            duplicates=tuple(duplicates),
        )
    return inputs


MetricInputSpec.__hash__ = None  # type: ignore[assignment]
GroupBySpec.__hash__ = None  # type: ignore[assignment]
MetricObservationViewPlan.__hash__ = None  # type: ignore[assignment]
MetricContract.__hash__ = None  # type: ignore[assignment]
