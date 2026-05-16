from __future__ import annotations

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import ProfileSpanSummary, TrainingProfiler, UnavailableProfileProbe


class FakeProfiler:
    def span(self, name: str, **kwargs: object) -> ProfileSpanSummary:
        return ProfileSpanSummary(name, **kwargs)


def test_profile_span_summary_records_timing_availability_and_overhead() -> None:
    span = ProfileSpanSummary(
        "forward",
        mode="train",
        duration_seconds=0.01,
        overhead_seconds=0.001,
        metadata={"clock": "cpu"},
    )

    assert span.name == "forward"
    assert span.mode is not None
    assert span.mode.value == "train"
    assert span.duration_seconds == 0.01
    assert span.overhead_seconds == 0.001
    assert span.metadata == {"clock": "cpu"}


def test_unavailable_probe_converts_to_unavailable_span() -> None:
    probe = UnavailableProfileProbe("cuda-sync", reason="cuda unavailable", overhead_seconds=0.0)
    span = probe.as_span()

    assert span.name == "cuda-sync"
    assert span.status == "unavailable"
    assert span.metadata["reason"] == "cuda unavailable"


def test_training_profiler_protocol_and_validation() -> None:
    profiler = FakeProfiler()

    assert isinstance(profiler, TrainingProfiler)
    assert profiler.span("forward", mode="test").mode.value == "test"

    with pytest.raises(RemotePhysTrainingError) as duration_error:
        ProfileSpanSummary("bad", duration_seconds=-1.0)
    assert duration_error.value.context["field"] == "duration_seconds"

    with pytest.raises(RemotePhysTrainingError) as reason_error:
        UnavailableProfileProbe("bad", reason="")
    assert reason_error.value.context["field"] == "reason"
