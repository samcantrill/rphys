from __future__ import annotations

import sys
from types import ModuleType

import pytest

from rphys.data import Batch, FieldValue
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopContext, LoopMode
from rphys.metrics import MetricValue
from rphys.training import (
    AsyncTrainingProfileWriter,
    CheckpointCatalog,
    CheckpointMetricDirection,
    CheckpointPrunePolicy,
    CheckpointRef,
    CheckpointRefStatus,
    CheckpointRestorePolicy,
    CheckpointSavePolicy,
    CheckpointSelection,
    CheckpointSelectionMode,
    DataFieldProbeSummary,
    DataProbeSummary,
    FakeCPUResourceProbe,
    InMemoryProfileWriterBackend,
    ModelGradientProbeSummary,
    ModelProbeSummary,
    PrecisionPolicy,
    ProbeCadence,
    ProbeHookPoint,
    ProbeSelector,
    ProbeSelectorMode,
    ResourceMonitor,
    ResourceMonitorExecutionMode,
    Trainer,
    TrainingEventPhase,
    TrainingOutputSpec,
    TrainingPlan,
    TrainingStatus,
)
from rphys.training.lightning import (
    LightningBridgeCallback,
    LightningDependencyStatus,
    LightningProfilerBridge,
    LightningTrainerConfig,
    LightningTrainingEngine,
    fit_lightning_module,
    map_lightning_checkpoint_policies,
    preflight_lightning_dependency,
)

import rphys.training.lightning as lightning_adapter


class FakeLightningModule:
    pass


