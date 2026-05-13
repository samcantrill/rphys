from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.errors import InvalidResourceRefError
from rphys.io.resources import ResourceRef


def test_resource_ref_preserves_storage_identity_without_parsing() -> None:
    ref = ResourceRef(
        "archive://dataset.zip#records/r001/video.mp4",
        "archive",
        {"anon": False},
    )

    assert ref.uri == "archive://dataset.zip#records/r001/video.mp4"
    assert ref.protocol == "archive"
    assert ref.storage_options == {"anon": False}
    assert not hasattr(ref, "path")
    assert not hasattr(ref, "member")
    assert not hasattr(ref, "codec")


def test_resource_ref_copies_and_freezes_storage_options() -> None:
    options = {
        "headers": {"authorization": "token"},
        "chunks": [1, 2],
    }

    ref = ResourceRef("s3://bucket/record.zarr", "s3", options)
    options["headers"]["authorization"] = "mutated"
    options["chunks"].append(3)

    assert ref.to_dict()["storage_options"] == {
        "headers": {"authorization": "token"},
        "chunks": [1, 2],
    }
    with pytest.raises(TypeError):
        ref.storage_options["headers"] = {}
    with pytest.raises(TypeError):
        ref.storage_options["headers"]["authorization"] = "mutated"  # type: ignore[index]
    with pytest.raises(AttributeError):
        ref.storage_options["chunks"].append(3)  # type: ignore[attr-defined]


def test_resource_ref_has_value_equality_without_public_hash_contract() -> None:
    ref = ResourceRef("file:///record.mp4", "file", {"mode": "r"})

    assert ref == ResourceRef("file:///record.mp4", "file", {"mode": "r"})
    with pytest.raises(FrozenInstanceError):
        ref.uri = "file:///mutated.mp4"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(ref)


def test_resource_ref_round_trips_through_primitive_dict() -> None:
    ref = ResourceRef(
        "zarr://dataset/record",
        "zarr",
        {"cache": {"enabled": True}, "chunks": [1, 2], "missing": None},
    )

    serialized = ref.to_dict()

    assert serialized == {
        "uri": "zarr://dataset/record",
        "protocol": "zarr",
        "storage_options": {
            "cache": {"enabled": True},
            "chunks": [1, 2],
            "missing": None,
        },
    }
    assert ResourceRef.from_dict(serialized) == ref
    assert "schema_version" not in serialized
    assert "fingerprint" not in serialized


@pytest.mark.parametrize(
    ("args", "kwargs"),
    [
        (("", "file"), {}),
        (("file:///record.mp4", ""), {}),
        (("file:///record.mp4", "file"), {"storage_options": "anon"}),
        (("file:///record.mp4", "file"), {"storage_options": {"obj": object()}}),
        (("file:///record.mp4", "file"), {"storage_options": {"nan": float("nan")}}),
    ],
)
def test_resource_ref_rejects_invalid_inputs(args: tuple[object, ...], kwargs: dict[str, object]) -> None:
    with pytest.raises(InvalidResourceRefError):
        ResourceRef(*args, **kwargs)  # type: ignore[arg-type]


def test_resource_ref_from_dict_rejects_non_stage_3_shapes() -> None:
    with pytest.raises(InvalidResourceRefError):
        ResourceRef.from_dict({"uri": "file:///record.mp4", "protocol": "file"})
    with pytest.raises(InvalidResourceRefError):
        ResourceRef.from_dict(
            {
                "uri": "file:///record.mp4",
                "protocol": "file",
                "storage_options": {},
                "schema_version": 1,
            }
        )


def test_resource_ref_has_no_io_runtime_hooks() -> None:
    ref = ResourceRef("file:///record.mp4", "file")

    for name in ["load", "save", "probe", "open", "build", "to_sample"]:
        assert not hasattr(ref, name)
