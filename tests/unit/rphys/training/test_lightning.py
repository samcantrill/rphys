from __future__ import annotations

import sys
from types import ModuleType

import pytest

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext, LoopMode
from rphys.metrics import MetricValue
from rphys.training import PrecisionPolicy, Trainer, TrainingOutputSpec, TrainingPlan, TrainingStatus
from rphys.training.lightning import (
    LightningDependencyStatus,
    LightningTrainerConfig,
    LightningTrainingEngine,
    fit_lightning_module,
    preflight_lightning_dependency,
)

import rphys.training.lightning as lightning_adapter


class FakeLightningModule:
    pass


class FakeTrainer:
    instances: list["FakeTrainer"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.calls: list[tuple[str, object, dict[str, object]]] = []
        self.global_step = 3
        self.current_epoch = 2
        self.training_step_output: object | None = None
        FakeTrainer.instances.append(self)

    def fit(self, model: object, **kwargs: object) -> list[dict[str, float]]:
        self.calls.append(("fit", model, kwargs))
        train_dataloaders = kwargs.get("train_dataloaders")
        if train_dataloaders is not None and hasattr(model, "training_step"):
            batch = next(iter(train_dataloaders))  # type: ignore[arg-type]
            self.training_step_output = model.training_step(batch, 0)
        return [{"train_metric": 1.5}]

    def validate(self, model: object | None = None, **kwargs: object) -> list[dict[str, float]]:
        self.calls.append(("validate", model, kwargs))
        return [{"val_loss": 0.25}]

    def test(self, model: object | None = None, **kwargs: object) -> list[dict[str, float]]:
        self.calls.append(("test", model, kwargs))
        return [{"test_loss": 0.5}]

    def predict(self, model: object | None = None, **kwargs: object) -> list[dict[str, int]]:
        self.calls.append(("predict", model, kwargs))
        return [{"prediction_count": 2}]


class FakeScalar:
    def __init__(self) -> None:
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1


class RecordingLearner:
    def __init__(self) -> None:
        self.contexts: list[LoopContext] = []

    def step(self, batch: Batch, context: LoopContext) -> Batch:
        self.contexts.append(context)
        output = batch.shallow_copy()
        if context.mode is LoopMode.TRAIN:
            output.set_field("objectives/custom.training.total", FieldValue(FakeScalar()))
        output.set_field("metrics/custom.training.mae", FieldValue(MetricValue(0.5, unit="bpm")))
        return output


def test_lightning_preflight_reports_absent_available_and_unsafe(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_version(name: str) -> str:
        raise lightning_adapter.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(lightning_adapter.metadata, "version", missing_version)
    absent = preflight_lightning_dependency()
    assert absent.status is LightningDependencyStatus.ABSENT
    assert "lightning" in (absent.reason or "")

    monkeypatch.setattr(lightning_adapter.metadata, "version", lambda name: "2.6.1")
    available = preflight_lightning_dependency()
    assert available.status is LightningDependencyStatus.AVAILABLE
    assert available.version == "2.6.1"

    monkeypatch.setattr(lightning_adapter.metadata, "version", lambda name: "2.6.2")
    unsafe = preflight_lightning_dependency()
    assert unsafe.status is LightningDependencyStatus.UNSAFE
    assert unsafe.advisory_url == lightning_adapter.LIGHTNING_SECURITY_ADVISORY_URL


def test_lightning_engine_blocks_unsafe_dependency_before_import(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lightning_adapter.metadata, "version", lambda name: "2.6.2")

    def forbidden_import(name: str) -> object:
        raise AssertionError(f"unsafe dependency was imported: {name}")

    monkeypatch.setattr(lightning_adapter.importlib, "import_module", forbidden_import)

    result = LightningTrainingEngine().fit(TrainingPlan(), RecordingLearner())

    assert result.status is TrainingStatus.FAILED
    assert result.failure is not None
    assert "GHSA-w37p-236h-pfx3" in result.failure
    assert result.training_profile is not None
    assert "lightning_preflight:unsafe" in result.training_profile.decisions


def test_lightning_trainer_config_rejects_unknown_trainer_kwargs() -> None:
    config = LightningTrainerConfig({"max_epochs": 2, "enable_checkpointing": False})
    assert config.to_kwargs() == {"max_epochs": 2, "enable_checkpointing": False}

    with pytest.raises(RemotePhysTrainingError) as error:
        LightningTrainerConfig({"private_loop_state": object()})
    assert error.value.context["field"] == "trainer_kwargs"
    assert error.value.context["key"] == "private_loop_state"


def test_lightning_training_engine_runs_shared_rphys_learner_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_lightning(monkeypatch)
    plan = TrainingPlan(
        train_batches=(Batch(),),
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.mae",),
        ),
    )
    learner = RecordingLearner()
    engine = LightningTrainingEngine(
        trainer_kwargs={"max_epochs": 2},
        precision_policy=PrecisionPolicy("32"),
    )

    result = Trainer(engine=engine).fit(plan, learner)

    assert result.status is TrainingStatus.COMPLETED
    assert result.mode is LoopMode.TRAIN
    assert result.metrics["train_metric"].value == 1.5
    assert learner.contexts[0].mode is LoopMode.TRAIN
    assert FakeTrainer.instances[-1].kwargs["precision"] == "32-true"
    assert FakeTrainer.instances[-1].calls[0][2]["train_dataloaders"] is plan.train_batches
    assert isinstance(FakeTrainer.instances[-1].training_step_output, FakeScalar)
    assert result.training_profile is not None
    assert "precision.applied:32-true" in result.training_profile.decisions


def test_fit_lightning_module_uses_direct_lightning_entrypoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_lightning(monkeypatch)
    model = FakeLightningModule()

    result = fit_lightning_module(
        model,
        train_dataloaders=("batch",),
        trainer_kwargs={"max_epochs": 1},
        ckpt_path="last",
    )

    trainer = FakeTrainer.instances[-1]
    assert result.status is TrainingStatus.COMPLETED
    assert trainer.calls[0][0] == "fit"
    assert trainer.calls[0][1] is model
    assert trainer.calls[0][2]["ckpt_path"] == "last"
    assert trainer.kwargs["max_epochs"] == 1


def test_lightning_entrypoint_rejects_datamodule_and_dataloader_mix() -> None:
    with pytest.raises(RemotePhysTrainingError) as error:
        fit_lightning_module(object(), train_dataloaders=("batch",), datamodule=object())
    assert error.value.context["field"] == "datamodule"


def _install_fake_lightning(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeTrainer.instances.clear()
    fake_parent = ModuleType("lightning")
    fake_module = ModuleType("lightning.pytorch")
    fake_module.Trainer = FakeTrainer
    fake_module.LightningModule = FakeLightningModule
    fake_parent.pytorch = fake_module

    monkeypatch.setitem(sys.modules, "lightning", fake_parent)
    monkeypatch.setitem(sys.modules, "lightning.pytorch", fake_module)

    def safe_version(name: str) -> str:
        if name == "lightning":
            return "2.6.1"
        raise lightning_adapter.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(lightning_adapter.metadata, "version", safe_version)
