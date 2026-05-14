from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from rphys.data.collation import CollatePolicy
from rphys.data.fields import FieldSpec, FieldValue
from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.data.schemas import SchemaName
from rphys.data.types import DataType
from rphys.errors import InvalidDataKeyError, InvalidSchemaNameError


def test_field_spec_coerces_stage_1_vocabulary_and_compares_by_value() -> None:
    spec = FieldSpec("video.rgb", "video", "video.rgb.v1")

    assert spec == FieldSpec(
        DataKey("video.rgb"),
        DataType("video"),
        SchemaName("video.rgb.v1"),
    )
    assert isinstance(spec.key, DataKey)
    assert isinstance(spec.data_type, DataType)
    assert isinstance(spec.schema, SchemaName)


def test_field_spec_copy_and_deepcopy_preserve_value() -> None:
    spec = FieldSpec("signal.bvp.reference", "signal", "signal.bvp.v1")

    assert copy.copy(spec) == spec
    assert copy.deepcopy(spec) == spec


def test_field_spec_is_frozen_and_explicitly_unhashable() -> None:
    spec = FieldSpec("video.rgb", "video", "video.rgb.v1")

    with pytest.raises(FrozenInstanceError):
        spec.key = DataKey("signal.bvp.reference")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        spec.data_type = DataType("signal")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        spec.schema = SchemaName("signal.bvp.v1")  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(spec)


def test_field_spec_rejects_invalid_vocabulary_without_rich_fields() -> None:
    with pytest.raises(InvalidDataKeyError):
        FieldSpec("Video.RGB", "video", "video.rgb.v1")
    with pytest.raises(InvalidSchemaNameError):
        FieldSpec("video.rgb", "video", "video.rgb")

    spec = FieldSpec("video.rgb", "video")
    assert not hasattr(spec, "shape")
    assert not hasattr(spec, "dtype")
    assert not hasattr(spec, "sample_rate")


def test_field_value_uses_identity_equality_and_copies_metadata() -> None:
    payload = [1, 2, 3]
    metadata = {"source_id": {"path": "fixture"}}

    field_value = FieldValue(
        payload,
        schema="video.rgb.v1",
        metadata=metadata,
        collate_policy="list",
    )
    equivalent = FieldValue(
        payload,
        schema="video.rgb.v1",
        metadata=metadata,
        collate_policy=CollatePolicy.LIST,
    )

    assert field_value is not equivalent
    assert field_value != equivalent
    assert field_value.payload is payload
    assert field_value.schema == SchemaName("video.rgb.v1")
    assert field_value.metadata == {MetadataKey("source_id"): {"path": "fixture"}}
    assert field_value.metadata is not metadata
    assert field_value.collate_policy is CollatePolicy.LIST

    metadata["source_id"] = {"path": "mutated"}
    assert field_value.metadata[MetadataKey("source_id")] == {"path": "fixture"}


def test_field_value_shallow_copy_shares_payload_and_nested_metadata() -> None:
    nested = {"path": "fixture"}
    field_value = FieldValue(
        ["payload"],
        schema="video.rgb.v1",
        metadata={"source_id": nested},
    )

    copied = copy.copy(field_value)

    assert copied is not field_value
    assert copied.payload is field_value.payload
    assert copied.metadata is not field_value.metadata
    assert copied.metadata[MetadataKey("source_id")] is nested


def test_field_value_deepcopy_delegates_to_payload_and_metadata() -> None:
    field_value = FieldValue(
        [["payload"]],
        schema="video.rgb.v1",
        metadata={"source_id": {"path": "fixture"}},
    )

    copied = copy.deepcopy(field_value)

    assert copied is not field_value
    assert copied.payload == field_value.payload
    assert copied.payload is not field_value.payload
    assert copied.metadata == field_value.metadata
    assert copied.metadata is not field_value.metadata
    assert (
        copied.metadata[MetadataKey("source_id")]
        is not field_value.metadata[MetadataKey("source_id")]
    )
