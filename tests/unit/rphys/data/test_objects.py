from __future__ import annotations

import pytest

from rphys.data.objects import CompositeDataObjectBase, DataObjectBase
from rphys.errors import RemotePhysDataError


class FakeTensor:
    def __init__(self, value: str) -> None:
        self.value = value

    def to(self, device: str) -> "FakeTensor":
        return FakeTensor(f"{self.value}:to:{device}")

    def detach(self) -> "FakeTensor":
        return FakeTensor(f"{self.value}:detach")

    def pin_memory(self) -> "FakeTensor":
        return FakeTensor(f"{self.value}:pin")


class LeafObject(DataObjectBase):
    tensor_fields = ("tensor",)

    def __init__(self, tensor: object) -> None:
        self.tensor = tensor
        self.untracked = FakeTensor("untracked")


class CompositeObject(CompositeDataObjectBase):
    child_fields = ("video", "landmarks")

    def __init__(self, video: DataObjectBase, landmarks: DataObjectBase) -> None:
        self.video = video
        self.landmarks = landmarks


def test_data_object_base_defaults_are_noop_and_return_self() -> None:
    base = DataObjectBase()

    assert base.validate() is base
    assert base.map_tensors(lambda tensor: tensor) is base
    assert base.to("cpu") is base
    assert base.detach() is base
    assert base.pin_memory() is base


def test_declared_tensor_leaves_are_mapped_without_arbitrary_attribute_walking() -> None:
    payload = LeafObject(FakeTensor("video"))

    returned = payload.map_tensors(lambda tensor: FakeTensor(f"{tensor.value}:mapped"))

    assert returned is payload
    assert payload.tensor.value == "video:mapped"
    assert payload.untracked.value == "untracked"


def test_device_detach_and_pin_helpers_use_declared_leaf_methods() -> None:
    payload = LeafObject(FakeTensor("video"))

    assert payload.to("cuda") is payload
    assert payload.tensor.value == "video:to:cuda"

    assert payload.detach() is payload
    assert payload.tensor.value == "video:to:cuda:detach"

    assert payload.pin_memory() is payload
    assert payload.tensor.value == "video:to:cuda:detach:pin"


def test_declared_leaf_without_operation_fails_loudly() -> None:
    payload = LeafObject(object())

    with pytest.raises(RemotePhysDataError) as exc_info:
        payload.to("cpu")

    assert exc_info.value.context["operation"] == "to"
    assert exc_info.value.context["leaf_type"] == "object"


def test_missing_declared_leaf_fails_validation() -> None:
    payload = LeafObject(FakeTensor("video"))
    del payload.tensor

    with pytest.raises(RemotePhysDataError) as exc_info:
        payload.validate()

    assert exc_info.value.context["field"] == "tensor"


def test_composite_data_object_validates_and_recurses_through_declared_children() -> None:
    video = LeafObject(FakeTensor("video"))
    landmarks = LeafObject(FakeTensor("landmarks"))
    composite = CompositeObject(video, landmarks)

    assert composite.validate() is composite
    assert composite.to("cpu") is composite
    assert video.tensor.value == "video:to:cpu"
    assert landmarks.tensor.value == "landmarks:to:cpu"


def test_composite_data_object_rejects_non_data_object_children() -> None:
    composite = CompositeObject(LeafObject(FakeTensor("video")), object())  # type: ignore[arg-type]

    with pytest.raises(RemotePhysDataError) as exc_info:
        composite.validate()

    assert exc_info.value.context["field"] == "landmarks"
    assert exc_info.value.context["actual"] == "object"
