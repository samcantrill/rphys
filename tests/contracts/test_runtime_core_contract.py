from __future__ import annotations

import pytest

import rphys.data as data
from rphys.data.collation import CollatePolicy, collate_samples
from rphys.data.containers import Sample
from rphys.data.contracts import FieldRequirement, SampleContract
from rphys.data.fields import FieldSpec, FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.data.objects import CompositeDataObjectBase, DataObjectBase
from rphys.errors import CollatePolicyError, MissingFieldError


class TensorLeaf:
    def __init__(self, value: str) -> None:
        self.value = value

    def to(self, device: str) -> "TensorLeaf":
        return TensorLeaf(f"{self.value}:{device}")


class VideoObject(DataObjectBase):
    tensor_fields = ("tensor",)

    def __init__(self, tensor: TensorLeaf) -> None:
        self.tensor = tensor


class VideoWithLandmarks(CompositeDataObjectBase):
    child_fields = ("video", "landmarks")

    def __init__(self, video: VideoObject, landmarks: VideoObject) -> None:
        self.video = video
        self.landmarks = landmarks


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


def test_loaded_video_field_contract_example() -> None:
    spec = FieldSpec("video.rgb", "video", "video.rgb.v1")
    payload = object()
    value = FieldValue(
        payload,
        schema="video.rgb.v1",
        metadata={"source_id": "fixture"},
        collate_policy=None,
    )

    assert spec.key == "video.rgb"
    assert spec.data_type == "video"
    assert spec.schema == "video.rgb.v1"
    assert value.payload is payload
    assert value.metadata[MetadataKey("source_id")] == "fixture"


def test_sample_access_and_contract_validation_contract_example() -> None:
    sample = Sample(
        {
            VIDEO: FieldValue([], schema="video.rgb.v1"),
            BVP: FieldValue([0.2, 0.3], schema="signal.bvp.v1"),
        }
    )
    contract = SampleContract(
        required=[
            FieldRequirement(VIDEO, expected_type=list, schema="video.rgb.v1"),
            FieldRequirement(BVP, expected_type=list, schema="signal.bvp.v1"),
        ]
    )

    assert sample.require(BVP) == [0.2, 0.3]
    assert contract.validate(sample) is sample
    assert isinstance(sample, data.FieldContainer)
    assert sample.field_items() == ((VIDEO, sample.field(VIDEO)), (BVP, sample.field(BVP)))

    with pytest.raises(MissingFieldError):
        contract.validate(Sample({VIDEO: FieldValue([], schema="video.rgb.v1")}))


def test_list_collation_contract_example_preserves_sparse_metadata() -> None:
    batch = collate_samples(
        [
            Sample(
                {
                    VIDEO: FieldValue(
                        "a",
                        schema="video.rgb.v1",
                        metadata={"subject_id": "s1"},
                        collate_policy=CollatePolicy.LIST,
                    )
                }
            ),
            Sample(
                {
                    VIDEO: FieldValue(
                        "b",
                        schema="video.rgb.v1",
                        metadata={"source_id": "record-1"},
                        collate_policy="list",
                    )
                }
            ),
        ]
    )

    field_value = batch.field(VIDEO)
    assert field_value.payload == ["a", "b"]
    assert field_value.metadata[MetadataKey("source_id")] == [None, "record-1"]
    assert field_value.metadata[MetadataKey("subject_id")] == ["s1", None]


def test_implicit_or_unsupported_collation_is_rejected_contract_example() -> None:
    with pytest.raises(CollatePolicyError):
        collate_samples(
            [
                Sample({VIDEO: FieldValue("a", schema="video.rgb.v1")}),
                Sample({VIDEO: FieldValue("b", schema="video.rgb.v1")}),
            ]
        )


def test_data_object_traversal_contract_examples_are_local_and_structural() -> None:
    video = VideoObject(TensorLeaf("video"))
    landmarks = VideoObject(TensorLeaf("landmarks"))
    composite = VideoWithLandmarks(video, landmarks)

    assert video.to("cpu") is video
    assert video.tensor.value == "video:cpu"
    assert composite.to("cuda") is composite
    assert composite.video.tensor.value == "video:cpu:cuda"
    assert composite.landmarks.tensor.value == "landmarks:cuda"


def test_data_package_contract_does_not_export_private_helpers_or_stage_1_vocab() -> None:
    assert "FieldSpec" in data.__all__
    assert "FieldLocator" not in data.__all__
    assert "_FieldEntry" not in data.__all__
    assert "_RoleView" not in data.__all__
    assert "_ValidatorStep" not in data.__all__
