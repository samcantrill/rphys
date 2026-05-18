from __future__ import annotations

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.datasources.datapath import (
    DataLoaderState,
    DataPipelineStage,
    FakeDataQualityProbe,
    StreamingReadPlan,
    build_data_path_benchmark,
    build_data_path_profile,
    build_data_pipeline_stage_context,
)
from rphys.datasources.sources import SampleRequest, SampleRuntimeContext
from rphys.ops import (
    BatchEquivalenceReport,
    BatchOperationContext,
    BatchOperationContract,
    BatchTransform,
    SampleFieldPermissions,
)


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
MASK = FieldLocator.parse("metadata/metadata.valid")
LABEL = FieldLocator.parse("metadata/label.subject")
PRED = FieldLocator.parse("outputs/signal.bvp.predicted")


def test_stage15_data_path_profile_records_pipeline_probes_and_batch_evidence() -> None:
    request = SampleRequest([VIDEO, BVP, MASK, LABEL], eager=True)
    runtime_context = SampleRuntimeContext(
        index_id="stage15-index",
        entry_id="stage15-index:0",
        position=0,
        candidate_id="candidate-0",
        record_id="record-0",
        datasource_id="synthetic-rphys",
        source_id="camera-a",
        request_fingerprint=request.fingerprint,
        split="train",
        worker_id=0,
        rank=0,
        metadata={"path": "process-cache-augment-process"},
    )
    streaming = StreamingReadPlan(
        "stage15-stream",
        mode="windowed",
        request_fingerprint=request.fingerprint,
        sample_count=1,
        start_position=0,
        stop_position=1,
        worker_count=1,
    )
    state = DataLoaderState(
        "stage15-state",
        streaming_plan_fingerprint=streaming.fingerprint,
        request_fingerprint=request.fingerprint,
        positions_seen=1,
        cache_hits=1,
        batch_count=1,
        last_position=0,
    )

    batch = Batch(
        {
            VIDEO: FieldValue(["frame-0"], schema="video.rgb.v1"),
            BVP: FieldValue([0.1, float("nan")], schema="signal.bvp.v1"),
            MASK: FieldValue([True, "bad"]),
            LABEL: FieldValue(["subject-001"]),
        }
    )

    def copy_reference(payload: Batch, *, context) -> Batch:
        payload.set_field(PRED, FieldValue(list(payload.require(BVP)), schema="signal.bvp.v1"))
        return payload

    transform = BatchTransform(
        copy_reference,
        name="copy-reference",
        contract=BatchOperationContract(
            field_permissions=SampleFieldPermissions(reads=(BVP,), writes=(PRED,)),
            dtype="float32",
            device="cpu",
            equivalence=BatchEquivalenceReport(
                claim="identical",
                reference_operation="sample-copy-reference",
                sample_count=1,
            ),
        ),
    )
    batch_result = transform(
        batch,
        context=BatchOperationContext(
            operation_index=0,
            operation_name="copy-reference",
            batch_size=1,
            dtype="float32",
            device="cpu",
            metadata={"alignment": "sample-order"},
            provenance={"operation_fingerprint": "sample-copy-reference"},
        ),
    )

    probe = FakeDataQualityProbe(
        "stage15-quality",
        expected_fields=(str(VIDEO), str(BVP), str(MASK), str(LABEL)),
        mask_fields=(str(MASK),),
        expected_shapes={str(BVP): [2]},
        expected_dtypes={str(BVP): "float32"},
        expected_devices={str(BVP): "cpu"},
        label_field=str(LABEL),
        required_provenance=("subject_id",),
    )
    quality_results = probe.inspect(
        {str(locator): value for locator, value in batch.field_items()},
        stage=DataPipelineStage.POST_PROCESSING,
        field_metadata={str(BVP): {"shape": [2], "dtype": "float32", "device": "cpu"}},
        provenance={"record_id": "record-0"},
    )

    contexts = (
        build_data_pipeline_stage_context(
            DataPipelineStage.INDEXED,
            source_kind="source",
            request=request,
            runtime_context=runtime_context,
            streaming_plan=streaming,
            loader_state=state,
            measurements={"duration.queue_wait.ms": 0.0},
        ),
        build_data_pipeline_stage_context(
            DataPipelineStage.CACHE_LOOKUP,
            source_kind="cache",
            request=request,
            runtime_context=runtime_context,
            streaming_plan=streaming,
            loader_state=state,
            cache_status="hit",
            measurements={"cache.hit.count": 1},
        ),
        build_data_pipeline_stage_context(
            DataPipelineStage.POST_AUGMENTATION,
            source_kind="augmentation",
            request=request,
            runtime_context=runtime_context,
            streaming_plan=streaming,
            loader_state=state,
            batch_operation_name=batch_result.operation_name,
            batch_operation_index=0,
            measurements={"duration.collate.ms": 0.2},
            metadata={
                "batch_equivalence_claim": batch_result.metadata["batch_equivalence"]["claim"],
                "batch_field_effects": {
                    key: list(value) if isinstance(value, tuple) else value
                    for key, value in dict(batch_result.metadata["batch_field_effects"]).items()
                },
                "dtype": "float32",
                "device": "cpu",
                "mask_alignment": "sample-order",
            },
        ),
        build_data_pipeline_stage_context(
            DataPipelineStage.COLLATE,
            source_kind="collate",
            request=request,
            runtime_context=runtime_context,
            streaming_plan=streaming,
            loader_state=state,
            measurements={"duration.collate.ms": 0.1},
        ),
    )
    profile = build_data_path_profile(
        "stage15-profile",
        loader_state=state,
        streaming_plan=streaming,
        stage_contexts=contexts,
        measurements={
            "duration.queue_wait.ms": 0.0,
            "duration.collate.ms": 0.3,
            "bytes.read": 128,
            "throughput.samples_per_second": 5.0,
            "unavailable.count": 0,
        },
        summaries={"quality_probe_fingerprints": [result.fingerprint for result in quality_results]},
        total_duration_ms=0.5,
        dataloader_wait_ms=0.0,
        cache_wait_ms=0.1,
        throughput_samples_per_second=5.0,
    )
    benchmark = build_data_path_benchmark(
        "stage15-benchmark",
        profiles=(profile,),
        measurements={"throughput.samples_per_second": 5.0, "bytes.read": 128},
        environment={"synthetic": True},
    )

    assert batch_result.metadata["batch_equivalence"]["claim"] == "identical"
    assert {result.issue_kind.value for result in quality_results} >= {
        "nan",
        "invalid_mask",
        "label_distribution",
        "provenance_anomaly",
    }
    assert profile.summaries["pipeline_stages"] == (
        "indexed",
        "cache_lookup",
        "post_augmentation",
        "collate",
    )
    assert profile.summaries["measurements"]["bytes.read"] == 128
    assert benchmark.metric == "throughput.samples_per_second"
    assert benchmark.limitations["thresholds_claimed"] is False
    assert benchmark.profile_fingerprints == (profile.fingerprint,)
