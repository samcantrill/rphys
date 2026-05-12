from __future__ import annotations

import pytest

from rphys import errors


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
    [
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
    ],
)
def test_broad_error_categories_inherit_base_behavior(error_name: str) -> None:
    error_type = getattr(errors, error_name)
    exc = error_type("category failure", locator="inputs/video.rgb")

    assert isinstance(exc, errors.RemotePhysError)
    assert str(exc) == "category failure"
    assert exc.context == {"locator": "inputs/video.rgb"}
