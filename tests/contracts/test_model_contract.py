from __future__ import annotations

import importlib
import sys

from rphys.models import Model


class SumModel:
    def __call__(self, inputs: tuple[float, ...]) -> float:
        return sum(inputs)


def test_model_contract_is_structural_callable_below_batch() -> None:
    model = SumModel()

    assert isinstance(model, Model)
    assert model((1.0, 2.0, 3.0)) == 6.0


def test_model_core_import_does_not_load_runtime_containers_or_method_stack(
    monkeypatch,
) -> None:
    _remove_import_tree(monkeypatch, "rphys.models.core")
    for module_name in [
        "rphys.data",
        "rphys.methods",
        "rphys.datasources",
        "rphys.training",
        "torch",
    ]:
        _remove_import_tree(monkeypatch, module_name)

    importlib.import_module("rphys.models.core")

    for forbidden in [
        "rphys.data",
        "rphys.methods",
        "rphys.datasources",
        "rphys.training",
        "torch",
    ]:
        assert forbidden not in sys.modules


def test_model_contract_does_not_define_framework_or_trainer_hooks() -> None:
    model = SumModel()

    for forbidden in [
        "predict",
        "training_step",
        "validation_step",
        "configure_optimizers",
        "to",
        "compile",
        "save_checkpoint",
    ]:
        assert not hasattr(model, forbidden)


def _remove_import_tree(monkeypatch, root: str) -> None:
    for module_name in sorted(
        [
            name
            for name in sys.modules
            if name == root or name.startswith(f"{root}.")
        ],
        key=len,
        reverse=True,
    ):
        parent_name, _, child_name = module_name.rpartition(".")
        parent = sys.modules.get(parent_name)
        if parent is not None:
            monkeypatch.delattr(parent, child_name, raising=False)
        monkeypatch.delitem(sys.modules, module_name, raising=False)
