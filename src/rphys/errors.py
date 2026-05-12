"""Public base exceptions for remote physiological measurement components."""

from __future__ import annotations

__all__ = [
    "RemotePhysError",
    "RemotePhysAnalysisError",
    "RemotePhysCodecError",
    "RemotePhysCollateError",
    "RemotePhysDataError",
    "RemotePhysDataSourceError",
    "RemotePhysDependencyError",
    "RemotePhysEvaluationError",
    "RemotePhysFieldError",
    "RemotePhysIOError",
    "RemotePhysLearningError",
    "RemotePhysMetadataError",
    "RemotePhysMethodError",
    "RemotePhysNameError",
    "RemotePhysOperationError",
    "RemotePhysPipelineError",
    "RemotePhysSliceError",
    "RemotePhysTrainingError",
]


class RemotePhysError(Exception):
    """Base exception with a readable message and inspectable context."""

    def __init__(self, message: str, **context: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = dict(context)


class RemotePhysDataError(RemotePhysError):
    """Base error for data container, key, schema, and value failures."""


class RemotePhysFieldError(RemotePhysError):
    """Base error for field addressing, presence, and type failures."""


class RemotePhysDataSourceError(RemotePhysError):
    """Base error for datasource discovery, views, indexes, and splits."""


class RemotePhysIOError(RemotePhysError):
    """Base error for resource references, lazy IO, and persistence."""


class RemotePhysCodecError(RemotePhysError):
    """Base error for codec selection, loading, and saving failures."""


class RemotePhysSliceError(RemotePhysError):
    """Base error for temporal or indexed slice failures."""


class RemotePhysCollateError(RemotePhysError):
    """Base error for batch collation and shape compatibility failures."""


class RemotePhysOperationError(RemotePhysError):
    """Base error for operation contract and execution failures."""


class RemotePhysPipelineError(RemotePhysError):
    """Base error for pipeline composition and execution failures."""


class RemotePhysMethodError(RemotePhysError):
    """Base error for batch-level prediction or representation methods."""


class RemotePhysLearningError(RemotePhysError):
    """Base error for learner and optimization-loop failures."""


class RemotePhysTrainingError(RemotePhysError):
    """Base error for trainer orchestration and training-state failures."""


class RemotePhysEvaluationError(RemotePhysError):
    """Base error for evaluation and reporting failures."""


class RemotePhysAnalysisError(RemotePhysError):
    """Base error for analysis and derived-result failures."""


class RemotePhysDependencyError(RemotePhysError):
    """Base error for unavailable or incompatible optional dependencies."""


class RemotePhysNameError(RemotePhysError):
    """Base error for rphys naming vocabulary failures."""


class RemotePhysMetadataError(RemotePhysError):
    """Base error for metadata key, value, and availability failures."""
