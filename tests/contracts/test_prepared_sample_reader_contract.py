from __future__ import annotations

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.prepared import (
    PreparedDataManifest,
    PreparedField,
    PreparedReadRequest,
    PreparedReadResult,
    PreparedSampleReader,
    PreparedSampleSource,
)
from rphys.datasources.sources import SampleRequest
from tests.support.lazy_sample_builder_fixtures import VIDEO


def test_prepared_sample_reader_is_public_provisional_protocol() -> None:
    request = SampleRequest()
    manifest = _manifest(request)
    reader = ContractReader(manifest, [_sample("prepared")])

    assert isinstance(reader, PreparedSampleReader)

    source = PreparedSampleSource(manifest, reader)
    sample = source.sample_at(0, request=SampleRequest(VIDEO))

    assert sample.require(VIDEO) == "prepared"
    assert reader.requests[0].manifest_fingerprint == manifest.fingerprint
    assert reader.requests[0].request.requested == (VIDEO,)


def test_prepared_manifest_contract_round_trips_equivalence_evidence() -> None:
    request = SampleRequest(operation_fingerprint={"pipeline": "v1"})
    manifest = _manifest(request)

    loaded = PreparedDataManifest.from_dict(manifest.to_dict())

    assert loaded.fingerprint == manifest.fingerprint
    assert loaded.request_fingerprint == request.fingerprint
    assert loaded.backend_id == "contract-reader"
    assert loaded.invalidation["source_checksum"] == "v1"


def test_prepared_source_contract_preserves_sample_shape_without_backend_semantics() -> None:
    request = SampleRequest()
    manifest = _manifest(request)
    reader = ContractReader(manifest, [_sample("prepared")])
    source = PreparedSampleSource(manifest, reader)

    sample = source[0]

    assert isinstance(sample, Sample)
    assert [locator for locator, _ in sample.field_items()] == [VIDEO]
    assert sample.require(VIDEO) == "prepared"


class ContractReader:
    def __init__(self, manifest: PreparedDataManifest, samples: list[Sample]) -> None:
        self.manifest = manifest
        self.samples = samples
        self.requests: list[PreparedReadRequest] = []

    def read(self, request: PreparedReadRequest) -> PreparedReadResult:
        self.requests.append(request)
        locators = self.manifest.expected_locators(request.request)
        return PreparedReadResult(
            sample=Sample({locator: self.samples[request.position].field(locator) for locator in locators}),
            manifest_fingerprint=self.manifest.fingerprint,
            backend_id=self.manifest.backend_id,
            field_locators=locators,
            metadata={"contract": "reader"},
        )


def _manifest(request: SampleRequest) -> PreparedDataManifest:
    return PreparedDataManifest(
        manifest_id="contract-prepared",
        backend_id="contract-reader",
        index_id="contract-index",
        datasource_id="synthetic-rphys",
        source_id="contract-camera",
        sample_count=1,
        request_fingerprint=request.fingerprint,
        operation_fingerprint=request.operation_fingerprint,
        fields=[
            PreparedField(
                VIDEO,
                schema="video.rgb.v1",
                dtype="uint8",
                shape=(16, 16, 3),
                checksum="sha256:video",
            )
        ],
        split_counts={"train": 1},
        invalidation={"source_checksum": "v1"},
    )


def _sample(payload: object) -> Sample:
    return Sample({VIDEO: FieldValue(payload, schema="video.rgb.v1")})
