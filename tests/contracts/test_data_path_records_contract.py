from __future__ import annotations

import json

from rphys.datasources.datapath import (
    DataLoaderState,
    DataPathBenchmark,
    DataPathProfile,
    StreamingReadPlan,
)

REQUEST_FP = "a" * 64


def test_data_path_records_contract_round_trips_primitive_evidence() -> None:
    plan = StreamingReadPlan(
        "contract-plan",
        mode="resume_hint",
        request_fingerprint=REQUEST_FP,
        sample_count=2,
        start_position=0,
        stop_position=2,
        resume_token={"position": 0},
        metadata={"contract": "datapath"},
    )
    state = DataLoaderState(
        "contract-state",
        streaming_plan_fingerprint=plan.fingerprint,
        request_fingerprint=REQUEST_FP,
        positions_seen=2,
        cache_hits=1,
        cache_misses=1,
        prepared_reads=1,
        batch_count=1,
    )
    profile = DataPathProfile(
        "contract-profile",
        loader_state_fingerprint=state.fingerprint,
        streaming_plan_fingerprint=plan.fingerprint,
        sample_count=2,
        batch_count=1,
        cache_hits=1,
        cache_misses=1,
        prepared_reads=1,
        total_duration_ms=10.0,
        throughput_samples_per_second=200.0,
    )
    benchmark = DataPathBenchmark(
        "contract-benchmark",
        profile_fingerprints=[profile.fingerprint],
        metric="throughput_samples_per_second",
        value=200.0,
        unit="samples/s",
        limitations={"synthetic": True},
    )

    for descriptor in (plan, state, profile, benchmark):
        payload = descriptor.to_dict()
        json.dumps(payload, sort_keys=True)

        loaded = type(descriptor).from_dict(payload)

        assert loaded.fingerprint == descriptor.fingerprint


def test_data_path_records_contract_remains_descriptive_only() -> None:
    plan = StreamingReadPlan("contract-plan", sample_count=1)
    state = DataLoaderState("contract-state", streaming_plan_fingerprint=plan.fingerprint)
    profile = DataPathProfile("contract-profile", loader_state_fingerprint=state.fingerprint)
    benchmark = DataPathBenchmark(
        "contract-benchmark",
        profile_fingerprints=[profile.fingerprint],
        metric="samples_per_second",
        value=1.0,
        unit="samples/s",
    )

    for descriptor in (plan, state, profile, benchmark):
        for runtime_method in (
            "benchmark",
            "cache",
            "iterate",
            "materialize",
            "profile",
            "read",
            "resume",
            "sample",
            "write",
            "__iter__",
            "__next__",
        ):
            assert not hasattr(descriptor, runtime_method)

    assert "threshold" not in benchmark.to_dict()
    assert plan.distributed_coordination == "none"
