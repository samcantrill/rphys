from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.data.schemas import SchemaName
from rphys.errors import (
    InvalidDataKeyError,
    InvalidFieldRefError,
    InvalidFieldViewError,
    InvalidSchemaNameError,
    UnsupportedFieldIndexError,
)
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


def _resource(uri: str = "file:///record/video.mp4") -> ResourceRef:
    return ResourceRef(uri, "file")


def test_field_ref_coerces_vocabulary_and_preserves_resource_order() -> None:
    first = _resource("file:///record/video.mp4")
    second = _resource("file:///record/video-sidecar.json")

    ref = FieldRef(
        "video.rgb",
        [first, second],
        schema="video.rgb.v1",
        metadata={"source_id": "fixture"},
    )

    assert ref.key == DataKey("video.rgb")
    assert ref.resources == (first, second)
    assert ref.schema == SchemaName("video.rgb.v1")
    assert ref.metadata == {MetadataKey("source_id"): "fixture"}
    assert not hasattr(ref, "member")
    assert not hasattr(ref, "role")
    assert not hasattr(ref, "field_index")


def test_field_ref_copies_and_freezes_metadata() -> None:
    metadata = {"source_id": {"record": "r001"}, "points": [1, 2]}
    ref = FieldRef("signal.bvp.reference", [_resource()], metadata=metadata)
    metadata["source_id"]["record"] = "mutated"
    metadata["points"].append(3)

    assert ref.to_dict()["metadata"] == {
        "source_id": {"record": "r001"},
        "points": [1, 2],
    }
    with pytest.raises(TypeError):
        ref.metadata[MetadataKey("source_id")] = "mutated"
    with pytest.raises(TypeError):
        ref.metadata[MetadataKey("source_id")]["record"] = "mutated"  # type: ignore[index]
    with pytest.raises(AttributeError):
        ref.metadata[MetadataKey("points")].append(3)  # type: ignore[attr-defined]


def test_field_ref_has_value_equality_without_public_hash_contract() -> None:
    ref = FieldRef("video.rgb", [_resource()], schema="video.rgb.v1")

    assert ref == FieldRef("video.rgb", [_resource()], schema="video.rgb.v1")
    with pytest.raises(FrozenInstanceError):
        ref.key = DataKey("signal.bvp.reference")  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(ref)


def test_field_ref_round_trips_through_primitive_dict() -> None:
    ref = FieldRef(
        "video.rgb",
        [ResourceRef("archive://dataset.zip#record/r001.mp4", "archive")],
        schema="video.rgb.v1",
        metadata={"source_id": "cam-1", "quality": {"usable": True}},
    )
    serialized = ref.to_dict()

    assert serialized == {
        "key": "video.rgb",
        "resources": [
            {
                "uri": "archive://dataset.zip#record/r001.mp4",
                "protocol": "archive",
                "storage_options": {},
            }
        ],
        "schema": "video.rgb.v1",
        "metadata": {"source_id": "cam-1", "quality": {"usable": True}},
    }
    assert FieldRef.from_dict(serialized) == ref
    assert "member" not in serialized
    assert "fingerprint" not in serialized


def test_field_ref_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidDataKeyError):
        FieldRef("Video.RGB", [_resource()])
    with pytest.raises(InvalidSchemaNameError):
        FieldRef("video.rgb", [_resource()], schema="video.rgb")
    with pytest.raises(InvalidFieldRefError):
        FieldRef("video.rgb", [])
    with pytest.raises(InvalidFieldRefError):
        FieldRef("video.rgb", ["file:///record.mp4"])  # type: ignore[list-item]
    with pytest.raises(InvalidFieldRefError):
        FieldRef("video.rgb", [_resource()], metadata={"source_id": object()})


def test_field_ref_from_dict_rejects_invalid_serialized_shapes() -> None:
    with pytest.raises(InvalidFieldRefError):
        FieldRef.from_dict({"key": "video.rgb", "resources": []})
    with pytest.raises(InvalidFieldRefError):
        FieldRef.from_dict(
            {
                "key": "video.rgb",
                "resources": [],
                "schema": None,
                "metadata": {},
                "schema_version": 1,
            }
        )


def test_field_view_binds_optional_field_native_index_without_role_or_alignment() -> None:
    field_ref = FieldRef("video.rgb", [_resource()], schema="video.rgb.v1")
    index = TemporalIndexSlice(0, 60, step=2)
    view = FieldView(field_ref, index)

    assert view.field_ref is field_ref
    assert view.field_index == index
    assert not hasattr(view, "role")
    assert not hasattr(view, "locator")
    assert not hasattr(view, "alignment")


def test_field_view_has_value_equality_without_public_hash_contract() -> None:
    view = FieldView(FieldRef("video.rgb", [_resource()]), TemporalIndexSlice(0, 1))

    assert view == FieldView(FieldRef("video.rgb", [_resource()]), TemporalIndexSlice(0, 1))
    with pytest.raises(FrozenInstanceError):
        view.field_index = None  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(view)


def test_field_view_round_trips_with_and_without_index() -> None:
    field_ref = FieldRef("signal.bvp.reference", [_resource()], schema="signal.bvp.v1")
    indexed = FieldView(field_ref, TemporalIndexSlice(10, 20, 2))
    full = FieldView(field_ref)

    assert FieldView.from_dict(indexed.to_dict()) == indexed
    assert FieldView.from_dict(full.to_dict()) == full
    assert indexed.to_dict()["field_index"] == {
        "type": "temporal_index_slice",
        "start": 10,
        "stop": 20,
        "step": 2,
    }
    assert full.to_dict()["field_index"] is None


def test_field_view_from_dict_fails_loudly_on_unknown_index_type() -> None:
    serialized = FieldView(FieldRef("video.rgb", [_resource()])).to_dict()
    serialized["field_index"] = {
        "type": "spatial_crop",
        "start": 0,
        "stop": 1,
        "step": 1,
    }

    with pytest.raises(UnsupportedFieldIndexError):
        FieldView.from_dict(serialized)


def test_field_view_rejects_invalid_components() -> None:
    with pytest.raises(InvalidFieldViewError):
        FieldView("video.rgb")  # type: ignore[arg-type]
    with pytest.raises(InvalidFieldViewError):
        FieldView(FieldRef("video.rgb", [_resource()]), field_index=object())  # type: ignore[arg-type]


def test_field_ref_and_field_view_have_no_loading_or_codec_hooks() -> None:
    ref = FieldRef("video.rgb", [_resource()])
    view = FieldView(ref, TemporalIndexSlice(0, 1))

    for descriptor in [ref, view]:
        for name in ["load", "save", "probe", "open", "build", "codec", "payload"]:
            assert not hasattr(descriptor, name)
