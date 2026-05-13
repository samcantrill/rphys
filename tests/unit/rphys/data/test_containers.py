from __future__ import annotations

from collections.abc import Mapping

import pytest

from rphys.data.collation import CollatePolicy
from rphys.data.containers import Batch, Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator, FieldRole
from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError


class MappedPayload:
    def __init__(self, value: str) -> None:
        self.value = value

    def map_tensors(self, mapper):
        self.value = mapper(self.value)
        return self


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
PREDICTION = FieldLocator.parse("predictions/signal.bvp")


@pytest.mark.parametrize("container_type", [Sample, Batch])
def test_container_accessors_return_wrapper_or_payload(container_type) -> None:
    field_value = FieldValue(
        [1, 2, 3],
        schema="signal.bvp.v1",
        collate_policy=CollatePolicy.LIST,
    )
    container = container_type({BVP: field_value})

    assert container.has(BVP)
    assert container.has(str(BVP))
    assert container.field(BVP) is field_value
    assert container.get(BVP) == [1, 2, 3]
    assert container.require(BVP, expected_type=list, schema="signal.bvp.v1") == [1, 2, 3]


@pytest.mark.parametrize("container_type", [Sample, Batch])
def test_container_mutation_wraps_payloads_and_renames_preserving_field_value(
    container_type,
) -> None:
    container = container_type()
    container.set_field(VIDEO, "payload", schema="video.rgb.v1")
    field_value = container.field(VIDEO)

    assert field_value.payload == "payload"
    assert field_value.schema == "video.rgb.v1"

    assert container.rename_field(VIDEO, PREDICTION) is container
    assert container.field(PREDICTION) is field_value
    assert not container.has(VIDEO)

    removed = container.delete_field(PREDICTION)
    assert removed is field_value
    assert not container.has(PREDICTION)


def test_sample_and_batch_are_distinct_public_classes_with_api_parity() -> None:
    sample = Sample()
    batch = Batch()

    assert not isinstance(batch, Sample)
    for method_name in [
        "has",
        "field",
        "get",
        "require",
        "set_field",
        "delete_field",
        "rename_field",
        "role",
        "shallow_copy",
        "deep_copy",
        "map_tensors_",
    ]:
        assert hasattr(sample, method_name)
        assert hasattr(batch, method_name)


def test_role_returns_read_only_shallow_mapping_snapshot() -> None:
    target_value = FieldValue([0.1], schema="signal.bvp.v1")
    sample = Sample(
        {
            VIDEO: FieldValue("video", schema="video.rgb.v1"),
            BVP: target_value,
        }
    )

    targets = sample.role(FieldRole.TARGETS)

    assert isinstance(targets, Mapping)
    assert list(targets) == [BVP]
    assert targets[BVP] is target_value
    with pytest.raises(TypeError):
        targets[BVP] = FieldValue("mutated")  # type: ignore[index]

    sample.delete_field(BVP)
    assert targets[BVP] is target_value


def test_shallow_and_deep_copy_have_explicit_aliasing_semantics() -> None:
    payload = [["sample"]]
    sample = Sample({VIDEO: FieldValue(payload, schema="video.rgb.v1")})

    shallow = sample.shallow_copy()
    deep = sample.deep_copy()

    assert shallow is not sample
    assert shallow.field(VIDEO) is sample.field(VIDEO)
    assert deep is not sample
    assert deep.field(VIDEO) is not sample.field(VIDEO)
    assert deep.require(VIDEO) == payload
    assert deep.require(VIDEO) is not payload


def test_map_tensors_delegates_only_to_payloads_with_tensor_mapping() -> None:
    sample = Sample(
        {
            VIDEO: FieldValue(MappedPayload("video")),
            BVP: FieldValue("plain"),
        }
    )

    returned = sample.map_tensors_(lambda value: f"{value}:mapped")

    assert returned is sample
    assert sample.require(VIDEO).value == "video:mapped"
    assert sample.require(BVP) == "plain"


def test_missing_type_and_schema_failures_are_typed() -> None:
    sample = Sample({BVP: FieldValue([0.1], schema="signal.bvp.v1")})

    with pytest.raises(MissingFieldError) as missing:
        sample.require(VIDEO)
    assert missing.value.context["locator"] == str(VIDEO)

    with pytest.raises(FieldTypeError) as wrong_type:
        sample.require(BVP, expected_type=str)
    assert wrong_type.value.context["expected"] == "str"

    with pytest.raises(FieldSchemaError) as wrong_schema:
        sample.require(BVP, schema="signal.ppg.v1")
    assert wrong_schema.value.context["expected"] == "signal.ppg.v1"
