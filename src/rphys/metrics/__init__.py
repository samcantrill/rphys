"""Field-native metric contracts and operation adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .context import MetricContext
from .core import Metric, MetricOutput
from .results import MetricValue
from .specs import GroupBySpec, MetricContract, MetricInputSpec

if TYPE_CHECKING:
    from .operations import (
        MetricCollectionOperation,
        MetricSampleOperation,
        collect_metric_fields,
    )

_OPERATION_EXPORTS = {
    "MetricCollectionOperation",
    "MetricSampleOperation",
    "collect_metric_fields",
}


def __getattr__(name: str):  # pragma: no cover
    if name in _OPERATION_EXPORTS:
        from importlib import import_module

        module = import_module(".operations", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(globals().keys()) | _OPERATION_EXPORTS)


__all__ = [
    "GroupBySpec",
    "Metric",
    "MetricCollectionOperation",
    "MetricContext",
    "MetricContract",
    "MetricInputSpec",
    "MetricOutput",
    "MetricSampleOperation",
    "MetricValue",
    "collect_metric_fields",
]
