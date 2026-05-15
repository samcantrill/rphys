from __future__ import annotations

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.cache import (
    CacheEntry,
    CacheKey,
    CacheManifest,
    CachedSampleSource,
    LocalCacheStore,
)
from rphys.datasources.sources import SampleRequest, SampleRuntimeContext, SampleSource
from tests.support.lazy_sample_builder_fixtures import VIDEO


def test_cache_records_round_trip_as_versioned_primitive_manifest() -> None:
    request = SampleRequest(VIDEO)
    key = CacheKey.for_sample(request, _context(request))
    entry = CacheEntry(
        key=key,
        field_locators=[VIDEO],
        value_strategy="explicit-test-token",
        value_token={"uri": "cache://record-001/video"},
        metadata={"scope": "contract"},
    )

    loaded = CacheManifest.loads(CacheManifest([entry]).dumps())

    assert loaded.schema_version == 1
    assert loaded.entries[0].key.digest == key.digest
    assert loaded.entries[0].value_strategy == "explicit-test-token"
    assert loaded.entries[0].value_token == {"uri": "cache://record-001/video"}
    assert loaded.entries[0].metadata["scope"] == "contract"


def test_local_cache_store_contract_returns_result_records_for_ordinary_cache_state(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    key = CacheKey.for_sample(request, _context(request))
    store = LocalCacheStore(tmp_path)

    assert store.lookup(key).status == "miss"

    incomplete = CacheEntry(key=key, status="incomplete", field_locators=[VIDEO])
    assert store.write(incomplete).written is True
    incomplete_lookup = store.lookup(key)
    assert incomplete_lookup.status == "incomplete"
    assert incomplete_lookup.entry is not None

    store.path_for(key).write_text("not json", encoding="utf-8")
    corrupt_lookup = store.lookup(key)
    assert corrupt_lookup.status == "corrupt"
    assert corrupt_lookup.entry is None


def test_cached_sample_source_contract_requires_explicit_hit_loader(tmp_path) -> None:
    request = SampleRequest(VIDEO)
    store = LocalCacheStore(tmp_path)
    key = CacheKey.for_sample(request, _context(request))
    store.write(CacheEntry(key=key, field_locators=[VIDEO], value_token={"payload": "cached"}))

    delegate_source = RecordingSampleSource([_sample("delegate")])
    no_loader = CachedSampleSource(
        delegate_source,
        store,
        context_factory=_context_factory,
    )
    delegated = no_loader.sample_at(0, request=request)

    assert delegated.require(VIDEO) == "delegate"
    assert delegate_source.calls == [0]
    assert no_loader.last_lookup is not None
    assert no_loader.last_lookup.hit is True

    hit_source = RecordingSampleSource([_sample("delegate")])
    with_loader = CachedSampleSource(
        hit_source,
        store,
        context_factory=_context_factory,
        hit_loader=lambda entry: _sample(entry.value_token["payload"]),  # type: ignore[index]
    )
    loaded = with_loader.sample_at(0, request=request)

    assert loaded.require(VIDEO) == "cached"
    assert hit_source.calls == []


class RecordingSampleSource(SampleSource):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = samples
        self.calls: list[int] = []

    def __len__(self) -> int:
        return len(self.samples)

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        self.calls.append(position)
        return self.samples[position]


def _sample(payload: object) -> Sample:
    return Sample({VIDEO: FieldValue(payload, schema="video.rgb.v1")})


def _context_factory(position: int, request: SampleRequest) -> SampleRuntimeContext:
    return _context(request, position=position)


def _context(request: SampleRequest, *, position: int = 0) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="cache-contract-index",
        entry_id=f"cache-contract-index:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=f"record-{position}",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        request_fingerprint=request.fingerprint,
    )
