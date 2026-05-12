from __future__ import annotations

import pytest

from rphys.errors import InvalidSchemaNameError
from rphys.data.schemas import SchemaName


@pytest.mark.parametrize(
    "value",
    [
        "video.rgb.v1",
        "signal.bvp.v1",
        "landmarks.face.mediapipe_468.v12",
    ],
)
def test_schema_name_accepts_versioned_names(value: str) -> None:
    schema = SchemaName(value)

    assert schema == value
    assert isinstance(schema, str)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "video.rgb",
        "Video.RGB.v1",
        "video/rgb.v1",
        "video.rgb#source_id.v1",
        "video..rgb.v1",
        "video.rgb.v0",
        "video.rgb.v01",
        "video.rgb.v",
        "video.rgb.version1",
        "float32",
        "torch.float32",
    ],
)
def test_schema_name_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidSchemaNameError) as exc_info:
        SchemaName(value)

    assert exc_info.value.context["schema"] == value
    assert "expected" in exc_info.value.context


def test_schema_names_do_not_define_payload_validation() -> None:
    assert not hasattr(SchemaName, "validate_payload")
    assert not hasattr(SchemaName, "dtype")
    assert not hasattr(SchemaName, "sample_rate")
