from __future__ import annotations

import pytest

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.prepared import (
    PreparedDataManifest,
    PreparedField,
    PreparedReadRequest,
    PreparedReadResult,
    PreparedSampleSource,
)
from rphys.datasources.sources import SampleRequest, SampleRuntimeContext
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO


def test_prepared_field_round_trips_and_validates_primitive_evidence() -> None:
    field = PreparedField(
        VIDEO,
        schema="video.rgb.v1",
        dtype="uint8",
        shape=(32, 32, 3),
        checksum="sha256:video",
        layout={"column": "video"},
        metadata={"unit": "pixel"},
    )

    loaded = PreparedField.from_dict(field.to_dict())

    assert loaded.locator == VIDEO
    assert loaded.shape == (32, 32, 3)
    assert loaded.fingerprint == field.fingerprint

    with pytest.raises(FieldTypeError):
        PreparedField(VIDEO, shape=(-1,))
    with pytest.raises(FieldTypeError):
        PreparedField(VIDEO, metadata={"bad": object()})


def test_prepared_manifest_round_trips_and_is_sensitive_to_equivalence_evidence() -> None:
    request = SampleRequest([VIDEO, BVP], operation_fingerprint={"op": "crop"})
    first = _manifest(request=request, invalidation={"source_checksum": "v1"})
    second = PreparedDataManifest.from_dict(first.to_dict())
    changed = _manifest(request=request, invalidation={"source_checksum": "v2"})

    assert second.fingerprint == first.fingerprint
    assert second.request_fingerprint == request.fingerprint
    assert second.field_locators == (VIDEO, BVP)
    assert first.fingerprint != changed.fingerprint


def test_prepared_manifest_rejects_duplicate_fields_and_bad_fingerprint() -> None:
    request = SampleRequest([VIDEO, BVP])

    with pytest.raises(FieldTypeError, match="unique"):
        _manifest(request=request, fields=[_prepared_field(VIDEO), _prepared_field(VIDEO)])

    data = _manifest(request=request).to_dict()
    data["fingerprint"] = "0" * 64
    with pytest.raises(RemotePhysDataSourceError, match="fingerprint mismatch"):
        PreparedDataManifest.from_dict(data)


def test_prepared_manifest_validates_request_and_context_equivalence() -> None:
    request = SampleRequest([VIDEO, BVP])
    manifest = _manifest(request=request)

    manifest.validate_request_context(request, _context(request), position=0)

    with pytest.raises(RemotePhysDataSourceError, match="does not match") as request_error:
        manifest.validate_request_context(SampleRequest(VIDEO), _context(SampleRequest(VIDEO)), position=0)
    assert "request_fingerprint" in request_error.value.context["mismatches"]

    wrong_source = _context(request, source_id="other-camera")
    with pytest.raises(RemotePhysDataSourceError, match="does not match") as source_error:
        manifest.validate_request_context(request, wrong_source, position=0)
    assert "source_id" in source_error.value.context["mismatches"]


def test_prepared_read_request_requires_matching_position_and_request_context() -> None:
    request = SampleRequest(VIDEO)
    manifest = _manifest(request=request, fields=[_prepared_field(VIDEO)])

    read_request = PreparedReadRequest(
        position=0,
        request=request,
        context=_context(request),
        manifest_fingerprint=manifest.fingerprint,
    )

    assert read_request.position == 0

    with pytest.raises(RemotePhysDataSourceError, match="position"):
        PreparedReadRequest(
            position=1,
            request=request,
            context=_context(request, position=0),
            manifest_fingerprint=manifest.fingerprint,
        )
    with pytest.raises(RemotePhysDataSourceError, match="request fingerprint"):
        PreparedReadRequest(
            position=0,
            request=request,
            context=_context(SampleRequest(BVP), position=0),
            manifest_fingerprint=manifest.fingerprint,
        )


def test_prepared_read_result_records_sample_and_field_locators() -> None:
    request = SampleRequest([VIDEO, BVP])
    manifest = _manifest(request=request)
    sample = _sample("video", [0.1])

    result = PreparedReadResult(
        sample=sample,
        manifest_fingerprint=manifest.fingerprint,
        backend_id=manifest.backend_id,
    )

    assert result.field_locators == (VIDEO, BVP)

    with pytest.raises(FieldTypeError):
        PreparedReadResult(
            sample=object(),  # type: ignore[arg-type]
            manifest_fingerprint=manifest.fingerprint,
            backend_id=manifest.backend_id,
        )


def test_prepared_sample_source_reads_all_and_subset_fields() -> None:
    request = SampleRequest()
    manifest = _manifest(request=request)
    reader = FakePreparedReader(manifest, [_sample("video", [0.1, 0.2])])
    source = PreparedSampleSource(manifest, reader)

    all_fields = source[0]
    subset = source.sample_at(0, request=SampleRequest(VIDEO))

    assert len(source) == 1
    assert all_fields.require(VIDEO) == "video"
    assert all_fields.require(BVP) == [0.1, 0.2]
    assert [str(locator) for locator, _ in subset.field_items()] == ["inputs/video.rgb"]


