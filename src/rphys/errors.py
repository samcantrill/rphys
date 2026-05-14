"""Public base exceptions for remote physiological measurement components."""

from __future__ import annotations

__all__ = [
    "RemotePhysError",
    "InvalidDataKeyError",
    "InvalidDataTypeError",
    "InvalidFieldLocatorError",
    "InvalidMetadataKeyError",
    "InvalidSchemaNameError",
    "InvalidSplitNameError",
    "CollatePolicyError",
    "FieldSchemaError",
    "FieldTypeError",
    "MissingFieldError",
    "InvalidDataSourceRefError",
    "InvalidDataSourceSchemaError",
    "InvalidIndexItemError",
    "InvalidRecordRefError",
    "InvalidDataSourceSpecError",
    "InvalidDataSourceScanResultError",
    "InvalidDataSourceValidationError",
    "InvalidDataSourceViewError",
    "InvalidDataSourceFilterError",
    "InvalidIndexCandidateError",
    "InvalidFieldIndexError",
    "InvalidFieldRefError",
    "InvalidFieldViewError",
    "InvalidResourceRefError",
    "UnsupportedFieldIndexError",
    "InvalidCodecError",
    "CodecResolutionError",
    "UnsupportedCodecOperationError",
    "UnsupportedCodecIndexError",
    "CodecDependencyError",
    "CodecOperationError",
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


class InvalidDataKeyError(RemotePhysNameError, RemotePhysDataError):
    """Raised when an intrinsic field identity violates the data-key grammar."""


class InvalidFieldLocatorError(RemotePhysFieldError, RemotePhysNameError):
    """Raised when a role-qualified field locator cannot be parsed."""


class InvalidSchemaNameError(RemotePhysNameError, RemotePhysDataError):
    """Raised when a schema identity violates the versioned schema grammar."""


class InvalidDataTypeError(RemotePhysNameError, RemotePhysDataError):
    """Raised when a backend-agnostic data category label is invalid."""


class InvalidMetadataKeyError(RemotePhysMetadataError, RemotePhysNameError):
    """Raised when a descriptive metadata key violates the metadata grammar."""


class InvalidSplitNameError(RemotePhysNameError, RemotePhysDataSourceError):
    """Raised when a split label violates the split-name grammar."""


class MissingFieldError(RemotePhysFieldError, RemotePhysDataError):
    """Raised when a runtime field container lacks a required field."""


class FieldTypeError(RemotePhysFieldError, RemotePhysDataError):
    """Raised when a runtime field payload or declaration has the wrong type."""


class FieldSchemaError(RemotePhysFieldError, RemotePhysDataError):
    """Raised when a runtime field schema does not match a requirement."""


class CollatePolicyError(RemotePhysCollateError):
    """Raised when runtime collation cannot apply the requested policy."""


class InvalidResourceRefError(RemotePhysIOError):
    """Raised when a lazy physical resource descriptor is invalid."""


class InvalidFieldRefError(RemotePhysFieldError, RemotePhysIOError):
    """Raised when a lazy logical field descriptor is invalid."""


class InvalidFieldIndexError(RemotePhysSliceError, RemotePhysIOError):
    """Raised when a lazy field-native index descriptor is invalid."""


class InvalidFieldViewError(RemotePhysFieldError, RemotePhysSliceError, RemotePhysIOError):
    """Raised when a lazy field-view descriptor is invalid."""


class UnsupportedFieldIndexError(RemotePhysSliceError, RemotePhysIOError):
    """Raised when a serialized field index uses an unsupported Stage 3 tag."""


class InvalidCodecError(RemotePhysCodecError):
    """Raised when a registered codec object lacks the required shape."""


class CodecResolutionError(RemotePhysCodecError):
    """Raised when codec selection has no unique matching codec."""


class UnsupportedCodecOperationError(RemotePhysCodecError):
    """Raised when no registered codec declares support for an operation."""


class UnsupportedCodecIndexError(RemotePhysCodecError, RemotePhysSliceError):
    """Raised when a codec cannot materialize a requested field index."""


class CodecDependencyError(RemotePhysCodecError, RemotePhysDependencyError):
    """Raised when a codec operation cannot run because a dependency is absent."""


class CodecOperationError(RemotePhysCodecError):
    """Raised when a codec operation fails or returns an invalid result."""


class InvalidDataSourceSchemaError(RemotePhysDataSourceError, RemotePhysFieldError):
    """Raised when a declaration-only datasource schema descriptor is invalid."""


class InvalidDataSourceRefError(RemotePhysDataSourceError):
    """Raised when a lazy datasource provenance descriptor is invalid."""


class InvalidRecordRefError(RemotePhysDataSourceError, RemotePhysFieldError):
    """Raised when a lazy datasource record descriptor is invalid."""


class InvalidIndexItemError(RemotePhysDataSourceError, RemotePhysFieldError):
    """Raised when a role-qualified lazy index item descriptor is invalid."""


class InvalidDataSourceSpecError(RemotePhysDataSourceError):
    """Raised when a datasource scan specification is invalid."""


class InvalidDataSourceScanResultError(RemotePhysDataSourceError):
    """Raised when a descriptor-only datasource scan result is invalid."""


class InvalidDataSourceValidationError(RemotePhysDataSourceError):
    """Raised when datasource validation inputs or IO policy are invalid."""


class InvalidDataSourceViewError(RemotePhysDataSourceError):
    """Raised when a non-mutating datasource view request or result is invalid."""


class InvalidDataSourceFilterError(RemotePhysDataSourceError):
    """Raised when descriptor or candidate filtering inputs are invalid."""


class InvalidIndexCandidateError(RemotePhysDataSourceError, RemotePhysFieldError):
    """Raised when a provisional datasource index candidate is invalid."""
