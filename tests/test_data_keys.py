"""Tests for logical field key validation and public string behavior."""

from __future__ import annotations

from copy import copy, deepcopy

import pytest

from rphys.data import (
    CUSTOM_NAMESPACE,
    STANDARD_NAMESPACES,
    VIDEO_NAMESPACE,
    DataKey,
)
from rphys.errors import RemotePhysDataError


@pytest.mark.parametrize(
    "raw_key",
    (
        "video.rgb",
        "video.rgb.raw",
        "signal.bvp.reference",
        "timestamps.video",
        "face.landmarks.mediapipe_468",
        "prediction.quality.signal_snr",
        "view.a.video.rgb",
        "custom.my_project.some_field",
    ),
)
def test_data_key_accepts_reserved_and_custom_keys(raw_key: str) -> None:
    key = DataKey(raw_key)

    assert isinstance(key, str)
    assert str(key) == raw_key
    assert key == raw_key
    assert hash(key) == hash(raw_key)
    assert copy(key) == key
    assert deepcopy(key) == key


def test_data_key_exposes_namespace_parts_and_custom_status() -> None:
    standard_key = DataKey("video.rgb.raw")
    custom_key = DataKey("custom.project.field")

    assert standard_key.namespace == "video"
    assert standard_key.parts == ("video", "rgb", "raw")
    assert standard_key.is_custom is False
    assert custom_key.namespace == "custom"
    assert custom_key.is_custom is True


def test_namespace_constants_are_public_without_standard_key_catalog() -> None:
    assert VIDEO_NAMESPACE == "video"
    assert CUSTOM_NAMESPACE == "custom"
    assert "video" in STANDARD_NAMESPACES
    assert "custom" in STANDARD_NAMESPACES
    assert all("." not in namespace for namespace in STANDARD_NAMESPACES)


@pytest.mark.parametrize(
    "raw_key",
    (
        "",
        "video",
        ".video.rgb",
        "video.rgb.",
        "video..rgb",
        "Video.rgb",
        "video.RGB",
        "video.rgb-raw",
        "video rgb",
        "unknown.rgb",
        "custom.project",
        "custom..field",
        "custom.Project.field",
    ),
)
def test_data_key_rejects_invalid_strings(raw_key: str) -> None:
    with pytest.raises(RemotePhysDataError):
        DataKey(raw_key)


def test_data_key_rejects_non_string_values() -> None:
    with pytest.raises(RemotePhysDataError):
        DataKey(42)  # type: ignore[arg-type]
