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
from rphys.errors import RemotePhysDataSourceError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO


def test_stage9_prepared_source_flow_validates_manifest_equivalence_and_fake_reader() -> None:
    manifest = _manifest(SampleRequest())
    reader = FakePreparedReader(
        manifest,
        [
            _sample("video-0", [0.1, 0.2]),
            _sample("video-1", [0.3, 0.4]),
        ],
    )
    source = PreparedSampleSource(manifest, reader)

    all_fields = source[1]
    subset = source.sample_at(0, request=SampleRequest(VIDEO))

    assert all_fields.require(VIDEO) == "video-1"
    assert all_fields.require(BVP) == [0.3, 0.4]
    assert subset.require(VIDEO) == "video-0"
    assert [str(locator) for locator, _ in subset.field_items()] == ["inputs/video.rgb"]
    assert [request.position for request in reader.requests] == [1, 0]

    with pytest.raises(RemotePhysDataSourceError, match="does not match"):
        source.sample_at(
            0,
            request=SampleRequest(VIDEO),
            context=_context(SampleRequest(VIDEO), datasource_id="other-datasource"),
        )


class FakePreparedReader:
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
            metadata={"reader": "fake-integration"},
        )


def _manifest(request: SampleRequest) -> PreparedDataManifest:
    return PreparedDataManifest(
        manifest_id="integration-prepared",
        backend_id="fake-integration-reader",
        index_id="integration-index",
        datasource_id="synthetic-rphys",
        source_id="integration-camera",
        sample_count=2,
        request_fingerprint=request.fingerprint,
        fields=[
            PreparedField(
                VIDEO,
                schema="video.rgb.v1",
                dtype="uint8",
                shape=(64, 64, 3),
                checksum="sha256:video",
                layout={"column": "video"},
            ),
            PreparedField(
                BVP,
                schema="signal.bvp.v1",
                dtype="float32",
                shape=(128,),
                checksum="sha256:bvp",
                layout={"column": "bvp"},
            ),
        ],
        split_counts={"train": 2},
        group_counts={"subject-001": 2},
        checksums={"manifest": "sha256:manifest"},
        layout={"format": "fake-table", "shards": 1},
        cost={"read_cost": 1},
        runtime={"python": "3.12"},
        invalidation={"source_checksum": "v1"},
        metadata={"scope": "integration"},
    )


def _context(
    request: SampleRequest,
    *,
    datasource_id: str = "synthetic-rphys",
) -> SampleRuntimeContext:
    return SampleRuntimeContext(
        index_id="integration-index",
        entry_id="integration-index:0",
        position=0,
        candidate_id="candidate-0",
        record_id="record-0",
        datasource_id=datasource_id,
        source_id="integration-camera",
        groups={"subject": "subject-001"},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        request_fingerprint=request.fingerprint,
        metadata={"scope": "integration"},
    )


def _sample(video_payload: object, bvp_payload: object) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(video_payload, schema="video.rgb.v1"),
            BVP: FieldValue(bvp_payload, schema="signal.bvp.v1"),
        }
    )
