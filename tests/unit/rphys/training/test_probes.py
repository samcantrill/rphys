from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    DataFieldProbeSummary,
    DataProbeSummary,
    DataSampleProbeSummary,
    ModelActivationProbeSummary,
    ModelGradientProbeSummary,
    ModelHealthProbeSummary,
    ModelParameterProbeSummary,
    ModelProbeSummary,
    ProbeAggregation,
    ProbeCadence,
    ProbeCadenceMode,
    ProbeFailurePolicy,
    ProbeHookPoint,
    ProbeSelector,
    ProbeSelectorMode,
    ProbeUnavailable,
    TrainingPipelineStage,
    TrainingProbe,
    UnavailableProbeEvidence,
)


class ProbeCollector:
    def collect(self, context: object) -> tuple[DataProbeSummary]:
        del context
        return (DataProbeSummary(
            "probe-id",
            "batch",
            hook_point=ProbeHookPoint.BATCH_FETCH,
            selector=ProbeSelector(ProbeSelectorMode.ALL),
            cadence=ProbeCadence(ProbeCadenceMode.MANUAL),
        ),)


def test_probe_hook_point_and_pipeline_stage_coercion() -> None:
    for value in (
        "setup",
        "step_started",
        "batch_fetch",
        "pipeline_stage",
        "checkpoint",
    ):
        assert ProbeHookPoint.coerce(value) is not None

    for value in (
        "indexed",
        "cache_lookup",
        "pre_augmentation",
        "learner_output_validation",
    ):
        assert TrainingPipelineStage.coerce(value) is not None

    with pytest.raises(RemotePhysTrainingError) as invalid_hook:
        ProbeHookPoint.coerce("nope")
    assert invalid_hook.value.context["field"] == "hook_point"

    with pytest.raises(RemotePhysTrainingError) as invalid_stage:
        TrainingPipelineStage.coerce("nope")
    assert invalid_stage.value.context["field"] == "pipeline_stage"


def test_probe_selector_validation() -> None:
    assert ProbeSelector(ProbeSelectorMode.ALL)
    with pytest.raises(RemotePhysTrainingError) as all_error:
        ProbeSelector(ProbeSelectorMode.ALL, ("unexpected",))
    assert all_error.value.context["field"] == "values"

    with pytest.raises(RemotePhysTrainingError) as required_values:
        ProbeSelector(ProbeSelectorMode.BY_HOOK)
    assert required_values.value.context["field"] == "values"


def test_probe_cadence_validation_rules() -> None:
    every = ProbeCadence(ProbeCadenceMode.EVERY_N_STEPS, interval=10)
    assert every.interval == 10

    disabled = ProbeCadence(ProbeCadenceMode.DISABLED)
    assert disabled.interval is None

    with pytest.raises(RemotePhysTrainingError) as interval_error:
        ProbeCadence(ProbeCadenceMode.EVERY_N_STEPS)
    assert interval_error.value.context["field"] == "interval"

    metric = ProbeCadence(
        ProbeCadenceMode.ON_METRIC,
        metric_name="loss",
        metric_direction="min",
        metric_threshold=0.5,
    )
    assert metric.metric_name == "loss"
    assert metric.metric_threshold == 0.5

    with pytest.raises(RemotePhysTrainingError) as metric_error:
        ProbeCadence(ProbeCadenceMode.ON_METRIC, interval=1.0)
    assert metric_error.value.context["field"] == "interval"


