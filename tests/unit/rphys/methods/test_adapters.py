from __future__ import annotations

import pytest

from rphys.data import Batch, FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import FieldSchemaError, FieldTypeError, MissingFieldError, RemotePhysMethodError
from rphys.methods import MethodInputAdapter, MethodInputSpec


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")
def test_input_spec_normalizes_locators_and_validates_expected_type() -> None:
    spec = MethodInputSpec(
        "video",
        "inputs/video.rgb",
        expected_type=list,
        schema="video.rgb.v1",
    )

    assert spec.locator == VIDEO
    assert spec.expected_type is list
    assert str(spec.schema) == "video.rgb.v1"

    with pytest.raises(RemotePhysMethodError):
        MethodInputSpec("", VIDEO)
    with pytest.raises(RemotePhysMethodError):
        MethodInputSpec("bad", VIDEO, expected_type=())  # type: ignore[arg-type]
    with pytest.raises(RemotePhysMethodError) as target_error:
        MethodInputSpec("target", BVP)
    assert target_error.value.context["role"] == "targets"


def test_input_adapter_extracts_declared_batch_payloads() -> None:
    adapter = MethodInputAdapter(
        [
            MethodInputSpec("video", VIDEO, expected_type=list, schema="video.rgb.v1"),
        ]
    )
    batch = Batch(
        {
            VIDEO: FieldValue(["frame-0", "frame-1"], schema="video.rgb.v1"),
            BVP: FieldValue([[0.1], [0.2]], schema="signal.bvp.v1"),
        }
    )

    assert adapter.extract(batch) == {"video": ["frame-0", "frame-1"]}


def test_input_adapter_rejects_duplicates_missing_fields_and_type_schema_mismatch() -> None:
    with pytest.raises(RemotePhysMethodError, match="duplicate names"):
        MethodInputAdapter(
            [
                MethodInputSpec("video", VIDEO),
                MethodInputSpec("video", "inputs/signal.bvp.source"),
            ]
        )
    with pytest.raises(RemotePhysMethodError, match="duplicate locators"):
        MethodInputAdapter(
            [
                MethodInputSpec("video", VIDEO),
                MethodInputSpec("again", "inputs/video.rgb"),
            ]
        )

    adapter = MethodInputAdapter(
        [MethodInputSpec("video", VIDEO, expected_type=list, schema="video.rgb.v1")]
    )
    with pytest.raises(MissingFieldError):
        adapter.extract(Batch())
    with pytest.raises(FieldTypeError):
        adapter.extract(Batch({VIDEO: FieldValue("not-list", schema="video.rgb.v1")}))
    with pytest.raises(FieldSchemaError):
        adapter.extract(Batch({VIDEO: FieldValue([], schema="video.gray.v1")}))