class FakeTrainer:
    instances: list["FakeTrainer"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        callbacks = kwargs.get("callbacks", ())
        if callbacks is None:
            self.callbacks = []
        elif isinstance(callbacks, (list, tuple)):
            self.callbacks = list(callbacks)
        else:
            self.callbacks = [callbacks]
        self.profiler = kwargs.get("profiler")
        self.calls: list[tuple[str, object, dict[str, object]]] = []
        self.global_step = 3
        self.current_epoch = 2
        self.local_rank = 0
        self.global_rank = 1
        self.strategy = "fake-ddp"
        self.training_step_output: object | None = None
        FakeTrainer.instances.append(self)

    def fit(self, model: object, **kwargs: object) -> list[dict[str, float]]:
        self.calls.append(("fit", model, kwargs))
        self._call_profiler("setup", "fit", local_rank=self.local_rank, log_dir="fake-lightning")
        self._call_callbacks("setup", model, stage="fit")
        self._call_callbacks("on_fit_start", model)
        train_dataloaders = kwargs.get("train_dataloaders")
        if train_dataloaders is not None and hasattr(model, "training_step"):
            batch = next(iter(train_dataloaders))  # type: ignore[arg-type]
            self._call_callbacks("on_train_batch_start", model, batch, 0)
            self._call_profiler("start", "train_batch")
            self.training_step_output = model.training_step(batch, 0)
            self._call_callbacks("on_before_backward", model, self.training_step_output)
            backward = getattr(self.training_step_output, "backward", None)
            if callable(backward):
                backward()
            self._call_callbacks("on_after_backward", model)
            self._call_callbacks("on_before_optimizer_step", model, object())
            self.global_step += 1
            self._call_profiler("stop", "train_batch")
            self._call_callbacks("on_train_batch_end", model, self.training_step_output, batch, 0)
            self._call_callbacks("on_save_checkpoint", model, {"global_step": self.global_step})
        self._call_callbacks("on_fit_end", model)
        self._call_callbacks("teardown", model, stage="fit")
        self._call_profiler("teardown", "fit")
        self._call_profiler("describe")
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

    def _call_callbacks(self, hook_name: str, model: object | None, *args: object, **kwargs: object) -> None:
        for callback in self.callbacks:
            hook = getattr(callback, hook_name, None)
            if callable(hook):
                hook(self, model, *args, **kwargs)

    def _call_profiler(self, method_name: str, *args: object, **kwargs: object) -> None:
        method = getattr(self.profiler, method_name, None)
        if callable(method):
            method(*args, **kwargs)


class FakeModelCheckpoint:
    instances: list["FakeModelCheckpoint"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.last_model_path = "last.ckpt" if kwargs.get("save_last") else ""
        self.best_model_path = "best.ckpt" if kwargs.get("monitor") else ""
        self.best_k_models = {"best.ckpt": 0.1} if kwargs.get("save_top_k") not in (None, 0) else {}
        FakeModelCheckpoint.instances.append(self)


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


class FakeLightningProbe:
    probe_id = "fake-lightning-probe"

    def collect(self, context: dict[object, object]) -> tuple[object, ...]:
        hook_point = context["hook_point"]
        selector = ProbeSelector(ProbeSelectorMode.ALL)
        cadence = ProbeCadence()
        common = {
            "run_id": context.get("run_id"),
            "timeline_id": context.get("timeline_id"),
            "batch_index": context.get("batch_index"),
            "local_rank": context.get("local_rank"),
            "global_rank": context.get("global_rank"),
            "process_id": context.get("process_id"),
            "node_id": context.get("node_id"),
            "device_id": context.get("device_id"),
            "metadata": {"bridge": "lightning"},
            "provenance": {"engine": "LightningTrainingEngine"},
        }
        if hook_point is ProbeHookPoint.BACKWARD:
            summary = ModelProbeSummary(
                self.probe_id,
                "gradient_norm",
                hook_point=hook_point,
                selector=selector,
                cadence=cadence,
                value=2.0,
                **common,
            )
            return (ModelGradientProbeSummary(summary, gradient_norm=2.0),)
        if hook_point is ProbeHookPoint.POST_DEVICE_TRANSFER:
            summary = DataProbeSummary(
                self.probe_id,
                "batch_quality",
                hook_point=hook_point,
                selector=selector,
                cadence=cadence,
                **common,
            )
            return (
                DataFieldProbeSummary(
                    summary,
                    field="signals/ppg",
                    shape=("batch", "time"),
                    dtype="float32",
                    present_ratio=1.0,
                ),
            )
        return ()


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


def test_lightning_checkpoint_policy_mapping_covers_public_checkpoint_kwargs() -> None:
    mapping = map_lightning_checkpoint_policies(
        save_policy=CheckpointSavePolicy(
            by_step=5,
            by_epoch=1,
            on_metric=True,
            metric_name="val_loss",
            metric_direction=CheckpointMetricDirection.MIN,
            on_failure=True,
            on_final=True,
        ),
        prune_policy=CheckpointPrunePolicy(
            keep_best=2,
            best_metric_name="val_loss",
            best_metric_direction=CheckpointMetricDirection.MIN,
            keep_recent=3,
        ),
    )

    kwargs = mapping.to_kwargs()
    assert kwargs["every_n_train_steps"] == 5
    assert kwargs["every_n_epochs"] == 1
    assert kwargs["monitor"] == "val_loss"
    assert kwargs["mode"] == "min"
    assert kwargs["save_on_exception"] is True
    assert kwargs["save_last"] is True
    assert kwargs["save_top_k"] == 2
    assert mapping.requires_recency_pruner is True
    assert "checkpoint.recency_pruner:3" in mapping.diagnostics


def test_lightning_profiler_bridge_supports_public_profile_context_manager() -> None:
    profiler = LightningProfilerBridge(mode=LoopMode.TRAIN)

    with profiler.profile("manual_scope") as action_name:
        assert action_name == "manual_scope"

    assert profiler.summary() == ""
    assert any(span.name == "lightning.profiler.manual_scope" for span in profiler.training_profile.scalar_spans)


def test_lightning_bridge_records_ranked_profile_checkpoint_probe_and_writer_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_lightning(monkeypatch)
    writer_backend = InMemoryProfileWriterBackend()
    writer = AsyncTrainingProfileWriter(writer_backend, queue_capacity=64)
    monitor = ResourceMonitor(
        FakeCPUResourceProbe(values=(10.0, 20.0), probe_id="fake-cpu"),
        execution_mode=ResourceMonitorExecutionMode.INLINE,
        run_id="run-15",
        timeline_id="timeline-15",
        process_id=11,
        node_id="node-a",
        local_rank=0,
        global_rank=7,
        device_id="cuda:0",
    )
    catalog = CheckpointCatalog(
        (
            CheckpointRef(
                "resume-1",
                path="resume.ckpt",
                status=CheckpointRefStatus.COMPLETED,
                step=1,
                timestamp=1.0,
            ),
        )
    )
    plan = TrainingPlan(
        train_batches=(Batch(),),
        output_spec=TrainingOutputSpec(
            objective="objectives/custom.training.total",
            metrics=("metrics/custom.training.mae",),
        ),
        resource_monitors=(monitor,),
        profile_writers=(writer,),
        training_probes=(FakeLightningProbe(),),
        checkpoint_catalog=catalog,
        checkpoint_restore_policy=CheckpointRestorePolicy(),
        checkpoint_restore_selection=CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED),
        checkpoint_save_policy=CheckpointSavePolicy(
            by_step=1,
            on_metric=True,
            metric_name="val_loss",
            metric_direction=CheckpointMetricDirection.MIN,
            on_failure=True,
            on_final=True,
        ),
        checkpoint_prune_policy=CheckpointPrunePolicy(
            keep_recent=2,
            keep_best=1,
            best_metric_name="val_loss",
            best_metric_direction=CheckpointMetricDirection.MIN,
        ),
        run_id="run-15",
        timeline_id="timeline-15",
        process_id=11,
        node_id="node-a",
        local_rank=0,
        global_rank=7,
        device_id="cuda:0",
    )

    result = Trainer(engine=LightningTrainingEngine()).fit(plan, RecordingLearner())

    trainer = FakeTrainer.instances[-1]
    profile = result.training_profile
    assert result.status is TrainingStatus.COMPLETED
    assert trainer.calls[0][2]["ckpt_path"] == "resume.ckpt"
    assert any(isinstance(callback, LightningBridgeCallback) for callback in trainer.callbacks)
    assert any(isinstance(callback, FakeModelCheckpoint) for callback in trainer.callbacks)
    assert isinstance(trainer.kwargs["profiler"], LightningProfilerBridge)
    assert FakeModelCheckpoint.instances[-1].kwargs["save_top_k"] == 1
    assert FakeModelCheckpoint.instances[-1].kwargs["save_last"] is True
    assert profile is not None

    phases = {event.phase for event in profile.events(timeline_id="timeline-15")}
    assert {
        TrainingEventPhase.SETUP,
        TrainingEventPhase.LOOP_STARTED,
        TrainingEventPhase.STEP_STARTED,
        TrainingEventPhase.STEP_COMPLETED,
        TrainingEventPhase.CHECKPOINT,
        TrainingEventPhase.LOOP_COMPLETED,
        TrainingEventPhase.TEARDOWN,
    }.issubset(phases)
    ranked_events = [
        event
        for event in profile.events(timeline_id="timeline-15")
        if event.phase is TrainingEventPhase.STEP_STARTED
    ]
    assert ranked_events[0].global_rank == 7
    assert ranked_events[0].device_id == "cuda:0"
    assert profile.resource_samples()
    assert profile.monitor_lifecycle_records
    assert profile.writer_results
    assert writer_backend.written_records
    assert profile.probe_results_for(probe_id="fake-lightning-probe")
    checkpoint_result_types = {type(result).__name__ for result in profile.checkpoint_results}
    assert {
        "CheckpointSelectionResult",
        "CheckpointRestoreResult",
        "CheckpointSaveResult",
        "CheckpointPruneResult",
    }.issubset(checkpoint_result_types)
    assert "checkpoint.recency_pruner:2" in profile.decisions
    assert any(span.name == "lightning.profiler.train_batch" for span in profile.scalar_spans)


def test_lightning_entrypoint_rejects_datamodule_and_dataloader_mix() -> None:
    with pytest.raises(RemotePhysTrainingError) as error:
        fit_lightning_module(object(), train_dataloaders=("batch",), datamodule=object())
    assert error.value.context["field"] == "datamodule"


def _install_fake_lightning(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeTrainer.instances.clear()
    FakeModelCheckpoint.instances.clear()
    fake_parent = ModuleType("lightning")
    fake_module = ModuleType("lightning.pytorch")
    fake_callbacks = ModuleType("lightning.pytorch.callbacks")
    fake_module.Trainer = FakeTrainer
    fake_module.LightningModule = FakeLightningModule
    fake_callbacks.ModelCheckpoint = FakeModelCheckpoint
    fake_module.callbacks = fake_callbacks
    fake_parent.pytorch = fake_module

    monkeypatch.setitem(sys.modules, "lightning", fake_parent)
    monkeypatch.setitem(sys.modules, "lightning.pytorch", fake_module)
    monkeypatch.setitem(sys.modules, "lightning.pytorch.callbacks", fake_callbacks)

    def safe_version(name: str) -> str:
        if name == "lightning":
            return "2.6.1"
        raise lightning_adapter.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(lightning_adapter.metadata, "version", safe_version)