def test_model_probe_summaries_capture_nested_primitive_context() -> None:
    selector = ProbeSelector(ProbeSelectorMode.BY_PROBE, values=("model", "grad"))
    cadence = ProbeCadence(ProbeCadenceMode.MANUAL)
    summary = ModelProbeSummary(
        "model-probe",
        "gradient",
        hook_point=ProbeHookPoint.FORWARD,
        selector=selector,
        cadence=cadence,
        aggregation=ProbeAggregation.MEAN,
        run_id="run-1",
        metadata={"scope": "model"},
    )

    params = ModelParameterProbeSummary(
        summary,
        parameter_count=1024,
        trainable_parameter_count=512,
        parameter_norm=1.2,
    )
    grad = ModelGradientProbeSummary(
        summary,
        gradient_norm=0.25,
        clipping_ratio=0.1,
        nan_fraction=0.0,
        inf_fraction=0.0,
    )
    activation = ModelActivationProbeSummary(
        summary,
        shape=(1, 3, 224, 224),
        dtype="float32",
        min_value=-1.0,
        max_value=1.0,
    )
    health = ModelHealthProbeSummary(
        summary,
        nonfinite_count=0,
        nan_fraction=0.0,
        inf_fraction=0.0,
        zero_fraction=0.12,
        saturation_fraction=0.03,
        clipping_fraction=0.01,
    )

    inspected = asdict(params)
    assert inspected["summary"]["name"] == "gradient"
    assert inspected["summary"]["metadata"] == {"scope": "model"}
    assert grad.clipping_ratio == 0.1
    assert activation.shape == (1, 3, 224, 224)
    assert health.saturation_fraction == 0.03

    with pytest.raises(RemotePhysTrainingError) as nonfinite_value:
        ModelProbeSummary(
            "bad-model-probe",
            "gradient",
            hook_point=ProbeHookPoint.FORWARD,
            selector=selector,
            cadence=cadence,
            value=float("nan"),
        )
    assert nonfinite_value.value.context["field"] == "value"


def test_data_probe_summaries_capture_field_and_batch_evidence() -> None:
    selector = ProbeSelector(ProbeSelectorMode.BY_SPLIT, ("train", "val"))
    cadence = ProbeCadence(ProbeCadenceMode.EVERY_N_EPOCHS, interval=2)
    data_summary = DataProbeSummary(
        "data-probe",
        "batch",
        hook_point=ProbeHookPoint.BATCH_FETCH,
        selector=selector,
        cadence=cadence,
        pipeline_stage="pre_augmentation",
        split="train",
    )

    field_summary = DataFieldProbeSummary(
        data_summary,
        field="signal",
        shape=(32, 128),
        dtype="float32",
        locator="batch.signal",
        present_ratio=0.98,
    )
    sample_summary = DataSampleProbeSummary(
        data_summary,
        batch_size=32,
        mask_fraction=0.01,
        mean_value=0.1,
    )

    assert data_summary.pipeline_stage is TrainingPipelineStage.PRE_AUGMENTATION
    assert sample_summary.batch_size == 32
    assert field_summary.locator == "batch.signal"


def test_unavailable_probe_evidence_remains_primitive_and_protocol_is_structural() -> None:
    unavailable = ProbeUnavailable("missing", reason="disabled")
    assert unavailable.name == "missing"

    detailed = UnavailableProbeEvidence(
        "probe",
        reason="disabled",
        hook_point="checkpoint",
        selector=ProbeSelector(ProbeSelectorMode.ALL),
        failure_policy=ProbeFailurePolicy.UNAVAILABLE,
        run_id="run-1",
    )
    assert detailed.reason == "disabled"
    assert detailed.run_id == "run-1"

    unsupported = UnavailableProbeEvidence(
        "probe",
        reason="backend_missing",
        hook_point="checkpoint",
        selector=ProbeSelector(ProbeSelectorMode.ALL),
        failure_policy="unsupported",
    )
    assert unsupported.failure_policy is ProbeFailurePolicy.UNSUPPORTED

    collector = ProbeCollector()
    assert isinstance(collector, TrainingProbe)
    assert collector.collect({})[0].name == "batch"

    with pytest.raises(RemotePhysTrainingError) as ratio_error:
        DataSampleProbeSummary(
            DataProbeSummary(
                "bad",
                "batch",
                hook_point=ProbeHookPoint.BATCH_FETCH,
                selector=ProbeSelector(ProbeSelectorMode.ALL),
                cadence=ProbeCadence(ProbeCadenceMode.MANUAL),
            ),
            mask_fraction=2.0,
        )
    assert ratio_error.value.context["field"] == "mask_fraction"
