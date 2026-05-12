from __future__ import annotations

import importlib.util

import pytest

from rphys import errors
from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator
from rphys.data.metadata import (
    GROUP,
    RECORD_ID,
    SAMPLE_ID,
    SOURCE_ID,
    SPLIT,
    SUBJECT_ID,
)
from rphys.data.schemas import SchemaName
from rphys.data.splits import PREDICT, TEST, TRAIN, VALID, SplitName
from rphys.data.types import SIGNAL, VIDEO, DataType


def test_data_key_contract_examples() -> None:
    valid = [
        "video.rgb",
        "signal.bvp.reference",
        "timestamps.video.seconds",
        "landmarks.face.mediapipe_468",
        "mask.face.skin",
        "quality.face_visibility",
        "custom.demo.embedding",
    ]
    invalid = [
        "inputs/video.rgb",
        "Video.RGB",
        "video/rgb",
        "video.rgb#source_id",
    ]

    assert [DataKey(value) for value in valid] == valid
    for value in invalid:
        with pytest.raises(errors.InvalidDataKeyError):
            DataKey(value)


def test_field_locator_contract_examples_preserve_components() -> None:
    values = [
        "inputs/video.rgb",
        "targets/signal.bvp.reference",
        "predictions/signal.bvp",
        "metrics/quality.face_visibility",
        "diagnostics/quality.face_visibility#source_id",
    ]

    for value in values:
        locator = FieldLocator.parse(value)
        assert str(locator) == value
        assert locator.role.value == value.split("/", 1)[0]
        assert isinstance(locator.key, DataKey)

    with pytest.raises(errors.InvalidFieldLocatorError) as exc_info:
        FieldLocator.parse("inputs/video.rgb#Source_ID")
    assert exc_info.value.context["component"] == "metadata_key"


def test_schema_and_data_type_contract_stay_separate() -> None:
    assert SchemaName("video.rgb.v1") == "video.rgb.v1"
    assert SchemaName("signal.bvp.v1") == "signal.bvp.v1"
    assert VIDEO == DataType("video")
    assert SIGNAL == DataType("signal")

    with pytest.raises(errors.InvalidSchemaNameError):
        SchemaName("video.rgb")
    with pytest.raises(errors.InvalidDataTypeError):
        DataType("video.rgb.v1")


def test_metadata_and_split_contract_stay_descriptive() -> None:
    assert [SOURCE_ID, GROUP, SPLIT] == ["source_id", "group", "split"]
    assert [SUBJECT_ID, RECORD_ID, SAMPLE_ID] == [
        "subject_id",
        "record_id",
        "sample_id",
    ]
    assert [TRAIN, VALID, TEST, PREDICT] == ["train", "valid", "test", "predict"]

    metadata = {SPLIT: SplitName("train")}
    assert metadata[SPLIT] == TRAIN
    assert not hasattr(SplitName, "loop_mode")


def test_no_normalization_contract() -> None:
    for constructor, value in [
        (DataKey, " Video.RGB "),
        (SchemaName, " Video.RGB.v1 "),
        (DataType, " Video "),
        (SplitName, " Train "),
    ]:
        with pytest.raises(errors.RemotePhysError):
            constructor(value)


def test_no_runtime_workflow_or_artifact_contract() -> None:
    for package_name in [
        "rphys.artifacts",
        "rphys.workflow",
        "rphys.workflows",
        "rphys.stages",
    ]:
        assert importlib.util.find_spec(package_name) is None

    assert not hasattr(FieldLocator, "lookup")
    assert not hasattr(SchemaName, "validate_payload")
    assert not hasattr(DataType, "from_torch")
