"""Detached metric value records.

Stage 13 metrics bind outputs to ordinary ``metrics/*`` fields on runtime
containers. There is intentionally no public metric observation collection,
view, or result family; grouping and aggregation reuse sample collections,
collection views, and operation metadata.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from rphys.errors import InvalidMetricResultError

from ._validation import (
    coerce_mapping,
    coerce_optional_string,
)

__all__ = ["MetricValue"]


@dataclass(frozen=True, init=False, slots=True)
class MetricValue:
    """Detached metric value plus backend-neutral metadata.

    ``MetricValue`` is a payload wrapper, not a metric result row. Metric
    callables and operation adapters write it through declared ``metrics/*``
    fields so downstream evaluation, reporting, or export recipes operate on
    the same field substrate as predictions, losses, and summaries.
    """

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
                "MetricValue must be detached and non-differentiable.",
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
            coerce_mapping(
                metadata,
                owner="MetricValue",
                field="metadata",
                error_type=InvalidMetricResultError,
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_mapping(
                diagnostics,
                owner="MetricValue",
                field="diagnostics",
                error_type=InvalidMetricResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(
                provenance,
                owner="MetricValue",
                field="provenance",
                error_type=InvalidMetricResultError,
            ),
        )


MetricValue.__hash__ = None  # type: ignore[assignment]