def test_prepared_sample_source_rejects_unproven_equivalence() -> None:
    request = SampleRequest([VIDEO, BVP])
    manifest = _manifest(request=request)
    source = PreparedSampleSource(
        manifest,
        FakePreparedReader(manifest, [_sample("video", [0.1])]),
    )

    with pytest.raises(RemotePhysDataSourceError, match="out of range"):
        source.sample_at(1, request=request)

    all_manifest = _manifest(request=SampleRequest())
    all_source = PreparedSampleSource(
        all_manifest,
        FakePreparedReader(all_manifest, [_sample("video", [0.1])]),
    )
    with pytest.raises(RemotePhysDataSourceError, match="does not contain requested fields"):
        all_source.sample_at(0, request="targets/signal.foo")
    with pytest.raises(RemotePhysDataSourceError, match="does not match"):
        source.sample_at(0, request=SampleRequest(VIDEO), context=_context(SampleRequest(VIDEO), source_id="other"))


def test_prepared_sample_source_validates_reader_manifest_and_results() -> None:
    request = SampleRequest([VIDEO, BVP])
    manifest = _manifest(request=request)
    other_manifest = _manifest(
        request=request,
        manifest_id="prepared-other",
        invalidation={"source_checksum": "other"},
    )

    with pytest.raises(RemotePhysDataSourceError, match="reader manifest"):
        PreparedSampleSource(manifest, FakePreparedReader(other_manifest, [_sample("video", [0.1])]))

    bad_reader = BadResultReader(manifest)
    source = PreparedSampleSource(manifest, bad_reader)
    with pytest.raises(RemotePhysDataSourceError, match="result"):
        source.sample_at(0, request=request)


class FakePreparedReader:
    def __init__(self, manifest: PreparedDataManifest, samples: list[Sample]) -> None:
        self.manifest = manifest
        self.samples = samples
        self.requests: list[PreparedReadRequest] = []

    def read(self, request: PreparedReadRequest) -> PreparedReadResult:
        self.requests.append(request)
        locators = self.manifest.expected_locators(request.request)
        return PreparedReadResult(
            sample=_subset(self.samples[request.position], locators),
            manifest_fingerprint=self.manifest.fingerprint,
            backend_id=self.manifest.backend_id,
            field_locators=locators,
            metadata={"reader": "fake"},
        )


class BadResultReader(FakePreparedReader):
    def __init__(self, manifest: PreparedDataManifest) -> None:
        super().__init__(manifest, [_sample("video", [0.1])])

    def read(self, request: PreparedReadRequest) -> PreparedReadResult:
        return PreparedReadResult(
            sample=_sample("video", [0.1]),
            manifest_fingerprint=self.manifest.fingerprint,
            backend_id="other-backend",
            field_locators=self.manifest.field_locators,
        )


def _prepared_field(locator=VIDEO) -> PreparedField:
    return PreparedField(
        locator,
        schema="video.rgb.v1" if locator == VIDEO else "signal.bvp.v1",
        dtype="uint8" if locator == VIDEO else "float32",
        shape=(32, 32, 3) if locator == VIDEO else (128,),
        checksum=f"sha256:{locator}",
        layout={"column": str(locator)},
    )


def _manifest(
    *,
    request: SampleRequest,
    manifest_id: str = "prepared-unit",
    fields: list[PreparedField] | None = None,
    invalidation: dict[str, object] | None = None,
) -> PreparedDataManifest:
    return PreparedDataManifest(
        manifest_id=manifest_id,
        backend_id="fake-prepared",
        index_id="prepared-index",
        datasource_id="synthetic-rphys",
        source_id="synthetic-camera",
        sample_count=1,
        request_fingerprint=request.fingerprint,
        operation_fingerprint=request.operation_fingerprint,
        materialization_fingerprint=request.materialization_fingerprint,
        fields=fields or [_prepared_field(VIDEO), _prepared_field(BVP)],
        split_counts={"train": 1},
        group_counts={"subject-001": 1},
        checksums={"manifest": "sha256:manifest"},
        layout={"format": "fake-table"},
        cost={"read_cost": 1},
        runtime={"python": "3.12"},
        invalidation=invalidation or {"source_checksum": "v1"},
        metadata={"scope": "unit"},
    )


def _context(
    request: SampleRequest,
    *,
    position: int = 0,
    source_id: str | None = "synthetic-camera",
) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="prepared-index",
        entry_id=f"prepared-index:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=f"record-{position}",
        datasource_id="synthetic-rphys",
        source_id=source_id,
        groups={"subject": "subject-001"},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        request_fingerprint=request.fingerprint,
        metadata={"scope": "unit"},
    )


def _sample(video_payload: object, bvp_payload: object) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(video_payload, schema="video.rgb.v1"),
            BVP: FieldValue(bvp_payload, schema="signal.bvp.v1"),
        }
    )


def _subset(sample: Sample, locators: tuple) -> Sample:
    return Sample({locator: sample.field(locator) for locator in locators})
