"""Metric execution context records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from rphys.data import FieldContainer
from rphys.data.collections import SampleCollection
from rphys.errors import InvalidMetricContextError

from ._validation import coerce_mapping
from .specs import MetricContract

__all__ = ["MetricContext"]


@dataclass(frozen=True, init=False, slots=True)
class MetricContext:
    """Runtime context for metric calls over fields or sample collections."""

    contract: MetricContract
    fields: FieldContainer | None
    samples: SampleCollection | None
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        contract: MetricContract,
        *,
        fields: FieldContainer | None = None,
        samples: SampleCollection | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(contract, MetricContract):
            raise InvalidMetricContextError(
                "MetricContext contract must be a MetricContract.",
                owner="MetricContext",
                field="contract",
                expected="MetricContract",
                actual=type(contract).__name__,
            )
        if fields is not None:
            _validate_field_container(fields)
        if samples is not None and not isinstance(samples, SampleCollection):
            raise InvalidMetricContextError(
                "MetricContext samples must be a SampleCollection.",
                owner="MetricContext",
                field="samples",
                expected="SampleCollection | None",
                actual=type(samples).__name__,
            )
        object.__setattr__(self, "contract", contract)
        object.__setattr__(self, "fields", fields)
        object.__setattr__(self, "samples", samples)
        object.__setattr__(
            self,
            "metadata",
            coerce_mapping(
                metadata,
                owner="MetricContext",
                field="metadata",
                error_type=InvalidMetricContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_mapping(
                provenance,
                owner="MetricContext",
                field="provenance",
                error_type=InvalidMetricContextError,
            ),
        )


def _validate_field_container(fields: object) -> None:
    for method_name in ("has", "field", "get", "require", "role", "field_items"):
        method = getattr(fields, method_name, None)
        if method is None or not callable(method):
            raise InvalidMetricContextError(
                "MetricContext fields must satisfy the FieldContainer protocol.",
                owner="MetricContext",
                field="fields",
                method=method_name,
                actual=type(fields).__name__,
            )


MetricContext.__hash__ = None  # type: ignore[assignment]
