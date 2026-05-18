from __future__ import annotations

from rphys.training import (
    ProfileSpanSummary,
    TrainingEvent,
    TrainingEventLog,
    TrainingEventPhase,
    UnavailableProfileProbe,
)


def test_observability_records_preserve_mode_phase_status_and_unavailable_probe_reason() -> None:
    event = TrainingEvent(
        TrainingEventPhase.STEP_COMPLETED,
        "train",
        status="completed",
        step_index=1,
        metadata={"loss": 0.1},
    )
    probe = UnavailableProfileProbe("cuda-timing", reason="cuda unavailable")
    span = ProfileSpanSummary("forward", mode="train", status="available", duration_seconds=0.01)

    assert event.phase.value == "step_completed"
    assert event.mode.value == "train"
    assert event.metadata == {"loss": 0.1}
    assert probe.as_span().status == "unavailable"
    assert probe.as_span().metadata["reason"] == "cuda unavailable"
    assert span.mode.value == "train"


def test_observability_contract_preserves_stage12_phase_values() -> None:
    stage12_values = (
        "loop_started",
        "step_started",
        "step_completed",
        "loop_completed",
        "loop_failed",
        "external_summary",
    )

    assert (
        tuple(TrainingEventPhase.coerce(value).value for value in stage12_values)
        == stage12_values
    )


def test_observability_contract_does_not_define_loop_control_methods() -> None:
    event = TrainingEvent("step_started", "predict")

    for forbidden in ["stop", "skip_batch", "set_lr", "backward", "optimizer_step"]:
        assert not hasattr(event, forbidden)


def test_observability_contract_records_timeline_log_evidence() -> None:
    event = TrainingEvent(
        TrainingEventPhase.STEP_COMPLETED,
        "train",
        sequence_id=1,
        timestamp=0.25,
        timeline_id="timeline-1",
        run_id="run-1",
    )
    log = TrainingEventLog(
        "timeline-1",
        run_id="run-1",
        events=(event,),
    )

    assert log.timeline_id == "timeline-1"
    assert log.events[0].timestamp == 0.25
    assert log.events[0].run_id == "run-1"
