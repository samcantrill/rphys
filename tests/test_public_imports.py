"""Contract tests for the first stable package import surface."""

from __future__ import annotations

import importlib
import importlib.util


STABLE_MODULES = (
    "rphys",
    "rphys.errors",
    "rphys.data",
    "rphys.io",
    "rphys.datasets",
    "rphys.transforms",
)

DEFERRED_MODULES = (
    "rphys.analysis",
    "rphys.evaluation",
    "rphys.losses",
    "rphys.methods",
    "rphys.models",
    "rphys.ops",
    "rphys.recipes",
    "rphys.stages",
    "rphys.testing",
    "rphys.training",
)


def test_first_wave_modules_are_importable() -> None:
    for module_name in STABLE_MODULES:
        assert importlib.import_module(module_name).__name__ == module_name


def test_deferred_module_homes_are_not_created_early() -> None:
    import rphys

    for module_name in DEFERRED_MODULES:
        assert importlib.util.find_spec(module_name) is None
        assert not hasattr(rphys, module_name.rsplit(".", maxsplit=1)[-1])


def test_rphys_data_exports_phase_1_runtime_contracts() -> None:
    module = importlib.import_module("rphys.data")

    assert set(module.__all__) == {
        "ANNOTATION_NAMESPACE",
        "BODY_NAMESPACE",
        "CAMERA_NAMESPACE",
        "CUSTOM_NAMESPACE",
        "CollatePolicy",
        "DataKey",
        "FACE_NAMESPACE",
        "FieldSpec",
        "FieldValue",
        "LABEL_NAMESPACE",
        "PREDICTION_NAMESPACE",
        "QUALITY_NAMESPACE",
        "SIGNAL_NAMESPACE",
        "STANDARD_NAMESPACES",
        "TIMESTAMPS_NAMESPACE",
        "VIDEO_NAMESPACE",
        "VIEW_NAMESPACE",
    }


def test_unimplemented_first_wave_domain_modules_export_no_placeholders() -> None:
    for module_name in ("rphys.io", "rphys.datasets", "rphys.transforms"):
        module = importlib.import_module(module_name)
        public_names = [name for name in vars(module) if not name.startswith("_")]

        assert public_names == []


def test_rphys_data_does_not_export_future_runtime_or_io_contracts() -> None:
    import rphys.data as data

    for name in (
        "Batch",
        "CollateContext",
        "DataObjectBase",
        "FieldRef",
        "FieldView",
        "Sample",
        "SampleContract",
        "TemporalIndexSlice",
        "collate_samples",
    ):
        assert not hasattr(data, name)
