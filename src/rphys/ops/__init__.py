"""Public entrypoint for runtime operation bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .core import Operation, OperationStep
from .context import OperationContext, OperationResult
from .kernels import FunctionalKernel
from .pipelines import OperationPipeline

if TYPE_CHECKING:
    from .sample import (
        SampleFieldPermissions,
        SampleOperation,
        SampleOperationContext,
        SampleOperationContract,
        SampleReplayRecord,
    )

_SAMPLE_EXPORTS = {
    "SampleFieldPermissions",
    "SampleOperationContract",
    "SampleOperationContext",
    "SampleReplayRecord",
    "SampleOperation",
}


def __getattr__(name: str):  # pragma: no cover
    if name in _SAMPLE_EXPORTS:
        from importlib import import_module

        module = import_module(".sample", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(globals().keys()) | _SAMPLE_EXPORTS)


__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
    "Operation",
    "OperationStep",
    "OperationContext",
    "OperationResult",
    "OperationPipeline",
    "FunctionalKernel",
    "SampleFieldPermissions",
    "SampleOperationContract",
    "SampleOperationContext",
    "SampleReplayRecord",
    "SampleOperation",
]
