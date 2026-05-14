from __future__ import annotations

import pytest

from rphys.data.fields import FieldValue
from rphys.errors import (
    CodecDependencyError,
    CodecResolutionError,
    UnsupportedCodecIndexError,
)
from rphys.io.codecs import CodecRegistry, LoadContext, MetadataSavePolicy, SaveContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef
from tests.support.synthetic_codecs import SyntheticCodec


def _field_ref(
    key: str = "video.rgb",
    resources: tuple[ResourceRef, ...] | None = None,
) -> FieldRef:
    return FieldRef(
        key,
        resources
        or (
            ResourceRef("file:///records/r001/video.bin", "file"),
            ResourceRef("file:///records/r001/video.json", "file"),
        ),
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )


def test_codec_registry_probes_without_loading_payload() -> None:
    codec = SyntheticCodec(name="video", payload=("f0", "f1", "f2"))
    registry = CodecRegistry([codec])
    context = LoadContext(FieldView(_field_ref()))

    result = registry.probe(context)

    assert result.field_spec is not None
    assert str(result.field_spec.key) == "video.rgb"
    assert result.metadata["resource_count"] == 2
    assert codec.probe_calls == 1
    assert codec.load_calls == 0


def test_codec_registry_loads_supported_field_native_slice_only() -> None:
    codec = SyntheticCodec(name="video", payload=("f0", "f1", "f2", "f3"))
    registry = CodecRegistry([codec])

    result = registry.load(
        LoadContext(FieldView(_field_ref(), TemporalIndexSlice(1, 3)))
    )

    assert result.field_value.payload == ("f1", "f2")

    with pytest.raises(UnsupportedCodecIndexError):
        registry.load(
            LoadContext(FieldView(_field_ref(), TemporalIndexSlice(0, 4, 2)))
        )
    assert codec.load_calls == 1


def test_codec_registry_save_uses_explicit_field_ref_target() -> None:
    resources = (
        ResourceRef("file:///derived/video.bin", "file"),
        ResourceRef("file:///derived/video.json", "file"),
    )
    target = _field_ref(resources=resources)
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry([codec])
    value = FieldValue(
        "payload",
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )

    reference_only = registry.save(value, SaveContext(target))
    include_metadata = registry.save(
        value,
        SaveContext(
            target,
            metadata_policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA,
        ),
    )

    assert reference_only.target is target
    assert reference_only.resources == resources
    assert "field_metadata" not in reference_only.metadata
    assert include_metadata.metadata["field_metadata"] == {
        "source_id": "camera-front"
    }
    assert codec.saved[0][1].target is target


def test_codec_registry_failure_matrix_is_typed_and_inspectable() -> None:
    context = LoadContext(FieldView(_field_ref()))

    with pytest.raises(CodecResolutionError):
        CodecRegistry().probe(context)

    with pytest.raises(CodecResolutionError) as missing:
        CodecRegistry([SyntheticCodec(name="other", key="signal.bvp.reference")]).probe(
            context
        )
    assert missing.value.context["field_key"] == "video.rgb"

    with pytest.raises(CodecResolutionError) as ambiguous:
        CodecRegistry([SyntheticCodec(name="a"), SyntheticCodec(name="b")]).load(
            context
        )
    assert ambiguous.value.context["matches"] == ["0:a", "1:b"]

    unavailable = CodecRegistry(
        [SyntheticCodec(name="video", dependency_available=False)]
    )
    with pytest.raises(CodecDependencyError) as dependency:
        unavailable.load(context)
    assert dependency.value.context["operation"] == "load"


def test_compound_ordered_resources_are_preserved_without_member_semantics() -> None:
    resources = (
        ResourceRef("archive://dataset.zip#records/r001/video.bin", "archive"),
        ResourceRef("archive://dataset.zip#records/r001/video.index.json", "archive"),
    )
    target = _field_ref(resources=resources)
    codec = SyntheticCodec(name="video")

    result = CodecRegistry([codec]).save(
        FieldValue("payload", schema="video.rgb.v1"),
        SaveContext(target),
    )

    assert result.resources == resources
    assert [resource.uri for resource in result.resources] == [
        "archive://dataset.zip#records/r001/video.bin",
        "archive://dataset.zip#records/r001/video.index.json",
    ]
    assert not hasattr(result, "member")
    assert not hasattr(result, "alignment")
