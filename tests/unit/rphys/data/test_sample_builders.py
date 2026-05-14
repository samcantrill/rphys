from __future__ import annotations

import copy

import pytest

from rphys.data.containers import FieldContainer
from rphys.data.locators import FieldLocator
from rphys.data.sample_builders import (
    SampleBuildContext,
    SampleBuilder,
    SampleFieldProvenance,
    SampleProbeResult,
)
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.errors import FieldTypeError, MissingFieldError
from rphys.io.codecs import CodecRegistry
from tests.support.lazy_sample_builder_fixtures import (
    BVP,
    VIDEO,
    make_builder_fixture,
)
from tests.support.synthetic_codecs import SyntheticCodec


class CountingBuilder(SampleBuilder):
    def __init__(self, context: SampleBuildContext) -> None:
        super().__init__(context)
        self.make_calls = 0

    def _make_field(self, *args: object, **kwargs: object) -> SampleField:
        self.make_calls += 1
        return super()._make_field(*args, **kwargs)  # type: ignore[arg-type]


def test_build_context_and_builder_validate_explicit_registry_inputs() -> None:
    registry = CodecRegistry([SyntheticCodec(name="video")])
    source_metadata = {"builder": "unit"}
    context = SampleBuildContext(registry, metadata=source_metadata)
    source_metadata["builder"] = "mutated"

    assert context.registry is registry
    assert context.metadata == {"builder": "unit"}
    assert SampleBuilder(context).context is context
    assert SampleBuilder(registry=registry, metadata={"trace": "local"}).context.metadata[
        "trace"
    ] == "local"

    with pytest.raises(TypeError):
        hash(context)
    with pytest.raises(FieldTypeError):
        SampleBuildContext(object())  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError):
        SampleBuildContext(registry, metadata={1: "invalid"})  # type: ignore[dict-item]
    with pytest.raises(FieldTypeError):
        SampleBuilder()
    with pytest.raises(FieldTypeError):
        SampleBuilder(context, registry=registry)
    with pytest.raises(FieldTypeError):
        SampleBuilder(context, metadata={"trace": "ambiguous"})


def test_build_all_creates_lazy_fields_without_loading() -> None:
    fixture = make_builder_fixture()

    sample = fixture.builder.build(fixture.item)
    video_field = sample.field(VIDEO)
    bvp_field = sample.field(BVP)

    assert isinstance(sample, FieldContainer)
    assert isinstance(video_field, SampleField)
    assert isinstance(bvp_field, SampleField)
    assert video_field.state is SampleFieldState.UNLOADED
    assert bvp_field.state is SampleFieldState.UNLOADED
    assert fixture.video_codec.load_calls == 0
    assert fixture.bvp_codec.load_calls == 0
    assert sample.field_items() == ((VIDEO, video_field), (BVP, bvp_field))

    provenance = video_field.provenance
    assert isinstance(provenance, SampleFieldProvenance)
    assert provenance.locator == VIDEO
    assert provenance.field_view is fixture.item.fields[VIDEO]
    assert provenance.record is fixture.item.record
    assert provenance.item_metadata == fixture.item.metadata
    assert provenance.builder_metadata == {
        "builder": "stage-4-unit",
        "sample_scope": "one-item",
    }
    assert video_field.load_context.field_view is fixture.item.fields[VIDEO]
    assert video_field.load_context.metadata == provenance.builder_metadata
    assert not hasattr(video_field.load_context, "record")
    assert not hasattr(video_field.load_context, "index_item")
    assert not hasattr(video_field.load_context, "locator")


def test_build_subset_preserves_request_order_and_roles() -> None:
    fixture = make_builder_fixture()

    sample = fixture.builder.build(fixture.item, requested=[str(BVP), VIDEO])

    assert tuple(locator for locator, _ in sample.field_items()) == (BVP, VIDEO)
    assert sample.role("targets")[BVP] is sample.field(BVP)
    assert sample.role("inputs")[VIDEO] is sample.field(VIDEO)
    assert sample.field(BVP).provenance.locator.key == BVP.key
    assert sample.field(VIDEO).provenance.locator.key == VIDEO.key


def test_build_one_returns_handle_and_eager_uses_same_state_machine() -> None:
    fixture = make_builder_fixture()

    lazy_field = fixture.builder.build_one(fixture.item, VIDEO)
    eager_field = fixture.builder.build_one(fixture.item, VIDEO, eager=True)

    assert isinstance(lazy_field, SampleField)
    assert lazy_field.state is SampleFieldState.UNLOADED
    assert eager_field.state is SampleFieldState.LOADED
    assert eager_field.payload == ("f1", "f2")
    assert fixture.video_codec.load_calls == 1
    assert eager_field.eager_load() is eager_field.load_result
    assert fixture.video_codec.load_calls == 1


