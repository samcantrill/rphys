from __future__ import annotations

import json

from rphys.data import Batch, BatchCollater
from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.cache import (
    CacheContext,
    CacheEntry,
    CachedSampleSource,
    LocalCacheStore,
)
from rphys.datasources.datapath import (
    DataLoaderState,
    DataPathBenchmark,
    DataPathProfile,
    StreamingReadPlan,
)
from rphys.datasources.indexes import DataSourceIndex, DataSourceIndexEntry
from rphys.datasources.prepared import (
    AccessPatternPlan,
    BatchCostMetadata,
    BatchSamplerPlan,
    BatchShapePolicy,
    ChunkMetadata,
    MaterializationManifest,
    MaterializationPlan,
    OptimizedDataPlan,
    OptimizedStorageFormat,
    PreparedDataManifest,
    PreparedField,
    PreparedReadRequest,
    PreparedReadResult,
    PreparedSampleSource,
    RecordLayoutMetadata,
    ShardManifest,
)
from rphys.datasources.sources import IndexSampleSource, SampleRequest, SampleRuntimeContext, SampleSource
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO, make_builder_fixture


def test_stage9_data_path_flow_records_source_cache_prepared_and_batch_evidence(tmp_path) -> None:
    request = SampleRequest([VIDEO, BVP], eager=True)
    batch = _source_to_batch(request)

    cache_sample, cache_hit = _cache_round_trip(tmp_path, request)
    prepared_sample, prepared_manifest = _prepared_round_trip(request)
    materialization, sampler_plan = _materialization_and_batch_plans(
        prepared_manifest=prepared_manifest,
        request=request,
    )

    streaming = StreamingReadPlan(
        "integration-stream",
        mode="windowed",
        request_fingerprint=request.fingerprint,
        materialization_fingerprint=materialization.fingerprint,
        sample_count=2,
        start_position=0,
        stop_position=2,
        prefetch=1,
        worker_count=1,
        metadata={"source": "synthetic"},
    )
    state = DataLoaderState(
        "integration-state",
        streaming_plan_fingerprint=streaming.fingerprint,
        request_fingerprint=request.fingerprint,
        positions_seen=2,
        cache_hits=1,
        cache_misses=1,
        prepared_reads=1,
        materialized_reads=1,
        batch_count=1,
        last_position=1,
        metadata={"batch_sampler_fingerprint": sampler_plan.fingerprint},
    )
    profile = DataPathProfile(
        "integration-profile",
        loader_state_fingerprint=state.fingerprint,
        streaming_plan_fingerprint=streaming.fingerprint,
        sample_count=2,
        batch_count=1,
        cache_hits=1,
        cache_misses=1,
        prepared_reads=1,
        materialized_reads=1,
        total_duration_ms=1.0,
        dataloader_wait_ms=0.0,
        throughput_samples_per_second=2.0,
        summaries={
            "batch_fields": [str(locator) for locator, _ in batch.field_items()],
            "cache_status": cache_hit,
            "prepared_manifest": prepared_manifest.fingerprint,
        },
        metadata={"scope": "integration"},
    )
    benchmark = DataPathBenchmark(
        "integration-benchmark",
        profile_fingerprints=[profile.fingerprint],
        metric="throughput_samples_per_second",
        value=2.0,
        unit="samples/s",
        measurements={"single_synthetic_run": 2.0},
        limitations={"synthetic": True, "thresholds_claimed": False},
    )

    for descriptor in (streaming, state, profile, benchmark):
        json.dumps(descriptor.to_dict(), sort_keys=True)

    assert isinstance(batch, Batch)
    assert batch.require(VIDEO) == [("f1", "f2"), ("f1", "f2")]
    assert cache_sample.require(BVP) == (0.1, 0.2)
    assert prepared_sample.require(VIDEO) == "prepared-video"
    assert profile.cache_hits == 1
    assert benchmark.profile_fingerprints == (profile.fingerprint,)
    assert "threshold" not in benchmark.to_dict()


def _source_to_batch(request: SampleRequest) -> Batch:
    fixture = make_builder_fixture()
    index = DataSourceIndex(
        "stage9-datapath",
        [fixture.item, fixture.item],
        [
            _entry_for_item("stage9-datapath", 0, fixture.item),
            _entry_for_item("stage9-datapath", 1, fixture.item),
        ],
    )
    source = IndexSampleSource(index, fixture.builder)
    samples = [source.sample_at(0, request=request), source.sample_at(1, request=request)]
    for sample in samples:
        for _, field_value in sample.field_items():
            field_value.collate_policy = "list"
    return BatchCollater()(samples)


def _cache_round_trip(tmp_path, request: SampleRequest) -> tuple[Sample, str]:
    store = LocalCacheStore(tmp_path)
    cache_context = CacheContext(invalidation={"source_checksum": "v1"})
    writer = CachedSampleSource(
        RecordingSampleSource([_sample("source-video", [0.1, 0.2])]),
        store,
        cache_context=cache_context,
        context_factory=_context_factory,
        entry_factory=lambda sample, key: CacheEntry(
            key=key,
            field_locators=[VIDEO, BVP],
            value_strategy="explicit-test-token",
            value_token={
                "video": sample.require(VIDEO),
                "bvp": sample.require(BVP),
            },
        ),
    )
    writer.sample_at(0, request=request)

    reader = CachedSampleSource(
        RecordingSampleSource([_sample("delegate-video", [9.9])]),
        store,
        cache_context=cache_context,
        context_factory=_context_factory,
        hit_loader=lambda entry: _sample(
            entry.value_token["video"],  # type: ignore[index]
            entry.value_token["bvp"],  # type: ignore[index]
        ),
    )
    sample = reader.sample_at(0, request=request)

    assert writer.last_lookup is not None
    assert writer.last_lookup.status == "miss"
    assert reader.last_lookup is not None
    assert reader.last_lookup.status == "hit"
    return sample, reader.last_lookup.status


