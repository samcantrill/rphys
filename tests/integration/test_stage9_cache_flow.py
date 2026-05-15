from __future__ import annotations

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.cache import (
    CacheContext,
    CacheEntry,
    CachedSampleSource,
    LocalCacheStore,
)
from rphys.datasources.sources import SampleRequest, SampleRuntimeContext, SampleSource
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO


def test_stage9_local_cache_flow_uses_request_context_and_invalidation_matrix(tmp_path) -> None:
    store = LocalCacheStore(tmp_path)
    request = SampleRequest([VIDEO, BVP])
    cache_context = CacheContext(invalidation={"source_checksum": "v1"})
    source = RecordingSampleSource([_sample("video-source", [0.1, 0.2])])
    writer = CachedSampleSource(
        source,
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

    written = writer.sample_at(0, request=request)

    assert written.require(VIDEO) == "video-source"
    assert writer.last_lookup is not None
    assert writer.last_lookup.status == "miss"
    assert writer.last_write is not None
    assert writer.last_write.written is True

    hit_source = RecordingSampleSource([_sample("video-delegate", [9.9])])
    reader = CachedSampleSource(
        hit_source,
        store,
        cache_context=cache_context,
        context_factory=_context_factory,
        hit_loader=lambda entry: _sample(
            entry.value_token["video"],  # type: ignore[index]
            entry.value_token["bvp"],  # type: ignore[index]
        ),
    )

    hit = reader.sample_at(0, request=request)

    assert hit.require(VIDEO) == "video-source"
    assert hit.require(BVP) == (0.1, 0.2)
    assert hit_source.calls == []

    invalidated_source = RecordingSampleSource([_sample("video-v2", [0.3])])
    invalidated = CachedSampleSource(
        invalidated_source,
        store,
        cache_context=CacheContext(invalidation={"source_checksum": "v2"}),
        context_factory=_context_factory,
        hit_loader=lambda entry: _sample(
            entry.value_token["video"],  # type: ignore[index]
            entry.value_token["bvp"],  # type: ignore[index]
        ),
    )

    refreshed = invalidated.sample_at(0, request=request)

    assert refreshed.require(VIDEO) == "video-v2"
    assert invalidated_source.calls == [0]
    assert invalidated.last_lookup is not None
    assert invalidated.last_lookup.status == "miss"


class RecordingSampleSource(SampleSource):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = samples
        self.calls: list[int] = []

    def __len__(self) -> int:
        return len(self.samples)

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        self.calls.append(position)
        return self.samples[position]


def _sample(video_payload: object, bvp_payload: object) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(video_payload, schema="video.rgb.v1"),
            BVP: FieldValue(bvp_payload, schema="signal.bvp.v1"),
        }
    )


def _context_factory(position: int, request: SampleRequest) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="stage9-cache-index",
        entry_id=f"stage9-cache-index:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=f"record-{position}",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        groups={"subject": "subject-001"},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        field_windows={
            "inputs/video.rgb": {"type": "full"},
            "targets/signal.bvp.reference": {"type": "full"},
        },
        request_fingerprint=request.fingerprint,
        metadata={"scope": "integration"},
    )
