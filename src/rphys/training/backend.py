"""Dependency-light native training engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import Learner, LoopContext, LoopMode
from rphys.metrics import MetricValue

from .events import TrainingEvent, TrainingEventPhase, emit_training_event
from ._validation import PrimitiveValue
from .plan import TrainingPlan
from .results import (
    TrainingMetricSummary,
    ProfileSummary,
    TrainingResult,
    TrainingStatus,
    TrainingStepSummary,
)

__all__ = ["NativeTrainingEngine"]


class NativeTrainingEngine:
    """Reference-grade loop over caller-provided ``Batch`` iterables.

    The native engine owns loop mechanics only: context construction, optional
    device movement, objective backward, optimizer/scheduler stepping, and
    primitive result accumulation. It does not build dataloaders, scan
    datasources, export predictions, write checkpoints, configure loggers, or
    implement distributed/precision framework features.
    """

    __slots__ = ()

    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run train-mode steps and optional validation after each epoch."""

        return self._run_fit(plan, learner)

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run validate-mode steps without backward or optimizer mechanics."""

        return self._run_mode(plan, learner, LoopMode.VALIDATE)

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run test-mode steps without backward or optimizer mechanics."""

        return self._run_mode(plan, learner, LoopMode.TEST)

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run predict-mode steps without prediction materialization."""

        return self._run_mode(plan, learner, LoopMode.PREDICT)

    def _run_fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        _require_plan(plan)
        _require_learner(learner)
        train_batches = plan.batches_for(LoopMode.TRAIN)
        if train_batches is None:
            return _stopped_result(LoopMode.TRAIN, "No train_batches configured.")

        state = _LoopState(LoopMode.TRAIN)
        try:
            _emit_loop_event(plan, LoopMode.TRAIN, TrainingEventPhase.LOOP_STARTED)
            for epoch_index in range(plan.max_epochs):
                stopped = self._run_epoch(
                    plan,
                    learner,
                    LoopMode.TRAIN,
                    train_batches,
                    state,
                    epoch_index=epoch_index,
                    split="train",
                )
                if stopped:
                    break
                validation_batches = plan.batches_for(LoopMode.VALIDATE)
                if validation_batches is not None:
                    validation_state = _LoopState(LoopMode.VALIDATE)
                    self._run_epoch(
                        plan,
                        learner,
                        LoopMode.VALIDATE,
                        validation_batches,
                        validation_state,
                        epoch_index=epoch_index,
                        split="validate",
                    )
                    state.validation_step_count += validation_state.step_count
        except Exception as exc:  # noqa: BLE001 - result normalization boundary
            _emit_loop_event(
                plan,
                LoopMode.TRAIN,
                TrainingEventPhase.LOOP_FAILED,
                status="failed",
                metadata={"failure_type": type(exc).__name__},
            )
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(exc).__name__}: {exc}",
                metadata={"validation_step_count": state.validation_step_count},
            )
        _emit_loop_event(plan, LoopMode.TRAIN, TrainingEventPhase.LOOP_COMPLETED, status="completed")
        return state.result(
            status=TrainingStatus.COMPLETED,
            metadata={"validation_step_count": state.validation_step_count},
        )

    def _run_mode(
        self,
        plan: TrainingPlan,
        learner: Learner,
        mode: LoopMode,
    ) -> TrainingResult:
        _require_plan(plan)
        _require_learner(learner)
        batches = plan.batches_for(mode)
        if batches is None:
            return _stopped_result(mode, f"No {mode.value}_batches configured.")

        state = _LoopState(mode)
        try:
            _emit_loop_event(plan, mode, TrainingEventPhase.LOOP_STARTED)
            self._run_epoch(
                plan,
                learner,
                mode,
                batches,
                state,
                epoch_index=None,
                split=mode.value,
            )
        except Exception as exc:  # noqa: BLE001 - result normalization boundary
            _emit_loop_event(
                plan,
                mode,
                TrainingEventPhase.LOOP_FAILED,
                status="failed",
                metadata={"failure_type": type(exc).__name__},
            )
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(exc).__name__}: {exc}",
            )
        _emit_loop_event(plan, mode, TrainingEventPhase.LOOP_COMPLETED, status="completed")
        return state.result(status=TrainingStatus.COMPLETED)

    def _run_epoch(
        self,
        plan: TrainingPlan,
        learner: Learner,
        mode: LoopMode,
        batches: Iterable[Batch],
        state: "_LoopState",
        *,
        epoch_index: int | None,
        split: str,
    ) -> bool:
        max_steps = plan.max_steps_for(mode)
        for batch_index, batch in enumerate(batches):
            if max_steps is not None and state.step_count >= max_steps:
                return True
            working_batch = _move_batch(plan, batch)
            context = LoopContext(
                mode,
                split=split,
                epoch_index=epoch_index,
                step_index=state.step_count,
                batch_index=batch_index,
                metadata=plan.metadata,
                provenance=plan.provenance,
            )
            _emit_step_event(plan, context, TrainingEventPhase.STEP_STARTED)
            output = learner.step(working_batch, context)
            if not isinstance(output, Batch):
                raise RemotePhysTrainingError(
                    "Learner.step must return a Batch.",
                    owner="NativeTrainingEngine",
                    field="learner",
                    expected="Batch",
                    actual=type(output).__name__,
                )
            plan.output_spec.validate_batch(output, mode)
            _train_step(plan, mode, output)
            state.record(output, context, plan)
            _emit_step_event(plan, context, TrainingEventPhase.STEP_COMPLETED, status="completed")
        return False


class _LoopState:
    def __init__(self, mode: LoopMode) -> None:
        self.mode = mode
        self.step_count = 0
        self.batch_count = 0
        self.epoch_count = 0
        self.validation_step_count = 0
        self.last_step: TrainingStepSummary | None = None
        self.metrics: dict[str, TrainingMetricSummary] = {}
        self.profiles: list[ProfileSummary] = []

    def record(self, output: Batch, context: LoopContext, plan: TrainingPlan) -> None:
        self.step_count += 1
        self.batch_count += 1
        if context.epoch_index is not None:
            self.epoch_count = max(self.epoch_count, context.epoch_index + 1)
        objective = plan.output_spec.objective_value(output, context.mode)
        metric_values = plan.output_spec.metric_values(output)
        step_metrics = _step_metric_mapping(metric_values)
        self.last_step = TrainingStepSummary(
            context.mode,
            epoch_index=context.epoch_index,
            step_index=context.step_index,
            batch_index=context.batch_index,
            split=context.split,
            objective=_primitive_scalar(objective),
            metrics=step_metrics,
            metadata={"output_field_count": len(output.field_items())},
            provenance={"engine": "NativeTrainingEngine"},
        )
        self.metrics.update(_metric_summaries(metric_values, output, plan))
        self.profiles.append(
            ProfileSummary(
                "native.step",
                status="unavailable",
                metadata={"reason": "native timing profiler not configured"},
            )
        )

    def result(
        self,
        *,
        status: TrainingStatus,
        failure: str | None = None,
        metadata: Mapping[str, PrimitiveValue] | None = None,
    ) -> TrainingResult:
        return TrainingResult(
            status=status,
            mode=self.mode,
            epoch_count=self.epoch_count,
            step_count=self.step_count,
            batch_count=self.batch_count,
            failure=failure,
            metrics=tuple(self.metrics.values()),
            last_step=self.last_step,
            profiles=tuple(self.profiles),
            metadata=metadata,
            provenance={"engine": "NativeTrainingEngine"},
        )


def _require_plan(plan: object) -> None:
    if not isinstance(plan, TrainingPlan):
        raise RemotePhysTrainingError(
            "NativeTrainingEngine requires a TrainingPlan.",
            owner="NativeTrainingEngine",
            field="plan",
            expected="TrainingPlan",
            actual=type(plan).__name__,
        )


def _require_learner(learner: object) -> None:
    step = getattr(learner, "step", None)
    if not callable(step):
        raise RemotePhysTrainingError(
            "NativeTrainingEngine requires a learner with step(batch, context).",
            owner="NativeTrainingEngine",
            field="learner",
            expected="Learner",
            actual=type(learner).__name__,
        )


def _stopped_result(mode: LoopMode, failure: str) -> TrainingResult:
    return TrainingResult(
        status=TrainingStatus.STOPPED,
        mode=mode,
        failure=failure,
        provenance={"engine": "NativeTrainingEngine"},
    )


def _move_batch(plan: TrainingPlan, batch: Batch) -> Batch:
    if not isinstance(batch, Batch):
        raise RemotePhysTrainingError(
            "NativeTrainingEngine batch iterables must yield Batch objects.",
            owner="NativeTrainingEngine",
            field="batch",
            expected="Batch",
            actual=type(batch).__name__,
        )
    if plan.device_mover is None:
        return batch
    moved = plan.device_mover(batch)
    if not isinstance(moved, Batch):
        raise RemotePhysTrainingError(
            "TrainingPlan device_mover must return a Batch.",
            owner="NativeTrainingEngine",
            field="device_mover",
            expected="Batch",
            actual=type(moved).__name__,
        )
    return moved


def _zero_grad(plan: TrainingPlan, mode: LoopMode) -> None:
    if mode is not LoopMode.TRAIN or plan.optimizer is None:
        return
    zero_grad = getattr(plan.optimizer, "zero_grad", None)
    if callable(zero_grad):
        zero_grad()


def _train_step(plan: TrainingPlan, mode: LoopMode, output: Batch) -> None:
    if mode is not LoopMode.TRAIN:
        return
    objective = plan.output_spec.objective_value(output, mode)
    if objective is None:
        raise RemotePhysTrainingError(
            "Train steps require the TrainingOutputSpec objective field for native backward execution.",
            owner="NativeTrainingEngine",
            field="objective",
            expected="BackwardableScalar",
            actual="None",
        )
    _zero_grad(plan, mode)
    _backward(plan, objective)
    _optimizer_step(plan)
    _scheduler_step(plan)


def _backward(plan: TrainingPlan, objective: object) -> None:
    if plan.backward is not None:
        plan.backward(objective)
        return
    backward = getattr(objective, "backward", None)
    if not callable(backward):
        raise RemotePhysTrainingError(
            "Objective does not expose backward() and no TrainingPlan.backward hook was provided.",
            owner="NativeTrainingEngine",
            field="objective",
            expected="callable backward() or TrainingPlan.backward",
            actual=type(objective).__name__,
        )
    backward()


def _optimizer_step(plan: TrainingPlan) -> None:
    if plan.optimizer is None:
        return
    step = getattr(plan.optimizer, "step", None)
    if not callable(step):
        raise RemotePhysTrainingError(
            "TrainingPlan optimizer must expose step() when provided.",
            owner="NativeTrainingEngine",
            field="optimizer",
            expected="object with step()",
            actual=type(plan.optimizer).__name__,
        )
    step()


def _scheduler_step(plan: TrainingPlan) -> None:
    if plan.scheduler is None:
        return
    step = getattr(plan.scheduler, "step", None)
    if not callable(step):
        raise RemotePhysTrainingError(
            "TrainingPlan scheduler must expose step() when provided.",
            owner="NativeTrainingEngine",
            field="scheduler",
            expected="object with step()",
            actual=type(plan.scheduler).__name__,
        )
    step()


def _step_metric_mapping(values: Mapping[str, object]) -> Mapping[str, PrimitiveValue]:
    return {
        name: _primitive_scalar(metric.value if isinstance(metric, MetricValue) else metric)
        for name, metric in values.items()
    }


def _metric_summaries(
    values: Mapping[str, object],
    output: Batch,
    plan: TrainingPlan,
) -> dict[str, TrainingMetricSummary]:
    summaries: dict[str, TrainingMetricSummary] = {}
    for name, metric in values.items():
        locator = name
        field_value = plan.output_spec.field_value(output, locator)
        if isinstance(metric, MetricValue):
            summaries[name] = TrainingMetricSummary(
                name,
                _primitive_scalar(metric.value),
                unit=metric.unit,
                metadata=metric.metadata,
                provenance=metric.provenance,
            )
        else:
            metadata = None
            if field_value is not None and field_value.schema is not None:
                metadata = {"schema": str(field_value.schema)}
            summaries[name] = TrainingMetricSummary(
                name,
                _primitive_scalar(metric),
                metadata=metadata,
            )
    return summaries


def _primitive_scalar(value: object) -> PrimitiveValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    nested = getattr(value, "value", None)
    if nested is not value and (nested is None or isinstance(nested, (str, int, float, bool))):
        return nested
    return str(value)


def _emit_loop_event(
    plan: TrainingPlan,
    mode: LoopMode,
    phase: TrainingEventPhase,
    *,
    status: str = "observed",
    metadata: Mapping[str, PrimitiveValue] | None = None,
) -> None:
    emit_training_event(
        TrainingEvent(
            phase,
            mode,
            status=status,
            split=mode.value,
            metadata=metadata,
            provenance={"engine": "NativeTrainingEngine"},
        ),
        sinks=plan.event_sinks,
        callbacks=plan.callbacks,
    )


def _emit_step_event(
    plan: TrainingPlan,
    context: LoopContext,
    phase: TrainingEventPhase,
    *,
    status: str = "observed",
) -> None:
    emit_training_event(
        TrainingEvent(
            phase,
            context.mode,
            status=status,
            epoch_index=context.epoch_index,
            step_index=context.step_index,
            batch_index=context.batch_index,
            split=context.split,
            provenance={"engine": "NativeTrainingEngine"},
        ),
        sinks=plan.event_sinks,
        callbacks=plan.callbacks,
    )
