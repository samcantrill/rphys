from __future__ import annotations

import json

import pytest

import rphys.io as io
from rphys.errors import UnsupportedFieldIndexError
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


def test_rgb_video_and_bvp_views_are_field_native_and_not_aligned() -> None:
    video_ref = FieldRef(
        "video.rgb",
        [ResourceRef("file:///records/r001/video.mp4", "file")],
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )
    bvp_ref = FieldRef(
        "signal.bvp.reference",
        [ResourceRef("zarr://records/r001/signals.zarr#bvp", "zarr")],
        schema="signal.bvp.v1",
        metadata={"source_id": "pulse-ox"},
    )

    video_view = FieldView(video_ref, TemporalIndexSlice(0, 60, 2))
    bvp_view = FieldView(bvp_ref, TemporalIndexSlice(120, 240))

    assert video_view.field_ref.key == "video.rgb"
    assert bvp_view.field_ref.key == "signal.bvp.reference"
    assert video_view.field_index != bvp_view.field_index
    assert not hasattr(video_view, "alignment")
    assert not hasattr(bvp_view, "alignment")


def test_lazy_io_descriptors_round_trip_through_json_primitives() -> None:
    view = FieldView(
        FieldRef(
            "video.rgb",
            [
                ResourceRef(
                    "archive://dataset.zip#records/r001/video.mp4",
                    "archive",
                    {"headers": {"accept": "video/mp4"}},
                )
            ],
            schema="video.rgb.v1",
            metadata={"source_id": "camera-front"},
        ),
        TemporalIndexSlice(5, 25, 5),
    )

    payload = json.loads(json.dumps(view.to_dict()))

    assert FieldView.from_dict(payload) == view
    assert "schema_version" not in payload
    assert "fingerprint" not in payload
    assert "payload" not in payload


def test_lazy_io_public_surface_has_no_runtime_or_registry_hooks() -> None:
    for name in io.__all__:
        assert not hasattr(io, "registry")
        public = getattr(io, name)
        for forbidden in ["load", "save", "probe", "build"]:
            assert not hasattr(public, forbidden)

    assert set(io.__all__) == {
        "ResourceRef",
        "FieldRef",
        "FieldIndex",
        "TemporalIndexSlice",
        "FieldView",
    }


def test_unknown_index_type_fails_loudly_without_public_registry() -> None:
    serialized = FieldView(
        FieldRef("video.rgb", [ResourceRef("file:///r001.mp4", "file")])
    ).to_dict()
    serialized["field_index"] = {
        "type": "seconds",
        "start": 0,
        "stop": 1,
        "step": 1,
    }

    with pytest.raises(UnsupportedFieldIndexError):
        FieldView.from_dict(serialized)
