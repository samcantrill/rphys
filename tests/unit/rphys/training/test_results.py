from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode
from rphys.training import (
    ProfileSpanSummary,
    ProfileSummary,
    TrainingMetricSummary,
    TrainingEvent,
    TrainingEventSummary,
    TrainingEventLog,
    TrainingProfile,
    TrainingResult,
    TrainingStatus,
    TrainingStepSummary,
    UnavailableProfileProbe,
)


def test_training_result_preserves_primitive_summaries() -> None:
    metric = TrainingMetricSummary("mae", 0.4, unit="bpm", level="batch")
    last_step = TrainingStepSummary(
        LoopMode.TRAIN,
        epoch_index=0,
        step_index=2,
        batch_index=2,
        split="train",
        objective=0.4,
        metrics={"mae": 0.4},
    )
    result = TrainingResult(
        status=TrainingStatus.COMPLETED,
        mode="train",
        epoch_count=1,
        step_count=3,
        batch_count=3,
        metrics=(metric,),
        last_step=last_step,
        events=(TrainingEventSummary("loop_completed", count=1),),
        profiles=(ProfileSummary("forward", duration_seconds=0.01),),
        monitored_metric="mae",
        checkpoint_id="ckpt-1",
        metadata={"engine": "fake"},
        provenance={"test": "unit"},
    )

    assert result.status is TrainingStatus.COMPLETED
    assert result.mode is LoopMode.TRAIN
    assert result.metrics["mae"] is metric
    assert result.last_step is last_step
    assert result.events[0].name == "loop_completed"
    assert result.profiles[0].duration_seconds == 0.01
    assert result.metadata == {"engine": "fake"}
    assert result.provenance == {"test": "unit"}
    inspected = asdict(result)
    assert inspected["metrics"]["mae"]["value"] == 0.4
    assert inspected["metadata"] == {"engine": "fake"}

    with pytest.raises(TypeError):
        result.metrics["rmse"] = metric  # type: ignore[index]


def test_training_result_rejects_nonprimitive_and_duplicate_summaries() -> None:
    with pytest.raises(RemotePhysTrainingError) as metric_value_error:
        TrainingMetricSummary("bad", object())  # type: ignore[arg-type]
    assert metric_value_error.value.context["field"] == "value"

    with pytest.raises(RemotePhysTrainingError) as duplicate_error:
        TrainingResult(
            status="completed",
            mode="train",
            metrics=(TrainingMetricSummary("mae", 1.0), TrainingMetricSummary("mae", 2.0)),
        )
    assert duplicate_error.value.context["name"] == "mae"

    with pytest.raises(RemotePhysTrainingError) as status_error:
        TrainingResult(status="done", mode="train")  # type: ignore[arg-type]
    assert status_error.value.context["field"] == "status"

    with pytest.raises(RemotePhysTrainingError) as count_error:
        TrainingResult(status="completed", mode="train", step_count=-1)
    assert count_error.value.context["field"] == "step_count"

    with pytest.raises(RemotePhysTrainingError) as metadata_error:
        TrainingResult(status="completed", mode="train", metadata={"raw": object()})
    assert metadata_error.value.context["field"] == "metadata"


def test_training_result_can_derive_profiles_from_training_profile() -> None:
    profile = TrainingProfile(
        event_logs=(
            TrainingEventLog(
                "timeline-1",
                run_id="run-1",
                events=(
                    TrainingEvent(
                        "loop_started",
                        "train",
                        timeline_id="timeline-1",
                        run_id="run-1",
                        sequence_id=0,
                    ),
                ),
            ),
        ),
        scalar_spans=(ProfileSpanSummary("forward", status="available", duration_seconds=0.1),),
        unavailable_spans=(UnavailableProfileProbe("cuda", reason="disabled"),),
    )
    result = TrainingResult(status="completed", mode="train", training_profile=profile)

    assert result.training_profile is profile
    assert len(result.profiles) == 2
    assert result.profiles[0].name == "forward"
    assert result.profiles[0].duration_seconds == 0.1
    assert result.profiles[1].status == "unavailable"
    assert result.profiles[1].metadata["reason"] == "disabled"


def test_training_result_keeps_profiles_when_explicitly_passed_with_training_profile() -> None:
    profile = TrainingProfile(
        event_logs=(
            TrainingEventLog(
                "timeline-1",
                events=(TrainingEvent("loop_started", "train", timeline_id="timeline-1", sequence_id=0),),
            ),
        ),
        scalar_spans=(ProfileSpanSummary("forward", status="available"),),
    )
    explicit_summary = ProfileSummary("manual", status="available", duration_seconds=0.5)
    result = TrainingResult(
        status="completed",
        mode="train",
        training_profile=profile,
        profiles=(explicit_summary,),
    )

    assert result.profiles == (explicit_summary,)


def test_training_result_rejects_invalid_training_profile_type() -> None:
    with pytest.raises(RemotePhysTrainingError) as profile_error:
        TrainingResult(status="completed", mode="train", training_profile=object())  # type: ignore[arg-type]
    assert profile_error.value.context["field"] == "training_profile"


def test_training_result_has_no_raw_framework_or_artifact_state() -> None:
    result = TrainingResult(status="partial", mode="validate", failure="interrupted")

    for forbidden in [
        "raw_trainer",
        "framework_state",
        "optimizer",
        "scheduler",
        "checkpoint",
        "logger",
        "callback_state",
        "artifact",
    ]:
        assert not hasattr(result, forbidden)
