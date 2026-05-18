from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    CheckpointCatalog,
    CheckpointRef,
    CheckpointRefStatus,
    CheckpointSelection,
    CheckpointSelectionMode,
    CheckpointSelectionResult,
    ProbeCadence,
    ProbeCadenceMode,
    ProbeHookPoint,
    PrecisionPolicy,
    PolicyStatus,
    TrainingPipelineStage,
    DataSampleProbeSummary,
    DataProbeSummary,
    ModelGradientProbeSummary,
    ModelProbeSummary,
    ProbeSelector,
    ProbeSelectorMode,
)


def test_phase15_pipeline_stage_and_hook_vocabularies_are_stage_stable() -> None:
    for value in (
        "setup",
        "teardown",
        "failure",
        "epoch_started",
        "step_started",
        "batch_fetch",
        "pre_device_transfer",
        "validation",
        "checkpoint",
        "pipeline_stage",
    ):
        assert ProbeHookPoint.coerce(value).value == value

    expected_stages = {
        "indexed",
        "pre_cache_processing",
        "cache_lookup",
        "cache_hit_load",
        "cache_miss_source_read",
        "cache_write",
        "prepared_read",
        "pre_augmentation",
        "post_augmentation",
        "post_processing",
        "collate",
        "pre_device_transfer",
        "post_device_transfer",
        "learner_output_validation",
    }

    assert {value.value for value in TrainingPipelineStage} == expected_stages


def test_probe_dataclass_records_stay_primitive_and_nested() -> None:
    cadence = ProbeCadence(mode=ProbeCadenceMode.ON_METRIC, metric_name="loss", metric_direction="min")
    selector = ProbeSelector(ProbeSelectorMode.BY_HOOK, values=("forward",))
    model_summary = ModelProbeSummary(
        "model-probe",
        "gradient",
        hook_point="forward",
        selector=selector,
        cadence=cadence,
    )
    gradient = ModelGradientProbeSummary(model_summary, gradient_norm=0.7, nan_fraction=0.0, inf_fraction=0.0)
    inspected = asdict(gradient)

    assert inspected["summary"]["name"] == "gradient"
    assert inspected["summary"]["hook_point"] == "forward"
    assert isinstance(inspected["nan_fraction"], float)
    assert inspected["summary"]["metadata"] == {}

    data_summary = DataProbeSummary(
        "data-probe",
        "batch",
        hook_point="batch_fetch",
        selector=ProbeSelector(ProbeSelectorMode.BY_SPLIT, values=("train", "val")),
        cadence=ProbeCadence("every_n_steps", interval=1),
        pipeline_stage="pre_augmentation",
        split="train",
    )
    data_sample = DataSampleProbeSummary(
        data_summary,
        batch_size=64,
        mean_value=0.0,
    )
    assert asdict(data_sample)["summary"]["pipeline_stage"] == "pre_augmentation"


def test_checkpoint_selection_contracts_cover_latest_best_and_rewind_cases() -> None:
    refs = (
        CheckpointRef("a", stream_id="s", status="completed", epoch=1, step=10, timestamp=1.0),
        CheckpointRef(
            "b",
            stream_id="s",
            status="completed",
            epoch=2,
            step=20,
            timestamp=2.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=1.0,
        ),
        CheckpointRef(
            "c",
            stream_id="s",
            status="completed",
            epoch=3,
            step=30,
            timestamp=3.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=0.5,
        ),
        CheckpointRef(
            "d",
            stream_id="s",
            status="completed",
            epoch=4,
            step=40,
            timestamp=4.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=2.0,
            is_failure=True,
        ),
        CheckpointRef("e", stream_id="s", is_final=True, status="completed", epoch=5, step=50, timestamp=5.0),
    )
    catalog = CheckpointCatalog(refs)

    latest = catalog.select(CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED))
    assert latest.status is not None
    assert latest.ref is not None
    assert latest.ref.ref_id == "e"

    best = catalog.select(
        CheckpointSelection(
            CheckpointSelectionMode.BEST_BY_METRIC,
            metric_name="loss",
            metric_direction="min",
        ),
    )
    assert best.status is not None
    assert best.ref is not None
    assert best.ref.ref_id == "c"

    rewind_steps = catalog.select(CheckpointSelection(CheckpointSelectionMode.N_STEPS_BACK, step_back=25))
    assert rewind_steps.ref is not None
    assert rewind_steps.ref.step == 20

    rewind_epochs = catalog.select(CheckpointSelection(CheckpointSelectionMode.N_EPOCHS_BACK, epoch_back=1))
    assert rewind_epochs.ref is not None
    assert rewind_epochs.ref.epoch == 4

    no_match = catalog.select(
        CheckpointSelection(
            CheckpointSelectionMode.EXPLICIT,
            explicit_ref_id="missing",
        ),
    )
    assert no_match.status.value == "unavailable"
    assert no_match.ref is None

    evidence = asdict(no_match)
    assert evidence["status"] == "unavailable"
    assert evidence["selection"]["mode"] == "explicit"


def test_precision_policy_contract_records_backend_applicability() -> None:
    policy = PrecisionPolicy(
        "bf16-mixed",
        status=PolicyStatus.REQUESTED,
        supported_backends=("torch", "jax"),
        metadata={"requested_by": "unit"},
        provenance={"scope": "training"},
    )

    assert policy.requested_precision == "bf16-mixed"
    assert policy.supported_backends == ("torch", "jax")
    assert asdict(policy)["provenance"] == {"scope": "training"}

    with pytest.raises(RemotePhysTrainingError):
        CheckpointSelectionResult(
            selection=CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED),
            status="completed",
        )


def test_checkpoint_ref_statuses_are_frozen_and_primitive() -> None:
    ref = CheckpointRef(
        "frozen",
        status=CheckpointRefStatus.COMPLETED,
        epoch=1,
        step=2,
        metadata={"adapter": "contract"},
    )
    payload = asdict(ref)
    assert payload["status"] == "completed"
    assert isinstance(payload["metric_value"], type(None))
    assert payload["metadata"] == {"adapter": "contract"}
