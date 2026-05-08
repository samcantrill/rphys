"""Tests for minimal field declarations and loaded value wrappers."""

from __future__ import annotations

from copy import copy, deepcopy

import pytest

from rphys.data import CollatePolicy, DataKey, FieldSpec, FieldValue
from rphys.errors import RemotePhysDataError


def test_field_spec_normalizes_key_and_preserves_minimal_contract() -> None:
    spec = FieldSpec(key="video.rgb", data_type="video", schema="rgb_video.v1")

    assert spec.key == DataKey("video.rgb")
    assert isinstance(spec.key, DataKey)
    assert spec.data_type == "video"
    assert spec.schema == "rgb_video.v1"
    assert not hasattr(spec, "description")
    assert not hasattr(spec, "runtime_type")
    assert not hasattr(spec, "coordinate_frame")
    assert not hasattr(spec, "temporal_axis")
    assert not hasattr(spec, "units")


def test_field_spec_uses_value_equality_but_is_not_hashable() -> None:
    left = FieldSpec(key="signal.bvp", data_type="signal", schema="bvp.v1")
    right = FieldSpec(key=DataKey("signal.bvp"), data_type="signal", schema="bvp.v1")
    different = FieldSpec(key="signal.ecg", data_type="signal", schema="ecg.v1")

    assert left == right
    assert left != different
    with pytest.raises(TypeError):
        hash(left)
    assert copy(left) == left
    assert deepcopy(left) == left


@pytest.mark.parametrize(
    "data_type",
    ("", "Video", "video type", ".video", "video.", "video..rgb", "video-raw"),
)
def test_field_spec_rejects_invalid_data_type_strings(data_type: str) -> None:
    with pytest.raises(RemotePhysDataError):
        FieldSpec(key="video.rgb", data_type=data_type)


def test_field_spec_rejects_non_string_data_type_and_invalid_schema() -> None:
    with pytest.raises(RemotePhysDataError):
        FieldSpec(key="video.rgb", data_type=object())  # type: ignore[arg-type]

    with pytest.raises(RemotePhysDataError):
        FieldSpec(key="video.rgb", data_type="video", schema="")

    with pytest.raises(RemotePhysDataError):
        FieldSpec(key="video.rgb", data_type="video", schema=" padded ")


def test_field_spec_rejects_extra_contract_fields() -> None:
    with pytest.raises(TypeError):
        FieldSpec(  # type: ignore[call-arg]
            key="video.rgb",
            data_type="video",
            description="not part of the base contract",
        )


def test_field_value_wraps_payload_with_schema_metadata_and_policy() -> None:
    payload = object()
    metadata = {"sample_rate": 30.0}
    value = FieldValue(
        payload,
        schema="rgb_video.v1",
        metadata=metadata,
        collate_policy=CollatePolicy.LIST,
    )

    assert value.value is payload
    assert value.schema == "rgb_video.v1"
    assert value.metadata == {"sample_rate": 30.0}
    assert value.metadata is not metadata
    assert value.collate_policy is CollatePolicy.LIST
    assert not hasattr(value, "data_type")


def test_field_value_defaults_are_narrow_and_explicit() -> None:
    payload = object()
    value = FieldValue(payload)

    assert value.value is payload
    assert value.schema is None
    assert value.metadata == {}
    assert value.collate_policy is None


def test_field_value_uses_identity_equality_and_is_not_hashable() -> None:
    class PayloadWithExplodingEquality:
        def __eq__(self, other: object) -> bool:
            raise AssertionError("payload equality should not be called")

    payload = PayloadWithExplodingEquality()
    left = FieldValue(payload)
    right = FieldValue(payload)

    assert left == left
    assert left != right
    with pytest.raises(TypeError):
        hash(left)


def test_field_value_copies_metadata_shallowly_on_construction() -> None:
    nested: list[str] = []
    metadata = {"nested": nested}

    value = FieldValue("payload", metadata=metadata)
    metadata["added"] = True

    assert value.metadata == {"nested": nested}
    assert value.metadata["nested"] is nested


def test_field_value_copy_and_deepcopy_contracts() -> None:
    payload = {"frames": [1, 2, 3]}
    nested_metadata = {"shape": [3]}
    value = FieldValue(
        payload,
        schema="video_payload.v1",
        metadata={"nested": nested_metadata},
        collate_policy=CollatePolicy.LIST,
    )

    shallow = copy(value)
    deep = deepcopy(value)

    assert shallow is not value
    assert shallow.value is payload
    assert shallow.metadata is not value.metadata
    assert shallow.metadata["nested"] is nested_metadata
    assert shallow.collate_policy is CollatePolicy.LIST

    assert deep is not value
    assert deep.value == payload
    assert deep.value is not payload
    assert deep.metadata == value.metadata
    assert deep.metadata["nested"] is not nested_metadata
    assert deep.collate_policy is CollatePolicy.LIST


def test_field_value_rejects_invalid_schema_metadata_and_policy() -> None:
    with pytest.raises(RemotePhysDataError):
        FieldValue("payload", schema="")

    with pytest.raises(RemotePhysDataError):
        FieldValue("payload", metadata=None)  # type: ignore[arg-type]

    with pytest.raises(RemotePhysDataError):
        FieldValue("payload", metadata={1: "not a string key"})  # type: ignore[dict-item]

    with pytest.raises(RemotePhysDataError):
        FieldValue("payload", collate_policy="list")  # type: ignore[arg-type]


def test_only_list_collate_policy_is_exposed() -> None:
    assert list(CollatePolicy) == [CollatePolicy.LIST]
    assert CollatePolicy.LIST.name == "LIST"
    assert CollatePolicy.LIST.value == "list"
    assert CollatePolicy("list") is CollatePolicy.LIST
    assert CollatePolicy.LIST == CollatePolicy.LIST
    assert hash(CollatePolicy.LIST) == hash(CollatePolicy.LIST)
    assert copy(CollatePolicy.LIST) is CollatePolicy.LIST
    assert deepcopy(CollatePolicy.LIST) is CollatePolicy.LIST
