"""Dependency-light native training engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import Learner, LoopContext, LoopMode
from rphys.metrics import MetricValue

from .checkpoint import (
    CheckpointCatalog,
    CheckpointPruneResult,
    CheckpointRef,
    CheckpointRestoreMode,
    CheckpointRestoreResult,
    CheckpointResultStatus,
    CheckpointSaveResult,
    CheckpointSelection,
)
from .events import TrainingEvent, TrainingEventPhase, emit_training_event
from ._validation import PrimitiveValue
from .plan import TrainingPlan
from .profiling import ProfileSpanSummary, TrainingProfile, TrainingProfileRecorder
from .probes import ProbeFailurePolicy, ProbeHookPoint, ProbeSelector, ProbeSelectorMode, UnavailableProbeEvidence
from .results import (
    TrainingMetricSummary,
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
        run = _NativeRun(plan, LoopMode.TRAIN)
        try:
            run.setup()
            run.emit(LoopMode.TRAIN, TrainingEventPhase.LOOP_STARTED, split="train")
            run.run_checkpoint_restore()
            for epoch_index in range(plan.max_epochs):
                run.invoke_probes("epoch_started", LoopMode.TRAIN, split="train", epoch_index=epoch_index)
                stopped = self._run_epoch(
                    plan,
                    learner,
                    LoopMode.TRAIN,
                    train_batches,
                    state,
                    run,
                    epoch_index=epoch_index,
                    split="train",
                )
                run.invoke_probes("epoch_completed", LoopMode.TRAIN, split="train", epoch_index=epoch_index)
                run.flush_writers("epoch")
                run.save_checkpoint_if_needed("epoch", LoopMode.TRAIN, state=state, epoch_index=epoch_index)
                if stopped:
                    break
                validation_batches = plan.batches_for(LoopMode.VALIDATE)
                if validation_batches is not None:
                    run.record_span("native.validation", mode=LoopMode.VALIDATE, stage_name="validation")
                    validation_state = _LoopState(LoopMode.VALIDATE)
                    self._run_epoch(
                        plan,
                        learner,
                        LoopMode.VALIDATE,
                        validation_batches,
                        validation_state,
                        run,
                        epoch_index=epoch_index,
                        split="validate",
                    )
                    state.validation_step_count += validation_state.step_count
        except Exception as exc:  # noqa: BLE001 - result normalization boundary
            run.record_failure(LoopMode.TRAIN, exc)
            run.save_checkpoint_if_needed("failure", LoopMode.TRAIN, state=state, failure=exc)
            run.teardown(failed=True)
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(exc).__name__}: {exc}",
                metadata={"validation_step_count": state.validation_step_count},
                training_profile=run.profile,
                checkpoint_id=run.last_checkpoint_id,
            )
        run.save_checkpoint_if_needed("final", LoopMode.TRAIN, state=state)
        run.emit(LoopMode.TRAIN, TrainingEventPhase.LOOP_COMPLETED, status="completed", split="train")
        teardown_error = run.teardown(failed=False)
        if teardown_error is not None:
            _record_teardown_failure(run, LoopMode.TRAIN, state, teardown_error)
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(teardown_error).__name__}: {teardown_error}",
                metadata={"validation_step_count": state.validation_step_count},
                training_profile=run.profile,
                checkpoint_id=run.last_checkpoint_id,
            )
        return state.result(
            status=TrainingStatus.COMPLETED,
            metadata={"validation_step_count": state.validation_step_count},
            training_profile=run.profile,
            checkpoint_id=run.last_checkpoint_id,
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
        run = _NativeRun(plan, mode)
        try:
            run.setup()
            run.emit(mode, TrainingEventPhase.LOOP_STARTED, split=mode.value)
            run.run_checkpoint_restore()
            self._run_epoch(
                plan,
                learner,
                mode,
                batches,
                state,
                run,
                epoch_index=None,
                split=mode.value,
            )
        except Exception as exc:  # noqa: BLE001 - result normalization boundary
            run.record_failure(mode, exc)
            run.save_checkpoint_if_needed("failure", mode, state=state, failure=exc)
            run.teardown(failed=True)
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(exc).__name__}: {exc}",
                training_profile=run.profile,
                checkpoint_id=run.last_checkpoint_id,
            )
        run.save_checkpoint_if_needed("final", mode, state=state)
        run.emit(mode, TrainingEventPhase.LOOP_COMPLETED, status="completed", split=mode.value)
        teardown_error = run.teardown(failed=False)
        if teardown_error is not None:
            _record_teardown_failure(run, mode, state, teardown_error)
            return state.result(
                status=TrainingStatus.FAILED,
                failure=f"{type(teardown_error).__name__}: {teardown_error}",
                training_profile=run.profile,
                checkpoint_id=run.last_checkpoint_id,
            )
        return state.result(status=TrainingStatus.COMPLETED, training_profile=run.profile, checkpoint_id=run.last_checkpoint_id)

    def _run_epoch(
        self,
        plan: TrainingPlan,
        learner: Learner,
        mode: LoopMode,
        batches: Iterable[Batch],
        state: "_LoopState",
        run: "_NativeRun",
        *,
        epoch_index: int | None,
        split: str,
    ) -> bool:
        max_steps = plan.max_steps_for(mode)
        for batch_index, batch in enumerate(batches):
            if max_steps is not None and state.step_count >= max_steps:
                return True
            run.record_span("native.data_wait", mode=mode, stage_name="data_wait", epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            run.invoke_probes("data_wait", mode, split=split, epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, batch=batch)
            run.emit(mode, TrainingEventPhase.DATA_WAIT, epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            run.record_span("native.device_transfer", mode=mode, stage_name="device_transfer", epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            run.invoke_probes("pre_device_transfer", mode, split=split, epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, batch=batch)
            working_batch = _move_batch(plan, batch)
            run.invoke_probes("post_device_transfer", mode, split=split, epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, batch=working_batch)
            run.emit(mode, TrainingEventPhase.DEVICE_TRANSFER, epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            context = LoopContext(
                mode,
                split=split,
                epoch_index=epoch_index,
                step_index=state.step_count,
                batch_index=batch_index,
                metadata=plan.metadata,
                provenance=plan.provenance,
            )
            run.emit_step(context, TrainingEventPhase.STEP_STARTED)
            run.invoke_probes("step_started", mode, context=context, batch=working_batch)
            run.collect_monitors()
            run.record_span("native.forward", mode=mode, stage_name="forward", epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            run.invoke_probes("forward", mode, context=context, batch=working_batch)
            output = learner.step(working_batch, context)
            if not isinstance(output, Batch):
                raise RemotePhysTrainingError(
                    "Learner.step must return a Batch.",
                    owner="NativeTrainingEngine",
                    field="learner",
                    expected="Batch",
                    actual=type(output).__name__,
                )
            run.record_span("native.learner_output_validation", mode=mode, stage_name="learner_output_validation", epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            run.invoke_probes("objective", mode, context=context, batch=working_batch, output=output)
            plan.output_spec.validate_batch(output, mode)
            run.record_span("native.train_step", mode=mode, stage_name="train_step", epoch_index=epoch_index, step_index=state.step_count, batch_index=batch_index, split=split)
            _train_step(plan, mode, output, run=run)
            state.record(output, context, plan)
            run.invoke_probes("step_completed", mode, context=context, batch=working_batch, output=output)
            run.emit_step(context, TrainingEventPhase.STEP_COMPLETED, status="completed")
            run.collect_monitors()
            run.flush_writers("step")
            run.save_checkpoint_if_needed("step", mode, state=state, context=context)
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

    def result(
        self,
        *,
        status: TrainingStatus,
        failure: str | None = None,
        training_profile: TrainingProfile | None = None,
        checkpoint_id: str | None = None,
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
            profiles=None,
            training_profile=training_profile,
            checkpoint_id=checkpoint_id,
            metadata=metadata,
            provenance={"engine": "NativeTrainingEngine"},
        )


class _NativeRun:
    def __init__(self, plan: TrainingPlan, mode: LoopMode) -> None:
        self.plan = plan
        self.mode = mode
        self.run_id = plan.run_id or f"native-{mode.value}"
        self.timeline_id = plan.timeline_id or f"native-{mode.value}-timeline"
        self.recorder = TrainingProfileRecorder()
        self.monitor_offsets = {id(monitor): 0 for monitor in plan.resource_monitors}
        self.checkpoint_refs = list(plan.checkpoint_catalog.refs)
        self.last_checkpoint_id: str | None = None
        self.setup_started = False

    @property
    def profile(self) -> TrainingProfile:
        return self.recorder.snapshot()

    def setup(self) -> None:
        self.setup_started = True
        self.record_span("native.setup", mode=self.mode, stage_name="setup")
        self.emit(self.mode, TrainingEventPhase.SETUP, status="started", split=self.mode.value)
        for monitor in self.plan.resource_monitors:
            monitor.start()
            self._record_monitor_lifecycle(monitor)
        self.invoke_probes("setup", self.mode, split=self.mode.value)
        self.collect_monitors()
        self.emit(self.mode, TrainingEventPhase.SETUP, status="completed", split=self.mode.value)

    def teardown(self, *, failed: bool) -> Exception | None:
        status = "failed" if failed else "completed"
        try:
            self.record_span("native.teardown", mode=self.mode, stage_name="teardown", status=status)
            self.emit(
                self.mode,
                TrainingEventPhase.TEARDOWN,
                status="started",
                split=self.mode.value,
                fanout=not failed,
            )
            self.invoke_probes("teardown", self.mode, split=self.mode.value)
            for monitor in self.plan.resource_monitors:
                monitor.request_flush()
                self._record_monitor_lifecycle(monitor)
                monitor.stop()
                self._record_monitor_lifecycle(monitor)
                if failed:
                    monitor.cleanup_orphan()
                    self._record_monitor_lifecycle(monitor)
            self.flush_writers("run")
            self.emit(
                self.mode,
                TrainingEventPhase.PROFILING_SUMMARY,
                status=status,
                split=self.mode.value,
                metadata={"writer_results": len(self.recorder.snapshot().writer_results)},
                fanout=not failed,
            )
            self.emit(
                self.mode,
                TrainingEventPhase.TEARDOWN,
                status=status,
                split=self.mode.value,
                fanout=not failed,
            )
        except Exception as exc:  # noqa: BLE001 - teardown must not erase prior evidence
            self.recorder.record_decision(f"native_teardown_failed:{type(exc).__name__}")
            return exc
        return None

    def emit(
        self,
        mode: LoopMode,
        phase: TrainingEventPhase,
        *,
        status: str = "observed",
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        metadata: Mapping[str, PrimitiveValue] | None = None,
        fanout: bool = True,
    ) -> None:
        event = TrainingEvent(
            phase,
            mode,
            status=status,
            epoch_index=epoch_index,
            step_index=step_index,
            batch_index=batch_index,
            split=split,
            run_id=self.run_id,
            timeline_id=self.timeline_id,
            process_id=self.plan.process_id,
            node_id=self.plan.node_id,
            local_rank=self.plan.local_rank,
            global_rank=self.plan.global_rank,
            device_id=self.plan.device_id,
            metadata=metadata,
            provenance={"engine": "NativeTrainingEngine"},
        )
        self.recorder.record_event(event)
        self.writer_append({"record": "event", "phase": phase.value, "status": status})
        if fanout:
            emit_training_event(event, sinks=self.plan.event_sinks, callbacks=self.plan.callbacks)

    def emit_step(
        self,
        context: LoopContext,
        phase: TrainingEventPhase,
        *,
        status: str = "observed",
    ) -> None:
        self.emit(
            context.mode,
            phase,
            status=status,
            epoch_index=context.epoch_index,
            step_index=context.step_index,
            batch_index=context.batch_index,
            split=context.split,
        )

    def record_span(
        self,
        name: str,
        *,
        mode: LoopMode,
        stage_name: str,
        status: str = "available",
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        split: str | None = None,
        metadata: Mapping[str, PrimitiveValue] | None = None,
    ) -> None:
        span_metadata: dict[str, PrimitiveValue] = {"engine": "NativeTrainingEngine"}
        if epoch_index is not None:
            span_metadata["epoch_index"] = epoch_index
        if step_index is not None:
            span_metadata["step_index"] = step_index
        if batch_index is not None:
            span_metadata["batch_index"] = batch_index
        if split is not None:
            span_metadata["split"] = split
        if metadata is not None:
            span_metadata.update(metadata)
        self.recorder.record_scalar_span(
            ProfileSpanSummary(
                name,
                mode=mode,
                status=status,
                stage_name=stage_name,
                duration_seconds=0.0,
                run_id=self.run_id,
                timeline_id=self.timeline_id,
                process_id=self.plan.process_id,
                node_id=self.plan.node_id,
                local_rank=self.plan.local_rank,
                global_rank=self.plan.global_rank,
                device_id=self.plan.device_id,
                metadata=span_metadata,
                provenance={"engine": "NativeTrainingEngine"},
            )
        )
        self.writer_append({"record": "span", "name": name, "status": status})

    def collect_monitors(self) -> None:
        for monitor in self.plan.resource_monitors:
            sample = monitor.collect_sample()
            if sample is not None:
                self.recorder.record_resource_sample(sample)
            self._record_monitor_lifecycle(monitor)

    def _record_monitor_lifecycle(self, monitor: object) -> None:
        events = getattr(monitor, "lifecycle_events", ())
        offset = self.monitor_offsets.get(id(monitor), 0)
        for record in events[offset:]:
            self.recorder.record_monitor_lifecycle_record(record)
        self.monitor_offsets[id(monitor)] = len(events)

    def writer_append(self, record: object) -> None:
        for writer in self.plan.profile_writers:
            self.recorder.record_writer_result(writer.append(record))

    def flush_writers(self, scope: str) -> None:
        for writer in self.plan.profile_writers:
            if scope == "step":
                result = writer.flush_step()
            elif scope == "epoch":
                result = writer.flush_epoch()
            else:
                result = writer.flush_run()
            self.recorder.record_writer_result(result)

    def invoke_probes(
        self,
        hook_point: str,
        mode: LoopMode,
        *,
        context: LoopContext | None = None,
        split: str | None = None,
        epoch_index: int | None = None,
        step_index: int | None = None,
        batch_index: int | None = None,
        batch: Batch | None = None,
        output: Batch | None = None,
    ) -> None:
        if context is not None:
            split = context.split
            epoch_index = context.epoch_index
            step_index = context.step_index
            batch_index = context.batch_index
        probe_context: dict[object, object] = {
            "hook_point": hook_point,
            "mode": mode.value,
            "run_id": self.run_id,
            "timeline_id": self.timeline_id,
            "split": split,
            "epoch_index": epoch_index,
            "step_index": step_index,
            "batch_index": batch_index,
            "process_id": self.plan.process_id,
            "node_id": self.plan.node_id,
            "local_rank": self.plan.local_rank,
            "global_rank": self.plan.global_rank,
            "device_id": self.plan.device_id,
        }
        if batch is not None:
            probe_context["batch"] = batch
        if output is not None:
            probe_context["output"] = output
        for probe in self.plan.training_probes:
            try:
                results = tuple(probe.collect(probe_context))
            except Exception as exc:  # noqa: BLE001 - probe policy is represented by returned records
                self.recorder.record_decision(f"native_probe_failed:{type(exc).__name__}")
                policy = _probe_failure_policy(probe)
                if policy is ProbeFailurePolicy.FAIL:
                    raise
                self.recorder.record_probe_result(
                    UnavailableProbeEvidence(
                        _probe_id(probe),
                        reason="probe_failed",
                        hook_point=ProbeHookPoint.coerce(hook_point),
                        selector=_probe_selector(probe),
                        failure_policy=policy,
                        run_id=self.run_id,
                        timeline_id=self.timeline_id,
                        local_rank=self.plan.local_rank,
                        global_rank=self.plan.global_rank,
                        process_id=self.plan.process_id,
                        node_id=self.plan.node_id,
                        device_id=self.plan.device_id,
                        metadata={
                            "failure_type": type(exc).__name__,
                            "failure_message": str(exc),
                            "split": split,
                            "epoch_index": epoch_index,
                            "step_index": step_index,
                            "batch_index": batch_index,
                        },
                        provenance={"engine": "NativeTrainingEngine"},
                    )
                )
                continue
            for result in results:
                self.recorder.record_probe_result(result)

    def run_checkpoint_restore(self) -> None:
        selector = self.plan.checkpoint_restore_selection
        if selector is None and self.plan.checkpoint_restore_policy is not None:
            selector = CheckpointSelection(
                self.plan.checkpoint_restore_policy.selector,
                stream_id=self.plan.checkpoint_restore_policy.preferred_stream_id,
            )
        if selector is None:
            return
        selection_result = CheckpointCatalog(self.checkpoint_refs).select(selector)
        self.recorder.record_checkpoint_result(selection_result)
        restore_policy = self.plan.checkpoint_restore_policy
        restore_mode = CheckpointRestoreMode.CATALOG if restore_policy is None else restore_policy.mode
        if selection_result.ref is None:
            self.recorder.record_checkpoint_result(
                CheckpointRestoreResult(
                    status=CheckpointResultStatus.UNAVAILABLE,
                    mode=restore_mode,
                    reason="checkpoint_selection_unavailable",
                    run_id=self.run_id,
                    timeline_id=self.timeline_id,
                    metadata={"selector": selector.mode.value},
                    provenance={"engine": "NativeTrainingEngine"},
                )
            )
            return
        if self.plan.checkpoint_restore_hook is None:
            self.recorder.record_checkpoint_result(
                CheckpointRestoreResult(
                    status=CheckpointResultStatus.UNSUPPORTED,
                    mode=restore_mode,
                    ref_id=selection_result.ref.ref_id,
                    reason="checkpoint_restore_hook_not_configured",
                    run_id=self.run_id,
                    timeline_id=self.timeline_id,
                    provenance={"engine": "NativeTrainingEngine"},
                )
            )
            return
        self.record_span("native.checkpoint_restore", mode=self.mode, stage_name="checkpoint")
        result = self.plan.checkpoint_restore_hook(selection_result)
        if not isinstance(result, CheckpointRestoreResult):
            raise RemotePhysTrainingError(
                "TrainingPlan checkpoint_restore_hook must return CheckpointRestoreResult.",
                owner="NativeTrainingEngine",
                field="checkpoint_restore_hook",
                expected="CheckpointRestoreResult",
                actual=type(result).__name__,
            )
        self.recorder.record_checkpoint_result(result)

    def save_checkpoint_if_needed(
        self,
        boundary: str,
        mode: LoopMode,
        *,
        state: _LoopState,
        context: LoopContext | None = None,
        epoch_index: int | None = None,
        failure: Exception | None = None,
    ) -> None:
        policy = self.plan.checkpoint_save_policy
        if policy is None or not policy.enabled:
            return
        reason = self._checkpoint_save_reason(policy=policy, boundary=boundary, state=state, context=context, epoch_index=epoch_index, failure=failure)
        if reason is None:
            self.record_metric_checkpoint_skip(
                policy=policy,
                boundary=boundary,
                mode=mode,
                state=state,
                context=context,
                epoch_index=epoch_index,
            )
            return
        metadata = self._checkpoint_save_metadata(policy=policy, reason=reason, boundary=boundary, state=state)
        self.emit(
            mode,
            TrainingEventPhase.CHECKPOINT,
            status="attempted",
            epoch_index=epoch_index if context is None else context.epoch_index,
            step_index=None if context is None else context.step_index,
            batch_index=None if context is None else context.batch_index,
            split=mode.value if context is None else context.split,
            metadata=metadata,
        )
        self.record_span("native.checkpoint_save", mode=mode, stage_name="checkpoint", metadata=metadata)
        if self.plan.checkpoint_save_hook is None:
            result = CheckpointSaveResult(
                status=CheckpointResultStatus.UNSUPPORTED,
                reason="checkpoint_save_hook_not_configured",
                run_id=self.run_id,
                timeline_id=self.timeline_id,
                metadata=metadata,
                provenance={"engine": "NativeTrainingEngine"},
            )
            self.recorder.record_checkpoint_result(result)
            return
        hook_result = self.plan.checkpoint_save_hook(
            {
                "reason": reason,
                "mode": mode.value,
                "run_id": self.run_id,
                "timeline_id": self.timeline_id,
                "epoch_index": epoch_index if context is None else context.epoch_index,
                "step_index": None if context is None else context.step_index,
                "metrics": {name: summary.value for name, summary in state.metrics.items()},
                "metric_name": metadata.get("metric_name"),
                "metric_direction": metadata.get("metric_direction"),
                "metric_value": metadata.get("metric_value"),
                "metric_threshold": metadata.get("metric_threshold"),
                "failure_type": None if failure is None else type(failure).__name__,
            }
        )
        if isinstance(hook_result, CheckpointRef):
            self.checkpoint_refs.append(hook_result)
            self.last_checkpoint_id = hook_result.ref_id
            save_result = CheckpointSaveResult(
                status=CheckpointResultStatus.COMPLETED,
                ref_id=hook_result.ref_id,
                run_id=self.run_id,
                timeline_id=self.timeline_id,
                metadata=metadata,
                provenance={"engine": "NativeTrainingEngine"},
            )
            self.recorder.record_checkpoint_result(save_result)
        elif isinstance(hook_result, CheckpointSaveResult):
            if hook_result.ref_id is not None:
                self.last_checkpoint_id = hook_result.ref_id
            self.recorder.record_checkpoint_result(hook_result)
        else:
            raise RemotePhysTrainingError(
                "TrainingPlan checkpoint_save_hook returned an unsupported result.",
                owner="NativeTrainingEngine",
                field="checkpoint_save_hook",
                expected="CheckpointSaveResult | CheckpointRef",
                actual=type(hook_result).__name__,
            )
        self.prune_checkpoints()

    def _checkpoint_save_reason(
        self,
        *,
        policy: object,
        boundary: str,
        state: _LoopState,
        context: LoopContext | None,
        epoch_index: int | None,
        failure: Exception | None,
    ) -> str | None:
        del failure
        if boundary == "failure" and policy.on_failure:
            return "failure"
        if boundary == "final" and policy.on_final:
            return "final"
        if boundary == "epoch" and policy.by_epoch is not None and epoch_index is not None:
            if (epoch_index + 1) % policy.by_epoch == 0:
                return "epoch"
        if boundary == "step" and policy.by_step is not None and context is not None:
            if (context.step_index + 1) % policy.by_step == 0:
                return "step"
        if policy.on_metric and policy.metric_name is not None:
            summary = state.metrics.get(policy.metric_name)
            if summary is None or not _is_numeric_metric(summary.value):
                return None
            if policy.metric_threshold is None:
                return "metric"
            if policy.metric_direction is not None and policy.metric_direction.value == "min":
                return "metric" if summary.value <= policy.metric_threshold else None
            return "metric" if summary.value >= policy.metric_threshold else None
        return None

    def _checkpoint_save_metadata(
        self,
        *,
        policy: object,
        reason: str,
        boundary: str,
        state: _LoopState,
    ) -> dict[str, PrimitiveValue]:
        metadata: dict[str, PrimitiveValue] = {"reason": reason, "boundary": boundary}
        if not policy.on_metric or policy.metric_name is None:
            return metadata
        metadata["metric_name"] = policy.metric_name
        if policy.metric_direction is not None:
            metadata["metric_direction"] = policy.metric_direction.value
        if policy.metric_threshold is not None:
            metadata["metric_threshold"] = policy.metric_threshold
        summary = state.metrics.get(policy.metric_name)
        if summary is not None:
            metadata["metric_value"] = summary.value
        return metadata

    def record_metric_checkpoint_skip(
        self,
        *,
        policy: object,
        boundary: str,
        mode: LoopMode,
        state: _LoopState,
        context: LoopContext | None,
        epoch_index: int | None,
    ) -> None:
        if not policy.on_metric or policy.metric_name is None:
            return
        metadata = self._checkpoint_save_metadata(
            policy=policy,
            reason="metric_checkpoint_skipped",
            boundary=boundary,
            state=state,
        )
        summary = state.metrics.get(policy.metric_name)
        if summary is None:
            status = CheckpointResultStatus.UNAVAILABLE
            reason = "metric_unavailable"
            metadata["metric_available"] = False
        elif not _is_numeric_metric(summary.value):
            status = CheckpointResultStatus.UNAVAILABLE
            reason = "metric_not_numeric"
            metadata["metric_available"] = True
        else:
            status = CheckpointResultStatus.SKIPPED
            reason = "metric_threshold_not_met"
            metadata["metric_available"] = True
        metadata["reason"] = reason
        self.emit(
            mode,
            TrainingEventPhase.CHECKPOINT,
            status=status.value,
            epoch_index=epoch_index if context is None else context.epoch_index,
            step_index=None if context is None else context.step_index,
            batch_index=None if context is None else context.batch_index,
            split=mode.value if context is None else context.split,
            metadata=metadata,
        )
        self.recorder.record_checkpoint_result(
            CheckpointSaveResult(
                status=status,
                reason=reason,
                run_id=self.run_id,
                timeline_id=self.timeline_id,
                metadata=metadata,
                provenance={"engine": "NativeTrainingEngine"},
            )
        )

    def prune_checkpoints(self) -> None:
        policy = self.plan.checkpoint_prune_policy
        if policy is None or not policy.enabled:
            return
        self.record_span("native.checkpoint_prune", mode=self.mode, stage_name="checkpoint")
        if self.plan.checkpoint_prune_hook is None:
            self.recorder.record_checkpoint_result(
                CheckpointPruneResult(
                    status=CheckpointResultStatus.UNSUPPORTED,
                    run_id=self.run_id,
                    timeline_id=self.timeline_id,
                    metadata={"reason": "checkpoint_prune_hook_not_configured"},
                    provenance={"engine": "NativeTrainingEngine"},
                )
            )
            return
        result = self.plan.checkpoint_prune_hook(CheckpointCatalog(self.checkpoint_refs))
        if not isinstance(result, CheckpointPruneResult):
            raise RemotePhysTrainingError(
                "TrainingPlan checkpoint_prune_hook must return CheckpointPruneResult.",
                owner="NativeTrainingEngine",
                field="checkpoint_prune_hook",
                expected="CheckpointPruneResult",
                actual=type(result).__name__,
            )
        self.recorder.record_checkpoint_result(result)
        if result.kept:
            self.checkpoint_refs = list(result.kept)

    def record_failure(self, mode: LoopMode, exc: Exception) -> None:
        self.record_span(
            "native.failure",
            mode=mode,
            stage_name="failure",
            status="failed",
            metadata={"failure_type": type(exc).__name__},
        )
        self.emit(
            mode,
            TrainingEventPhase.LOOP_FAILED,
            status="failed",
            split=mode.value,
            metadata={"failure_type": type(exc).__name__},
            fanout=False,
        )
        try:
            self.invoke_probes("failure", mode, split=mode.value)
        except Exception:
            pass


def _probe_failure_policy(probe: object) -> ProbeFailurePolicy:
    policy = getattr(probe, "failure_policy", ProbeFailurePolicy.FAIL)
    return ProbeFailurePolicy.coerce(policy)


def _probe_id(probe: object) -> str:
    probe_id = getattr(probe, "probe_id", None)
    if isinstance(probe_id, str) and probe_id:
        return probe_id
    return type(probe).__name__


def _probe_selector(probe: object) -> ProbeSelector:
    selector = getattr(probe, "selector", None)
    if isinstance(selector, ProbeSelector):
        return selector
    return ProbeSelector(ProbeSelectorMode.ALL)


def _is_numeric_metric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _record_teardown_failure(
    run: _NativeRun,
    mode: LoopMode,
    state: _LoopState,
    error: Exception,
) -> None:
    try:
        run.record_failure(mode, error)
        run.save_checkpoint_if_needed("failure", mode, state=state, failure=error)
    except Exception as exc:  # noqa: BLE001 - preserve the original teardown failure result
        run.recorder.record_decision(f"native_teardown_failure_recording_failed:{type(exc).__name__}")


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


def _train_step(plan: TrainingPlan, mode: LoopMode, output: Batch, *, run: "_NativeRun") -> None:
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
    run.invoke_probes("backward", mode, output=output)
    run.record_span("native.backward", mode=mode, stage_name="backward")
    _zero_grad(plan, mode)
    _backward(plan, objective)
    run.invoke_probes("optimizer_step", mode, output=output)
    run.record_span("native.optimizer_step", mode=mode, stage_name="optimizer_step")
    _optimizer_step(plan)
    run.invoke_probes("scheduler_step", mode, output=output)
    run.record_span("native.scheduler_step", mode=mode, stage_name="scheduler_step")
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
