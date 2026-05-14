from __future__ import annotations

import pytest

from rphys import errors

BROAD_ERROR_NAMES = [
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

STAGE_1_ERROR_NAMES = [
    "InvalidDataKeyError",
    "InvalidDataTypeError",
    "InvalidFieldLocatorError",
    "InvalidMetadataKeyError",
    "InvalidSchemaNameError",
    "InvalidSplitNameError",
]

STAGE_2_ERROR_NAMES = [
    "CollatePolicyError",
    "FieldSchemaError",
    "FieldTypeError",
    "MissingFieldError",
]

STAGE_3_IO_ERROR_NAMES = [
    "InvalidFieldIndexError",
    "InvalidFieldRefError",
    "InvalidFieldViewError",
    "InvalidResourceRefError",
    "UnsupportedFieldIndexError",
]

STAGE_4_CODEC_ERROR_NAMES = [
    "InvalidCodecError",
    "CodecResolutionError",
    "UnsupportedCodecOperationError",
    "UnsupportedCodecIndexError",
    "CodecDependencyError",
    "CodecOperationError",
]

STAGE_3_DATASOURCE_ERROR_NAMES = [
    "InvalidDataSourceRefError",
    "InvalidDataSourceSchemaError",
    "InvalidIndexItemError",
    "InvalidRecordRefError",
]

STAGE_5_DATASOURCE_ERROR_NAMES = [
    "InvalidDataSourceSpecError",
    "InvalidDataSourceScanResultError",
    "InvalidDataSourceValidationError",
    "InvalidDataSourceViewError",
    "InvalidDataSourceFilterError",
    "InvalidIndexCandidateError",
]


def test_errors_public_surface_lists_only_implemented_error_names() -> None:
    assert errors.__all__ == [
        "RemotePhysError",
        *STAGE_1_ERROR_NAMES,
        *STAGE_2_ERROR_NAMES,
        *STAGE_3_DATASOURCE_ERROR_NAMES,
        *STAGE_5_DATASOURCE_ERROR_NAMES,
        *STAGE_3_IO_ERROR_NAMES,
        *STAGE_4_CODEC_ERROR_NAMES,
        *BROAD_ERROR_NAMES,
    ]


def test_remote_phys_error_preserves_message_args_and_context() -> None:
    exc = errors.RemotePhysError(
        "invalid field",
        key="inputs/video.rgb",
        expected="data key",
    )

    assert str(exc) == "invalid field"
    assert exc.args == ("invalid field",)
    assert exc.message == "invalid field"
    assert exc.context == {
        "key": "inputs/video.rgb",
        "expected": "data key",
    }


def test_remote_phys_error_copies_context() -> None:
    metadata = {"source": "fixture"}
    context = {"metadata": metadata}

    exc = errors.RemotePhysError("bad metadata", **context)
    context["metadata"] = {"source": "mutated"}

    assert exc.context == {"metadata": metadata}
    assert exc.context is not context


def test_remote_phys_error_allows_empty_context() -> None:
    exc = errors.RemotePhysError("plain error")

    assert exc.context == {}


@pytest.mark.parametrize(
    "error_name",
    BROAD_ERROR_NAMES,
)
def test_broad_error_categories_inherit_base_behavior(error_name: str) -> None:
    error_type = getattr(errors, error_name)
    exc = error_type("category failure", locator="inputs/video.rgb")

    assert isinstance(exc, errors.RemotePhysError)
    assert str(exc) == "category failure"
    assert exc.context == {"locator": "inputs/video.rgb"}


def test_stage_1_errors_are_exported() -> None:
    for error_name in STAGE_1_ERROR_NAMES:
        assert error_name in errors.__all__


def test_stage_2_runtime_errors_are_exported() -> None:
    for error_name in STAGE_2_ERROR_NAMES:
        assert error_name in errors.__all__


@pytest.mark.parametrize("error_name", STAGE_1_ERROR_NAMES)
def test_stage_1_errors_preserve_base_message_and_context(error_name: str) -> None:
    error_type = getattr(errors, error_name)

    exc = error_type("invalid vocabulary", actual="Video.RGB", expected="lowercase")

    assert isinstance(exc, errors.RemotePhysError)
    assert isinstance(exc, errors.RemotePhysNameError)
    assert str(exc) == "invalid vocabulary"
    assert exc.args == ("invalid vocabulary",)
    assert exc.message == "invalid vocabulary"
    assert exc.context == {
        "actual": "Video.RGB",
        "expected": "lowercase",
    }


def test_stage_1_errors_map_to_broad_categories() -> None:
    assert issubclass(errors.InvalidDataKeyError, errors.RemotePhysDataError)
    assert issubclass(errors.InvalidDataTypeError, errors.RemotePhysDataError)
    assert issubclass(errors.InvalidFieldLocatorError, errors.RemotePhysFieldError)
    assert issubclass(errors.InvalidMetadataKeyError, errors.RemotePhysMetadataError)
    assert issubclass(errors.InvalidSchemaNameError, errors.RemotePhysDataError)
    assert issubclass(errors.InvalidSplitNameError, errors.RemotePhysDataSourceError)


def test_stage_2_errors_map_to_runtime_categories() -> None:
    assert issubclass(errors.MissingFieldError, errors.RemotePhysFieldError)
    assert issubclass(errors.MissingFieldError, errors.RemotePhysDataError)
    assert issubclass(errors.FieldTypeError, errors.RemotePhysFieldError)
    assert issubclass(errors.FieldTypeError, errors.RemotePhysDataError)
    assert issubclass(errors.FieldSchemaError, errors.RemotePhysFieldError)
    assert issubclass(errors.FieldSchemaError, errors.RemotePhysDataError)
    assert issubclass(errors.CollatePolicyError, errors.RemotePhysCollateError)


def test_stage_3_io_errors_map_to_approved_categories() -> None:
    assert issubclass(errors.InvalidResourceRefError, errors.RemotePhysIOError)
    assert issubclass(errors.InvalidFieldRefError, errors.RemotePhysFieldError)
    assert issubclass(errors.InvalidFieldRefError, errors.RemotePhysIOError)
    assert issubclass(errors.InvalidFieldIndexError, errors.RemotePhysSliceError)
    assert issubclass(errors.InvalidFieldIndexError, errors.RemotePhysIOError)
    assert issubclass(errors.InvalidFieldViewError, errors.RemotePhysFieldError)
    assert issubclass(errors.InvalidFieldViewError, errors.RemotePhysSliceError)
    assert issubclass(errors.InvalidFieldViewError, errors.RemotePhysIOError)
    assert issubclass(errors.UnsupportedFieldIndexError, errors.RemotePhysSliceError)
    assert issubclass(errors.UnsupportedFieldIndexError, errors.RemotePhysIOError)


def test_stage_4_codec_errors_map_to_approved_categories() -> None:
    assert issubclass(errors.InvalidCodecError, errors.RemotePhysCodecError)
    assert issubclass(errors.CodecResolutionError, errors.RemotePhysCodecError)
    assert issubclass(
        errors.UnsupportedCodecOperationError,
        errors.RemotePhysCodecError,
    )
    assert issubclass(errors.UnsupportedCodecIndexError, errors.RemotePhysCodecError)
    assert issubclass(errors.UnsupportedCodecIndexError, errors.RemotePhysSliceError)
    assert issubclass(errors.CodecDependencyError, errors.RemotePhysCodecError)
    assert issubclass(errors.CodecDependencyError, errors.RemotePhysDependencyError)
    assert issubclass(errors.CodecOperationError, errors.RemotePhysCodecError)


def test_stage_3_datasource_errors_map_to_approved_categories() -> None:
    assert issubclass(
        errors.InvalidDataSourceSchemaError,
        errors.RemotePhysDataSourceError,
    )
    assert issubclass(errors.InvalidDataSourceSchemaError, errors.RemotePhysFieldError)
    assert issubclass(errors.InvalidDataSourceRefError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidRecordRefError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidRecordRefError, errors.RemotePhysFieldError)
    assert issubclass(errors.InvalidIndexItemError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidIndexItemError, errors.RemotePhysFieldError)


def test_stage_5_datasource_errors_map_to_approved_categories() -> None:
    assert issubclass(errors.InvalidDataSourceSpecError, errors.RemotePhysDataSourceError)
    assert issubclass(
        errors.InvalidDataSourceScanResultError,
        errors.RemotePhysDataSourceError,
    )
    assert issubclass(
        errors.InvalidDataSourceValidationError,
        errors.RemotePhysDataSourceError,
    )
    assert issubclass(errors.InvalidDataSourceViewError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidDataSourceFilterError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidIndexCandidateError, errors.RemotePhysDataSourceError)
    assert issubclass(errors.InvalidIndexCandidateError, errors.RemotePhysFieldError)


def test_deferred_runtime_errors_are_not_defined() -> None:
    assert not hasattr(errors, "MissingMetadataError")
    assert not hasattr(errors, "ShapeMismatchError")
