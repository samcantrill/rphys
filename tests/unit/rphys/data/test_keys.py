from __future__ import annotations

import pytest

from rphys.errors import InvalidDataKeyError
from rphys.data.keys import DataKey, RESERVED_NAMESPACES


@pytest.mark.parametrize(
    "value",
    [
        "video.rgb",
        "signal.bvp.reference",
        "timestamps.video.seconds",
        "landmarks.face.mediapipe_468",
        "mask.face.skin",
        "quality.face_visibility",
        "custom.demo.embedding",
    ],
)
def test_data_key_accepts_approved_examples(value: str) -> None:
    key = DataKey(value)

    assert key == value
    assert isinstance(key, str)
    assert hash(key) == hash(value)


def test_data_key_reserved_namespaces_are_available_for_grammar_docs() -> None:
    assert "video" in RESERVED_NAMESPACES
    assert "custom" in RESERVED_NAMESPACES
    assert isinstance(RESERVED_NAMESPACES, frozenset)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "video",
        "Video.RGB",
        "video/rgb",
        "inputs/video.rgb",
        "video.rgb#source_id",
        "video.rgb ",
        " video.rgb",
        "vidéo.rgb",
        "video.-rgb",
        "video.rgb-source",
        ".video.rgb",
        "video..rgb",
        "video.rgb.",
        "custom",
        "custom.demo",
        "demo.embedding",
    ],
)
def test_data_key_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidDataKeyError) as exc_info:
        DataKey(value)

    assert exc_info.value.context["key"] == value
    assert "expected" in exc_info.value.context


def test_data_key_rejects_non_string_values() -> None:
    with pytest.raises(InvalidDataKeyError) as exc_info:
        DataKey(42)  # type: ignore[arg-type]

    assert exc_info.value.context["key"] == 42
    assert exc_info.value.context["actual"] == "int"
