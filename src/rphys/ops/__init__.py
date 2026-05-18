"""Public entrypoint for dependency-light runtime operation bindings.

Generic operation foundations are imported eagerly. Stage 7 sample and batch
operation families are exposed through lazy package attributes so importing
``rphys.ops`` does not load runtime container modules unless those specialized
names are requested.
"""

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
from .pipelines import BatchOperationPipeline, OperationPipeline, SampleOperationPipeline

if TYPE_CHECKING:
    from .batch import (
        BatchAugmentation,
        BatchAugmentationParams,
        BatchEquivalenceClaim,
        BatchEquivalenceReport,
        BatchFieldEffects,
        BatchOperation,
        BatchOperationContext,
        BatchOperationContract,
        BatchParameterScope,
        BatchTransform,
    )
    from .sample import (
        SampleFieldPermissions,
        SampleOperation,
        SampleAugmentationParams,
        SampleAugmentation,
        SampleOperationContext,
        SampleOperationContract,
        SampleReplayRecord,
        SampleCheck,
        SampleCollectionConcatOperation,
        SampleCollectionGroupOperation,
        SampleCollectionViewOperation,
        SampleDecision,
        SampleRoute,
        SampleTransform,
    )

_SAMPLE_EXPORTS = {
    "SampleFieldPermissions",
    "SampleOperationContract",
    "SampleOperationContext",
    "SampleReplayRecord",
    "SampleAugmentationParams",
    "SampleAugmentation",
    "SampleOperation",
    "SampleTransform",
    "SampleCheck",
    "SampleDecision",
    "SampleRoute",
    "SampleCollectionGroupOperation",
    "SampleCollectionViewOperation",
    "SampleCollectionConcatOperation",
}

_BATCH_EXPORTS = {
    "BatchParameterScope",
    "BatchEquivalenceClaim",
    "BatchFieldEffects",
    "BatchOperationContext",
    "BatchOperationContract",
    "BatchAugmentationParams",
    "BatchEquivalenceReport",
    "BatchOperation",
    "BatchTransform",
    "BatchAugmentation",
}


def __getattr__(name: str):  # pragma: no cover
    if name in _SAMPLE_EXPORTS:
        from importlib import import_module

        module = import_module(".sample", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    if name in _BATCH_EXPORTS:
        from importlib import import_module

        module = import_module(".batch", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(globals().keys()) | _SAMPLE_EXPORTS | _BATCH_EXPORTS)


__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
    "Operation",
    "OperationStep",
    "OperationContext",
    "OperationResult",
    "OperationPipeline",
    "SampleOperationPipeline",
    "BatchOperationPipeline",
    "FunctionalKernel",
    "SampleFieldPermissions",
    "SampleOperationContract",
    "SampleOperationContext",
    "SampleReplayRecord",
    "SampleAugmentationParams",
    "SampleAugmentation",
    "SampleOperation",
    "SampleTransform",
    "SampleCheck",
    "SampleDecision",
    "SampleRoute",
    "SampleCollectionGroupOperation",
    "SampleCollectionViewOperation",
    "SampleCollectionConcatOperation",
    "BatchParameterScope",
    "BatchEquivalenceClaim",
    "BatchFieldEffects",
    "BatchOperationContext",
    "BatchOperationContract",
    "BatchAugmentationParams",
    "BatchEquivalenceReport",
    "BatchOperation",
    "BatchTransform",
    "BatchAugmentation",
]
