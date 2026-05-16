"""Structural metric protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .context import MetricContext
from .results import MetricObservationCollection, MetricResult
from .specs import MetricContract, MetricObservationViewPlan

__all__ = ["Metric", "MetricObservationView"]


@runtime_checkable
class Metric(Protocol):
    """Backend-neutral metric behavior returning detached observations."""

    @property
    def contract(self) -> MetricContract:
        ...

    def __call__(self, context: MetricContext) -> MetricResult:
        ...


@runtime_checkable
class MetricObservationView(Protocol):
    """Structural observation view that returns metric observations.

    The public contract has no evaluator lifecycle methods such as ``reset``
    or ``update``. Stateful streaming, distributed synchronization, report
    tables, and dataframe adapters are future evaluator concerns.
    """

    @property
    def plan(self) -> MetricObservationViewPlan:
        ...

    def __call__(self, collection: MetricObservationCollection) -> MetricObservationCollection:
        ...
