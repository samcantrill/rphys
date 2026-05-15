from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.datasources.datapath import (
    DataLoaderState,
    DataPathBenchmark,
    DataPathProfile,
    StreamingReadPlan,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError

REQUEST_FP = "a" * 64
MATERIALIZATION_FP = "b" * 64


def test_data_path_records_round_trip_as_fingerprinted_primitives() -> None:
    plan = _streaming_plan()
    state = _loader_state(plan)
    profile = _profile(plan, state)
    benchmark = _benchmark(profile)

    for descriptor in (plan, state, profile, benchmark):
        loaded = type(descriptor).from_dict(descriptor.to_dict())

        assert loaded.to_dict() == descriptor.to_dict()
        assert loaded.fingerprint == descriptor.fingerprint

    assert profile.summaries["cache_status"] == "hit"
    assert benchmark.profile_fingerprints == (profile.fingerprint,)


def test_data_path_record_fingerprints_change_with_evidence() -> None:
    baseline = _profile()

    assert baseline.fingerprint != _profile(cache_hits=2).fingerprint
    assert _streaming_plan().fingerprint != _streaming_plan(skip_positions=[1]).fingerprint
    assert _benchmark(baseline).fingerprint != _benchmark(baseline, value=8.0).fingerprint


def test_data_path_records_are_immutable() -> None:
    plan = _streaming_plan()

    with pytest.raises(FrozenInstanceError):
        plan.plan_id = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        plan.metadata["scope"] = "mutated"  # type: ignore[index]


def test_streaming_read_plan_rejects_active_or_incoherent_runtime_claims() -> None:
    with pytest.raises(RemotePhysDataSourceError, match="greater than"):
        _streaming_plan(start_position=2, stop_position=2)
    with pytest.raises(RemotePhysDataSourceError, match="sample_count"):
        _streaming_plan(sample_count=2, start_position=3)
    with pytest.raises(RemotePhysDataSourceError, match="skip_positions"):
        _streaming_plan(sample_count=2, stop_position=2, skip_positions=[2])
    with pytest.raises(FieldTypeError, match="unsupported"):
        _streaming_plan(mode="streaming")
    with pytest.raises(FieldTypeError, match="unsupported"):
        _streaming_plan(distributed_coordination="stable")


def test_loader_state_rejects_invalid_counts_and_non_primitive_metadata() -> None:
    with pytest.raises(FieldTypeError, match="non-negative"):
        DataLoaderState("bad", positions_seen=-1)
    with pytest.raises(FieldTypeError, match="unsupported"):
        DataLoaderState("bad", status="resuming")
    with pytest.raises(FieldTypeError):
        DataLoaderState("bad", metadata={"bad": object()})


def test_profile_rejects_invalid_durations_and_counts() -> None:
    with pytest.raises(FieldTypeError, match="finite"):
        DataPathProfile("bad", total_duration_ms=float("nan"))
    with pytest.raises(FieldTypeError, match="non-negative"):
        DataPathProfile("bad", cache_misses=-1)
    with pytest.raises(FieldTypeError):
        DataPathProfile("bad", summaries={"bad": object()})


def test_benchmark_rejects_ambiguous_profiles_or_threshold_like_shape() -> None:
    profile = _profile()

    with pytest.raises(FieldTypeError, match="must not be empty"):
        DataPathBenchmark(
            "bad",
            profile_fingerprints=[],
            metric="samples_per_second",
            value=1.0,
            unit="samples/s",
        )
    with pytest.raises(FieldTypeError, match="unique"):
        DataPathBenchmark(
            "bad",
            profile_fingerprints=[profile.fingerprint, profile.fingerprint],
            metric="samples_per_second",
            value=1.0,
            unit="samples/s",
        )
    with pytest.raises(FieldTypeError, match="positive"):
        _benchmark(profile, repetitions=0)
    assert "threshold" not in _benchmark(profile).to_dict()


def _streaming_plan(
    *,
    mode: str = "windowed",
    sample_count: int = 4,
    start_position: int = 0,
    stop_position: int | None = 4,
    skip_positions: list[int] | None = None,
    distributed_coordination: str = "none",
) -> StreamingReadPlan:
    return StreamingReadPlan(
        "stream-0",
        mode=mode,
        request_fingerprint=REQUEST_FP,
        materialization_fingerprint=MATERIALIZATION_FP,
        sample_count=sample_count,
        start_position=start_position,
        stop_position=stop_position,
        skip_positions=skip_positions or [],
        resume_token={"position": start_position},
        prefetch=2,
        worker_count=1,
        distributed_coordination=distributed_coordination,
        metadata={"scope": "unit"},
    )


def _loader_state(plan: StreamingReadPlan | None = None) -> DataLoaderState:
    plan = plan or _streaming_plan()
    return DataLoaderState(
        "state-0",
        status="completed",
        streaming_plan_fingerprint=plan.fingerprint,
        request_fingerprint=REQUEST_FP,
        positions_seen=4,
        positions_skipped=0,
        positions_resumed=0,
        cache_hits=1,
        cache_misses=1,
        rereads=0,
        prepared_reads=1,
        materialized_reads=1,
        batch_count=1,
        last_position=3,
        metadata={"scope": "unit"},
    )


def _profile(
    plan: StreamingReadPlan | None = None,
    state: DataLoaderState | None = None,
    *,
    cache_hits: int = 1,
) -> DataPathProfile:
    plan = plan or _streaming_plan()
    state = state or _loader_state(plan)
    return DataPathProfile(
        "profile-0",
        loader_state_fingerprint=state.fingerprint,
        streaming_plan_fingerprint=plan.fingerprint,
        sample_count=4,
        batch_count=1,
        cache_hits=cache_hits,
        cache_misses=1,
        rereads=0,
        prepared_reads=1,
        materialized_reads=1,
        total_duration_ms=12.5,
        dataloader_wait_ms=2.0,
        cache_wait_ms=1.0,
        materialization_wait_ms=3.0,
        throughput_samples_per_second=320.0,
        summaries={"cache_status": "hit", "prepared": True},
        metadata={"scope": "unit"},
    )


def _benchmark(
    profile: DataPathProfile,
    *,
    value: float = 320.0,
    repetitions: int = 1,
) -> DataPathBenchmark:
    return DataPathBenchmark(
        "benchmark-0",
        profile_fingerprints=[profile.fingerprint],
        metric="throughput_samples_per_second",
        value=value,
        unit="samples/s",
        repetitions=repetitions,
        measurements={"median": value},
        environment={"python": "3.12"},
        limitations={"synthetic": True, "thresholds_claimed": False},
        metadata={"scope": "unit"},
    )
