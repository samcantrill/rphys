from __future__ import annotations

import pytest

from rphys.errors import InvalidDataTypeError
from rphys.data.types import (
    ANNOTATION,
    EMBEDDING,
    LABEL,
    LANDMARKS,
    MASK,
    METADATA,
    QUALITY,
    SIGNAL,
    TIMESTAMPS,
    VIDEO,
    DataType,
)


def test_data_type_constants_are_validated_instances() -> None:
    constants = [
        VIDEO,
        SIGNAL,
        TIMESTAMPS,
        LANDMARKS,
        MASK,
        EMBEDDING,
        LABEL,
        QUALITY,
        ANNOTATION,
        METADATA,
    ]

    assert [str(value) for value in constants] == [
        "video",
        "signal",
        "timestamps",
        "landmarks",
        "mask",
        "embedding",
        "label",
        "quality",
        "annotation",
        "metadata",
    ]
    assert all(isinstance(value, DataType) for value in constants)


@pytest.mark.parametrize("value", ["flow", "spectrogram", "custom_signal"])
def test_data_type_accepts_downstream_category_tokens(value: str) -> None:
    data_type = DataType(value)

    assert data_type == value
    assert isinstance(data_type, str)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Video",
        "video stream",
        "video-stream",
        "video/rgb",
        "video.rgb",
        "metadata#source_id",
        "vídeo",
        "1video",
        "float32",
        "int64",
        "torch.float32",
    ],
)
def test_data_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidDataTypeError) as exc_info:
        DataType(value)

    assert exc_info.value.context["data_type"] == value
    assert "expected" in exc_info.value.context


def test_data_types_do_not_inspect_backend_payloads() -> None:
    assert not hasattr(DataType, "from_numpy")
    assert not hasattr(DataType, "from_torch")
    assert not hasattr(DataType, "matches")
