"""Structural metric protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, TypeAlias, runtime_checkable

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from .context import MetricContext
from .results import MetricValue
from .specs import MetricContract

MetricOutput: TypeAlias = (
    Mapping[FieldLocator | str, FieldValue | MetricValue | object]
    | FieldValue
    | MetricValue
    | object
)

__all__ = ["Metric", "MetricOutput"]


@runtime_checkable
class Metric(Protocol):
    """Backend-neutral metric behavior returning field-native outputs.

    Metrics declare their writable ``metrics/*`` fields on
    :class:`MetricContract`. Callables may return a mapping from declared
    locators to ``FieldValue`` or ``MetricValue`` payloads, or a single value
    when the contract declares exactly one write. Public observation/result
    records are intentionally absent in Stage 13.
    """

    @property
    def contract(self) -> MetricContract:
        ...

    def __call__(self, context: MetricContext) -> MetricOutput:
        ...