def _prepared_round_trip(request: SampleRequest) -> tuple[Sample, PreparedDataManifest]:
    manifest = PreparedDataManifest(
        manifest_id="stage9-datapath-prepared",
        backend_id="fake-prepared",
        index_id="stage9-datapath-prepared-index",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        sample_count=1,
        request_fingerprint=request.fingerprint,
        fields=[
            PreparedField(VIDEO, schema="video.rgb.v1", dtype="uint8", shape=(2,), checksum="sha256:video"),
            PreparedField(BVP, schema="signal.bvp.v1", dtype="float32", shape=(2,), checksum="sha256:bvp"),
        ],
        split_counts={"train": 1},
        group_counts={"subject-001": 1},
        checksums={"manifest": "sha256:manifest"},
        layout={"format": "fake"},
        invalidation={"source_checksum": "v1"},
    )
    source = PreparedSampleSource(
        manifest,
        FakePreparedReader(manifest, [_sample("prepared-video", (0.5, 0.6))]),
    )
    return source.sample_at(0, request=request), manifest


def _materialization_and_batch_plans(
    *,
    prepared_manifest: PreparedDataManifest,
    request: SampleRequest,
) -> tuple[MaterializationManifest, BatchSamplerPlan]:
    storage_format = OptimizedStorageFormat("fake-table", version="1", capabilities={"sharded": True})
    optimized = OptimizedDataPlan(
        "optimized",
        storage_format=storage_format,
        prepared_manifest_fingerprint=prepared_manifest.fingerprint,
        field_locators=[VIDEO, BVP],
        sample_count=1,
        access_pattern=AccessPatternPlan("access", mode="sequential"),
        layout={"shards": 1},
        invalidation={"source_checksum": "v1"},
    )
    plan = MaterializationPlan(
        "materialization-plan",
        optimized_plan=optimized,
        prepared_manifest_fingerprint=prepared_manifest.fingerprint,
        request_fingerprint=request.fingerprint,
        field_locators=[VIDEO, BVP],
        sample_count=1,
        split_counts={"train": 1},
    )
    shard = ShardManifest(
        "shard-0",
        storage_format=storage_format,
        uri="memory://stage9/shard-0",
        sample_count=1,
        chunks=[
            ChunkMetadata(
                "chunk-0",
                field_locators=[VIDEO, BVP],
                sample_start=0,
                sample_count=1,
            )
        ],
    )
    materialization = MaterializationManifest(
        "materialization",
        plan_fingerprint=plan.fingerprint,
        storage_format=storage_format,
        prepared_manifest_fingerprint=prepared_manifest.fingerprint,
        shards=[shard],
        records=[
            RecordLayoutMetadata(
                "record-0",
                shard_id="shard-0",
                position=0,
                field_locators=[VIDEO, BVP],
            )
        ],
        sample_count=1,
        field_locators=[VIDEO, BVP],
    )
    sampler = BatchSamplerPlan(
        "sampler",
        shape_policy=BatchShapePolicy("shape", batch_size=2, field_locators=[VIDEO, BVP]),
        ordering="cost_aware",
        cost_metadata=[BatchCostMetadata(position=0, cost=1.0, length=2)],
    )
    return materialization, sampler


class RecordingSampleSource(SampleSource):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        return self.samples[position]


class FakePreparedReader:
    def __init__(self, manifest: PreparedDataManifest, samples: list[Sample]) -> None:
        self.manifest = manifest
        self.samples = samples

    def read(self, request: PreparedReadRequest) -> PreparedReadResult:
        locators = self.manifest.expected_locators(request.request)
        return PreparedReadResult(
            sample=Sample({locator: self.samples[request.position].field(locator) for locator in locators}),
            manifest_fingerprint=self.manifest.fingerprint,
            backend_id=self.manifest.backend_id,
            field_locators=locators,
        )


def _sample(video_payload: object, bvp_payload: object) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(video_payload, schema="video.rgb.v1"),
            BVP: FieldValue(bvp_payload, schema="signal.bvp.v1"),
        }
    )


def _context_factory(position: int, request: SampleRequest) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="stage9-datapath-cache",
        entry_id=f"stage9-datapath-cache:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=f"record-{position}",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        request_fingerprint=request.fingerprint,
    )


def _entry_for_item(
    index_id: str,
    position: int,
    fixture_item,
) -> DataSourceIndexEntry:
    return DataSourceIndexEntry(
        index_id=index_id,
        entry_id=f"{index_id}:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=fixture_item.record.record_id,
        datasource_id=fixture_item.record.datasource.datasource_id,
        source_id=fixture_item.record.datasource.datasource_id,
        groups={"subject": "subject-001", "source": fixture_item.record.datasource.datasource_id},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        source_key=index_id,
        metadata={"flow": "stage9-datapath"},
    )
