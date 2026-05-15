from __future__ import annotations

import json

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.cache import (
    CacheContext,
    CacheEntry,
    CacheKey,
    CacheManifest,
    CachePolicy,
    CachedSampleSource,
    LocalCacheStore,
)
from rphys.datasources.sources import SampleRequest, SampleRuntimeContext, SampleSource
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO


def test_cache_key_for_sample_is_deterministic_and_sensitive_to_evidence() -> None:
    request = SampleRequest(VIDEO, eager=True)
    context = _context(request)
    cache_context = CacheContext(
        operation_fingerprint={"op": "normalize", "version": 1},
        invalidation={"source_checksum": "abc"},
        metadata={"scope": "unit"},
    )

    first = CacheKey.for_sample(request, context, cache_context=cache_context)
    second = CacheKey.for_sample(request, context, cache_context=cache_context)
    request_changed = CacheKey.for_sample(
        SampleRequest(BVP, eager=True),
        _context(SampleRequest(BVP, eager=True)),
        cache_context=cache_context,
    )
    context_changed = CacheKey.for_sample(
        request,
        _context(request, position=1),
        cache_context=cache_context,
    )
    invalidation_changed = CacheKey.for_sample(
        request,
        context,
        cache_context=CacheContext(invalidation={"source_checksum": "changed"}),
    )

    assert first.digest == second.digest
    assert first.invalidation["source_checksum"] == "abc"
    assert len(first.digest) == 64
    assert first.digest != request_changed.digest
    assert first.digest != context_changed.digest
    assert first.digest != invalidation_changed.digest


def test_cache_key_for_sample_rejects_mismatched_request_context_evidence() -> None:
    request = SampleRequest(VIDEO)

    with pytest.raises(RemotePhysDataSourceError, match="request fingerprint"):
        CacheKey.for_sample(request, _context(SampleRequest(BVP)))


def test_cache_context_rejects_non_primitive_evidence() -> None:
    with pytest.raises(FieldTypeError):
        CacheContext(metadata={"bad": object()})


def test_cache_entry_records_invalidation_and_validates_checksum() -> None:
    entry = _entry(metadata={"field_count": 1})

    loaded = CacheEntry.from_dict(entry.to_dict())

    assert loaded.key.digest == entry.key.digest
    assert loaded.field_locators == (VIDEO,)
    assert loaded.invalidation == entry.invalidation
    assert loaded.metadata["field_count"] == 1

    tampered = entry.to_dict()
    tampered["status"] = "incomplete"
    with pytest.raises(RemotePhysDataSourceError, match="checksum mismatch"):
        CacheEntry.from_dict(tampered)


def test_cache_entry_rejects_mismatched_invalidation_evidence() -> None:
    key = _key(CacheContext(invalidation={"source_checksum": "expected"}))

    with pytest.raises(RemotePhysDataSourceError, match="invalidation"):
        CacheEntry(
            key=key,
            field_locators=[VIDEO],
            invalidation={"source_checksum": "other"},
        )


def test_cache_manifest_round_trips_and_rejects_corruption() -> None:
    entry = _entry()
    manifest = CacheManifest([entry])

    loaded = CacheManifest.loads(manifest.dumps())

    assert loaded.schema_version == 1
    assert loaded.entries[0].key.digest == entry.key.digest

    tampered = json.loads(manifest.dumps())
    tampered["entries"][0]["value_strategy"] = "other"
    with pytest.raises(RemotePhysDataSourceError, match="checksum mismatch"):
        CacheManifest.from_dict(tampered)


def test_local_cache_store_reports_miss_hit_incomplete_and_corrupt(tmp_path) -> None:
    store = LocalCacheStore(tmp_path)
    entry = _entry()

    assert store.lookup(entry.key).status == "miss"

    write = store.write(entry)
    assert write.written is True
    assert write.entry is entry

    hit = store.lookup(entry.key)
    assert hit.hit is True
    assert hit.entry is not None
    assert hit.entry.key.digest == entry.key.digest

    incomplete = CacheEntry(
        key=entry.key,
        status="incomplete",
        field_locators=[VIDEO],
        value_token={"uri": "local://pending"},
    )
    store.write(incomplete)
    incomplete_lookup = store.lookup(entry.key)
    assert incomplete_lookup.status == "incomplete"
    assert incomplete_lookup.entry is not None
    assert incomplete_lookup.entry.status == "incomplete"

    store.path_for(entry.key).write_text("{not-json", encoding="utf-8")
    corrupt = store.lookup(entry.key)
    assert corrupt.status == "corrupt"
    assert corrupt.entry is None


