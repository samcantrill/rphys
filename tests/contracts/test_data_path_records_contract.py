from __future__ import annotations

import json

import pytest

from rphys.errors import FieldTypeError
from rphys.datasources.datapath import (
    DATA_PATH_MEASUREMENT_UNITS,
    DataLoaderState,
    DataPathBenchmark,
    DataPathProfile,
    DataPipelineStage,
    DataPipelineStageContext,
    DataQualityIssueKind,
    DataQualityProbeResult,
    FakeDataQualityProbe,
    StreamingReadPlan,
    build_data_path_benchmark,
    build_data_path_profile,
)
from rphys.training import TrainingPipelineStage

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


def test_data_pipeline_stage_context_round_trips_stage9_evidence() -> None:
    context = DataPipelineStageContext(
        DataPipelineStage.CACHE_LOOKUP,
        source_kind="cache",
        request_fingerprint=REQUEST_FP,
        cache_key_digest="b" * 64,
        cache_status="hit",
        sample_position=1,
        worker_id=0,
        measurements={"duration.queue_wait.ms": 1.25, "cache.hit.count": 1},
        metadata={"cache": "local"},
        provenance={"source": "contract"},
    )

    payload = context.to_dict()
    json.dumps(payload, sort_keys=True)
    loaded = DataPipelineStageContext.from_dict(payload)

    assert loaded.fingerprint == context.fingerprint
    assert loaded.stage is DataPipelineStage.CACHE_LOOKUP
    assert DATA_PATH_MEASUREMENT_UNITS["duration.queue_wait.ms"] == "ms"


def test_data_path_profile_and_benchmark_builders_reuse_existing_records() -> None:
    plan = StreamingReadPlan("contract-stage15-plan", request_fingerprint=REQUEST_FP, sample_count=2)
    state = DataLoaderState(
        "contract-stage15-state",
        streaming_plan_fingerprint=plan.fingerprint,
        request_fingerprint=REQUEST_FP,
        positions_seen=2,
        cache_hits=1,
        cache_misses=1,
        batch_count=1,
    )
    context = DataPipelineStageContext(
        "cache_lookup",
        source_kind="cache",
        request_fingerprint=REQUEST_FP,
        streaming_plan_fingerprint=plan.fingerprint,
        loader_state_fingerprint=state.fingerprint,
        measurements={"cache.hit.count": 1, "cache.miss.count": 1},
    )

    profile = build_data_path_profile(
        "contract-stage15-profile",
        loader_state=state,
        streaming_plan=plan,
        stage_contexts=(context,),
        measurements={"throughput.samples_per_second": 10.0},
        throughput_samples_per_second=10.0,
    )
    benchmark = build_data_path_benchmark(
        "contract-stage15-benchmark",
        profiles=(profile,),
        measurements={"throughput.samples_per_second": 10.0},
    )

    assert isinstance(profile, DataPathProfile)
    assert isinstance(benchmark, DataPathBenchmark)
    assert profile.summaries["pipeline_stages"] == ("cache_lookup",)
    assert benchmark.metric == "throughput.samples_per_second"
    assert benchmark.unit == "samples/s"
    assert benchmark.limitations["thresholds_claimed"] is False


def test_data_quality_fake_probe_records_primitive_issue_evidence() -> None:
    probe = FakeDataQualityProbe(
        "contract-data-quality",
        expected_fields=("inputs/video", "targets/bvp", "masks/valid"),
        mask_fields=("masks/valid",),
        expected_shapes={"targets/bvp": [2]},
        expected_dtypes={"targets/bvp": "float32"},
        expected_devices={"targets/bvp": "cpu"},
        label_field="labels/subject",
        required_provenance=("subject_id",),
    )

    results = probe.inspect(
        {
            "targets/bvp": [0.1, float("nan")],
            "masks/valid": [True, "bad"],
            "labels/subject": ["s1", "s1", "s2"],
        },
        stage="post_processing",
        field_metadata={"targets/bvp": {"shape": [2], "dtype": "float64", "device": "cpu"}},
        provenance={"record_id": "r1"},
    )

    kinds = {result.issue_kind for result in results}
    assert DataQualityIssueKind.MISSING_FIELD in kinds
    assert DataQualityIssueKind.NAN in kinds
    assert DataQualityIssueKind.INVALID_MASK in kinds
    assert DataQualityIssueKind.LABEL_DISTRIBUTION in kinds
    assert DataQualityIssueKind.DTYPE_DRIFT in kinds
    assert DataQualityIssueKind.PROVENANCE_ANOMALY in kinds
    for result in results:
        json.dumps(result.to_dict(), sort_keys=True)
        assert DataQualityProbeResult.from_dict(result.to_dict()).fingerprint == result.fingerprint

    shape_probe = FakeDataQualityProbe("shape-drift", expected_shapes={"targets/bvp": [3]})
    shape_results = shape_probe.inspect(
        {"targets/bvp": [0.1, 0.2]},
        stage="post_processing",
        field_metadata={"targets/bvp": {"shape": [2]}},
    )
    assert shape_results[0].issue_kind is DataQualityIssueKind.SHAPE_DRIFT
    assert shape_results[0].expected == (3,)
    assert DataQualityProbeResult.from_dict(shape_results[0].to_dict()).fingerprint == shape_results[0].fingerprint


def test_data_pipeline_stage_names_align_with_training_probe_vocabulary() -> None:
    for stage in (
        DataPipelineStage.PRE_CACHE_PROCESSING,
        DataPipelineStage.CACHE_LOOKUP,
        DataPipelineStage.PREPARED_READ,
        DataPipelineStage.COLLATE,
        DataPipelineStage.PRE_DEVICE_TRANSFER,
        DataPipelineStage.POST_DEVICE_TRANSFER,
    ):
        assert TrainingPipelineStage(stage.value).value == stage.value


def test_reserved_data_path_measurements_validate_units_without_thresholds() -> None:
    with pytest.raises(FieldTypeError):
        DataPipelineStageContext(
            "queue_wait",
            measurements={"duration.queue_wait.ms": -1.0},
        )
    with pytest.raises(FieldTypeError):
        build_data_path_benchmark(
            "invalid",
            profiles=(DataPathProfile("profile"),),
            value=1.0,
            measurements={"bytes.read": "many"},
        )