def test_missing_requested_locator_prevalidates_before_partial_output() -> None:
    fixture = make_builder_fixture()
    context = SampleBuildContext(fixture.registry)
    builder = CountingBuilder(context)
    missing = FieldLocator.parse("inputs/video.nir")

    with pytest.raises(MissingFieldError) as build_error:
        builder.build(fixture.item, requested=[VIDEO, missing])
    with pytest.raises(MissingFieldError) as probe_error:
        builder.probe(fixture.item, requested=[VIDEO, missing])

    assert build_error.value.context["missing"] == [str(missing)]
    assert probe_error.value.context["missing"] == [str(missing)]
    assert builder.make_calls == 0
    assert fixture.video_codec.probe_calls == 0
    assert fixture.video_codec.load_calls == 0


def test_duplicate_and_malformed_requested_locators_fail_loudly() -> None:
    fixture = make_builder_fixture()

    with pytest.raises(FieldTypeError) as duplicate:
        fixture.builder.build(fixture.item, requested=[VIDEO, str(VIDEO)])
    with pytest.raises(FieldTypeError):
        fixture.builder.build(fixture.item, requested=object())  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError):
        fixture.builder.build(fixture.item, requested=[])

    assert duplicate.value.context["duplicates"] == [str(VIDEO)]


def test_build_one_rejects_iterable_locator_inputs() -> None:
    fixture = make_builder_fixture()

    with pytest.raises(FieldTypeError) as exc_info:
        fixture.builder.build_one(fixture.item, [VIDEO, BVP])  # type: ignore[arg-type]

    assert exc_info.value.context["field"] == "locator"
    assert fixture.video_codec.load_calls == 0
    assert fixture.bvp_codec.load_calls == 0


def test_probe_returns_results_without_loading_payloads() -> None:
    fixture = make_builder_fixture()

    results = fixture.builder.probe(fixture.item, requested=[VIDEO, BVP])

    assert tuple(result.locator for result in results) == (VIDEO, BVP)
    assert all(isinstance(result, SampleProbeResult) for result in results)
    assert results[0].field_view is fixture.item.fields[VIDEO]
    assert results[0].provenance.record is fixture.item.record
    assert results[0].probe_result.metadata["resource_count"] == 2
    assert results[1].probe_result.field_spec is not None
    assert str(results[1].probe_result.field_spec.key) == "signal.bvp.reference"
    assert fixture.video_codec.probe_calls == 1
    assert fixture.bvp_codec.probe_calls == 1
    assert fixture.video_codec.load_calls == 0
    assert fixture.bvp_codec.load_calls == 0


def test_compound_ordered_resources_are_preserved_on_built_handles() -> None:
    fixture = make_builder_fixture()

    field = fixture.builder.build_one(fixture.item, VIDEO)

    assert field.provenance.field_view.field_ref.resources == fixture.video_resources
    assert field.load_context.field_view.field_ref.resources == fixture.video_resources
    assert [resource.uri for resource in field.provenance.field_view.field_ref.resources] == [
        "archive://dataset.zip#records/r001/video.bin",
        "archive://dataset.zip#records/r001/video.index.json",
    ]
    assert not hasattr(field.provenance, "member")
    assert not hasattr(field.provenance, "alignment")


def test_build_probe_and_eager_paths_do_not_mutate_descriptors() -> None:
    fixture = make_builder_fixture()
    item_before = fixture.item.to_dict()
    record_before = fixture.item.record.to_dict()

    sample = fixture.builder.build(fixture.item, eager=True)
    probe_results = fixture.builder.probe(fixture.item)

    assert sample.field(VIDEO).state is SampleFieldState.LOADED
    assert len(probe_results) == 2
    assert fixture.item.to_dict() == item_before
    assert fixture.item.record.to_dict() == record_before


def test_container_copy_preserves_built_field_provenance_without_loading() -> None:
    fixture = make_builder_fixture()
    sample = fixture.builder.build(fixture.item)
    field = sample.field(VIDEO)

    shallow = sample.shallow_copy()
    deep = sample.deep_copy()
    copied = copy.copy(field)

    assert shallow.field(VIDEO) is field
    assert deep.field(VIDEO) is not field
    assert deep.field(VIDEO).provenance is field.provenance
    assert copied.provenance is field.provenance
    assert fixture.video_codec.load_calls == 0


def test_map_tensors_preserves_built_field_handle_and_provenance() -> None:
    fixture = make_builder_fixture()
    sample = fixture.builder.build(fixture.item, requested=VIDEO)
    field = sample.field(VIDEO)
    provenance = field.provenance

    assert sample.map_tensors_(lambda value: value) is sample

    assert sample.field(VIDEO) is field
    assert field.provenance is provenance
    assert field.state is SampleFieldState.LOADED
    assert field.load_result is not None
    assert field.load_result.metadata["codec"] == "video"
    assert fixture.video_codec.load_calls == 1