def test_cached_sample_source_writes_misses_and_loads_hits_through_explicit_loader(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    store = LocalCacheStore(tmp_path)
    source = RecordingSampleSource([_sample("source")])
    cached = CachedSampleSource(
        source,
        store,
        context_factory=_context_for_request,
        entry_factory=lambda sample, key: CacheEntry(
            key=key,
            field_locators=[VIDEO],
            value_token={"uri": sample.require(VIDEO)},
        ),
    )

    miss_sample = cached.sample_at(0, request=request)

    assert miss_sample.require(VIDEO) == "source"
    assert source.calls == [(0, request.fingerprint)]
    assert cached.last_lookup is not None
    assert cached.last_lookup.status == "miss"
    assert cached.last_write is not None
    assert cached.last_write.written is True

    hit_source = RecordingSampleSource([_sample("source-again")])
    hit_cached = CachedSampleSource(
        hit_source,
        store,
        context_factory=_context_for_request,
        hit_loader=lambda entry: _sample(entry.value_token["uri"]),  # type: ignore[index]
    )
    hit_sample = hit_cached.sample_at(0, request=request)

    assert hit_sample.require(VIDEO) == "source"
    assert hit_source.calls == []
    assert hit_cached.last_lookup is not None
    assert hit_cached.last_lookup.hit is True
    assert hit_cached.last_write is not None
    assert hit_cached.last_write.reason == "cache_hit"


def test_cached_sample_source_hit_without_loader_delegates_to_source(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    key = _key(request=request)
    store = LocalCacheStore(tmp_path)
    store.write(CacheEntry(key=key, field_locators=[VIDEO], value_token={"uri": "cached"}))
    source = RecordingSampleSource([_sample("source")])
    cached = CachedSampleSource(source, store, context_factory=_context_for_request)

    sample = cached.sample_at(0, request=request)

    assert sample.require(VIDEO) == "source"
    assert source.calls == [(0, request.fingerprint)]
    assert cached.last_lookup is not None
    assert cached.last_lookup.hit is True
    assert cached.last_write is not None
    assert cached.last_write.reason == "no_entry_factory"


def test_cached_sample_source_skips_cache_without_context_evidence(tmp_path) -> None:
    store = LocalCacheStore(tmp_path)
    source = RecordingSampleSource([_sample("source")])
    cached = CachedSampleSource(source, store)

    sample = cached.sample_at(0, request=SampleRequest(VIDEO))

    assert sample.require(VIDEO) == "source"
    assert list(tmp_path.iterdir()) == []
    assert cached.last_lookup is not None
    assert cached.last_lookup.status == "miss"
    assert cached.last_lookup.reason == "missing_context"
    assert cached.last_write is not None
    assert cached.last_write.reason == "missing_context"


def test_cached_sample_source_validates_strategy_results(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    store = LocalCacheStore(tmp_path)
    source = RecordingSampleSource([_sample("source")])

    bad_entry = CachedSampleSource(
        source,
        store,
        context_factory=_context_for_request,
        entry_factory=lambda sample, key: object(),  # type: ignore[return-value]
    )
    with pytest.raises(FieldTypeError, match="entry_factory"):
        bad_entry.sample_at(0, request=request)

    key = _key(request=request)
    store.write(CacheEntry(key=key, field_locators=[VIDEO], value_token={"uri": "cached"}))
    bad_loader = CachedSampleSource(
        RecordingSampleSource([_sample("source")]),
        store,
        context_factory=_context_for_request,
        hit_loader=lambda entry: object(),  # type: ignore[return-value]
    )
    with pytest.raises(FieldTypeError, match="hit_loader"):
        bad_loader.sample_at(0, request=request)


def test_cached_sample_source_rejects_mismatched_context_evidence(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    source = RecordingSampleSource([_sample("source")])
    cached = CachedSampleSource(source, LocalCacheStore(tmp_path))

    with pytest.raises(RemotePhysDataSourceError, match="position"):
        cached.sample_at(0, request=request, context=_context(request, position=1))

    with pytest.raises(RemotePhysDataSourceError, match="request fingerprint"):
        cached.sample_at(
            0,
            request=request,
            context=_context(SampleRequest(BVP), position=0),
        )


class RecordingSampleSource(SampleSource):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = samples
        self.calls: list[tuple[int, str]] = []

    def __len__(self) -> int:
        return len(self.samples)

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        resolved = SampleRequest.coerce(request)
        self.calls.append((position, resolved.fingerprint))
        return self.samples[position]


def _sample(video_payload: object) -> Sample:
    return Sample({VIDEO: FieldValue(video_payload, schema="video.rgb.v1")})


def _context_for_request(position: int, request: SampleRequest) -> SampleRuntimeContext:
    return _context(request, position=position)


def _context(request: SampleRequest, *, position: int = 0) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="cache-index",
        entry_id=f"cache-index:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=f"record-{position}",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        groups={"subject": "subject-001"},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        source_key="cache-unit",
        field_windows={"inputs/video.rgb": {"type": "full"}},
        request_fingerprint=request.fingerprint,
        metadata={"scope": "unit"},
    )


def _key(
    cache_context: CacheContext | None = None,
    *,
    request: SampleRequest | None = None,
) -> CacheKey:
    if request is None:
        request = SampleRequest(VIDEO)
    return CacheKey.for_sample(
        request,
        _context(request),
        cache_context=cache_context,
    )


def _entry(*, metadata: dict[str, object] | None = None) -> CacheEntry:
    key = _key()
    return CacheEntry(
        key=key,
        field_locators=[VIDEO],
        value_token={"uri": "local://cache/video"},
        metadata=metadata,
    )
