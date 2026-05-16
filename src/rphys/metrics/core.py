"""Structural metric protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .context import MetricContext
from .results import MetricResult
from .specs import MetricContract

__all__ = ["Metric"]


@runtime_checkable
class Metric(Protocol):
    """Backend-neutral metric behavior returning detached observations."""

    @property
    def contract(self) -> MetricContract:
        ...

    def __call__(self, context: MetricContext) -> MetricResult:
        ...
