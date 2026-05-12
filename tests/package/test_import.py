from __future__ import annotations

import importlib


PLANNED_PACKAGE_NAMES = [
    "rphys.analysis",
    "rphys.data",
    "rphys.datasources",
    "rphys.evaluation",
    "rphys.io",
    "rphys.learning",
    "rphys.losses",
    "rphys.methods",
    "rphys.metrics",
    "rphys.models",
    "rphys.nn",
    "rphys.objectives",
    "rphys.ops",
    "rphys.prediction",
    "rphys.training",
]

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


def test_import_rphys() -> None:
    import rphys

    assert rphys.__doc__
    assert rphys.__all__ == []


def test_planned_package_homes_import_with_empty_public_surfaces() -> None:
    for package_name in PLANNED_PACKAGE_NAMES:
        package = importlib.import_module(package_name)

        assert package.__doc__
        assert package.__all__ == []


def test_errors_import_and_expose_only_broad_error_categories() -> None:
    from rphys import errors

    assert errors.__all__ == ["RemotePhysError", *BROAD_ERROR_NAMES]

    for error_name in errors.__all__:
        error_type = getattr(errors, error_name)

        assert issubclass(error_type, errors.RemotePhysError)


def test_root_package_does_not_reexport_error_classes() -> None:
    import rphys

    assert not hasattr(rphys, "RemotePhysError")
    for error_name in BROAD_ERROR_NAMES:
        assert not hasattr(rphys, error_name)
