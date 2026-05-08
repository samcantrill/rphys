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


def test_first_wave_domain_modules_export_no_placeholders() -> None:
    for module_name in ("rphys.data", "rphys.io", "rphys.datasets", "rphys.transforms"):
        module = importlib.import_module(module_name)
        public_names = [name for name in vars(module) if not name.startswith("_")]

        assert public_names == []
