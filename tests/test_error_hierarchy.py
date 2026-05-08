"""Contract tests for public ``RemotePhys*Error`` classes."""

from __future__ import annotations

import rphys.errors as errors
from rphys.errors import (
    RemotePhysDataError,
    RemotePhysDatasetError,
    RemotePhysError,
    RemotePhysEvaluationError,
    RemotePhysIOError,
    RemotePhysTrainingError,
    RemotePhysTransformError,
)


EXPECTED_ERRORS = (
    RemotePhysError,
    RemotePhysDataError,
    RemotePhysIOError,
    RemotePhysDatasetError,
    RemotePhysTransformError,
    RemotePhysTrainingError,
    RemotePhysEvaluationError,
)


def test_error_classes_are_publicly_exported() -> None:
    assert set(errors.__all__) == {error.__name__ for error in EXPECTED_ERRORS}


def test_domain_errors_inherit_from_root_error() -> None:
    for error in EXPECTED_ERRORS[1:]:
        assert issubclass(error, RemotePhysError)
        assert issubclass(error, Exception)


def test_error_names_and_modules_are_stable() -> None:
    assert [error.__name__ for error in EXPECTED_ERRORS] == [
        "RemotePhysError",
        "RemotePhysDataError",
        "RemotePhysIOError",
        "RemotePhysDatasetError",
        "RemotePhysTransformError",
        "RemotePhysTrainingError",
        "RemotePhysEvaluationError",
    ]
    assert all(error.__module__ == "rphys.errors" for error in EXPECTED_ERRORS)
