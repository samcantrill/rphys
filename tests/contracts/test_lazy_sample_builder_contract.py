from __future__ import annotations

import pytest

from rphys.data.containers import FieldContainer
from rphys.data.sample_fields import SampleFieldState
from rphys.errors import UnsupportedCodecIndexError
from rphys.io.indexes import TemporalIndexSlice
from tests.support.lazy_sample_builder_fixtures import (
    BVP,
    VIDEO,
    make_builder_fixture,
)


def test_lazy_sample_builder_contract_builds_and_loads_on_payload_demand() -> None:
    fixture = make_builder_fixture()

    sample = fixture.builder.build(fixture.item)
    field = sample.field(VIDEO)

    assert isinstance(sample, FieldContainer)
    assert field.state is SampleFieldState.UNLOADED
    assert fixture.video_codec.load_calls == 0

    assert sample.require(VIDEO, expected_type=tuple, schema="video.rgb.v1") == (
        "f1",
        "f2",
    )

    assert sample.field(VIDEO) is field
    assert field.state is SampleFieldState.LOADED
    assert field.load_result is not None
    assert field.load_result.metadata["codec"] == "video"
    assert field.provenance.record is fixture.item.record
    assert field.provenance.field_view is fixture.item.fields[VIDEO]
    assert fixture.video_codec.load_calls == 1


def test_lazy_sample_builder_contract_probes_without_loading() -> None:
    fixture = make_builder_fixture()

    results = fixture.builder.probe(fixture.item, requested=[VIDEO, BVP])

    assert tuple(result.locator for result in results) == (VIDEO, BVP)
    assert results[0].probe_result.field_spec is not None
    assert str(results[0].probe_result.field_spec.key) == "video.rgb"
    assert results[0].provenance.record is fixture.item.record
    assert results[1].provenance.field_view is fixture.item.fields[BVP]
    assert fixture.video_codec.probe_calls == 1
    assert fixture.bvp_codec.probe_calls == 1
    assert fixture.video_codec.load_calls == 0
    assert fixture.bvp_codec.load_calls == 0


def test_lazy_sample_builder_contract_eager_keeps_lazy_handles() -> None:
    fixture = make_builder_fixture()

    sample = fixture.builder.build(fixture.item, requested=[BVP, VIDEO], eager=True)

    bvp_field = sample.field(BVP)
    video_field = sample.field(VIDEO)
    assert tuple(locator for locator, _ in sample.field_items()) == (BVP, VIDEO)
    assert bvp_field.state is SampleFieldState.LOADED
    assert video_field.state is SampleFieldState.LOADED
    assert bvp_field.payload == (0.1, 0.2, 0.3)
    assert video_field.payload == ("f1", "f2")
    assert bvp_field.provenance.record is fixture.item.record
    assert video_field.provenance.record is fixture.item.record
    assert fixture.bvp_codec.load_calls == 1
    assert fixture.video_codec.load_calls == 1


def test_lazy_sample_builder_contract_preserves_compound_resource_order() -> None:
    fixture = make_builder_fixture()

    field = fixture.builder.build_one(fixture.item, VIDEO)

    assert field.provenance.field_view.field_ref.resources == fixture.video_resources
    assert [resource.uri for resource in field.load_context.field_view.field_ref.resources] == [
        "archive://dataset.zip#records/r001/video.bin",
        "archive://dataset.zip#records/r001/video.index.json",
    ]
    assert not hasattr(field.provenance, "member")
    assert not hasattr(field.provenance, "alignment")


def test_lazy_sample_builder_contract_unsupported_slice_fails_without_fallback() -> None:
    fixture = make_builder_fixture(video_index=TemporalIndexSlice(0, 4, 2))
    sample = fixture.builder.build(fixture.item)

    with pytest.raises(UnsupportedCodecIndexError):
        sample.require(VIDEO)

    assert fixture.video_codec.load_calls == 0
    assert sample.field(VIDEO).state is SampleFieldState.FAILED
