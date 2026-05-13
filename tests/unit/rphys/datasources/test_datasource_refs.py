from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.fields import FieldSpec
from rphys.data.keys import DataKey
from rphys.data.metadata import GROUP, SOURCE_ID, SPLIT, SUBJECT_ID, MetadataKey
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.datasources.schemas import DataSourceSchema
from rphys.errors import (
    InvalidDataSourceRefError,
    InvalidRecordRefError,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef


def _video_field() -> FieldRef:
    return FieldRef(
        "video.rgb",
        [ResourceRef("file:///records/r001/video.mp4", "file")],
        schema="video.rgb.v1",
    )


def _bvp_field() -> FieldRef:
    return FieldRef(
        "signal.bvp.reference",
        [ResourceRef("file:///records/r001/bvp.csv", "file")],
        schema="signal.bvp.v1",
    )


def _schema() -> DataSourceSchema:
    return DataSourceSchema(
        {
            "video.rgb": FieldSpec("video.rgb", "video", "video.rgb.v1"),
            "signal.bvp.reference": FieldSpec(
                "signal.bvp.reference",
                "signal",
                "signal.bvp.v1",
            ),
        }
    )


def _datasource() -> DataSourceRef:
    return DataSourceRef(
        "ubfc-rppg",
        source=ResourceRef("file:///datasets/ubfc", "file"),
        schema=_schema(),
        metadata={SOURCE_ID: "ubfc", "license": "research-only"},
    )


def _record() -> RecordRef:
    return RecordRef(
        _datasource(),
        "subject01/vid01",
        {
            "video.rgb": _video_field(),
            "signal.bvp.reference": _bvp_field(),
        },
        metadata={SUBJECT_ID: "subject01", SPLIT: "train", GROUP: "subject01"},
    )


def test_datasource_ref_preserves_identity_source_schema_and_metadata() -> None:
    datasource = _datasource()

    assert datasource.datasource_id == "ubfc-rppg"
    assert datasource.source == ResourceRef("file:///datasets/ubfc", "file")
    assert datasource.schema == _schema()
    assert datasource.metadata[MetadataKey("source_id")] == "ubfc"
    assert not hasattr(datasource, "fingerprint")
    assert not hasattr(datasource, "records")


def test_datasource_ref_copies_and_freezes_metadata() -> None:
    metadata = {"source_id": {"name": "fixture"}, "folds": [1, 2]}
    datasource = DataSourceRef("fixture", metadata=metadata)
    metadata["source_id"]["name"] = "mutated"
    metadata["folds"].append(3)

    assert datasource.to_dict()["metadata"] == {
        "source_id": {"name": "fixture"},
        "folds": [1, 2],
    }
    with pytest.raises(TypeError):
        datasource.metadata[MetadataKey("source_id")] = "mutated"
    with pytest.raises(TypeError):
        datasource.metadata[MetadataKey("source_id")]["name"] = "mutated"  # type: ignore[index]
    with pytest.raises(AttributeError):
        datasource.metadata[MetadataKey("folds")].append(3)  # type: ignore[attr-defined]


def test_datasource_ref_round_trips_through_primitive_dict() -> None:
    datasource = _datasource()
    serialized = datasource.to_dict()

    assert serialized["datasource_id"] == "ubfc-rppg"
    assert serialized["source"] == {
        "uri": "file:///datasets/ubfc",
        "protocol": "file",
        "storage_options": {},
    }
    assert serialized["schema"] == _schema().to_dict()
    assert serialized["metadata"] == {
        "source_id": "ubfc",
        "license": "research-only",
    }
    assert DataSourceRef.from_dict(serialized) == datasource
    assert "fingerprint" not in serialized
    assert "schema_version" not in serialized


def test_datasource_ref_rejects_invalid_components() -> None:
    with pytest.raises(InvalidDataSourceRefError):
        DataSourceRef("")
    with pytest.raises(InvalidDataSourceRefError):
        DataSourceRef("fixture", source="file:///datasets/fixture")  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceRefError):
        DataSourceRef("fixture", schema=object())  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceRefError):
        DataSourceRef("fixture", metadata={"source_id": object()})


def test_record_ref_preserves_record_identity_fields_and_leakage_metadata() -> None:
    record = _record()

    assert record.datasource == _datasource()
    assert record.record_id == "subject01/vid01"
    assert record.fields[DataKey("video.rgb")] == _video_field()
    assert record.fields[DataKey("signal.bvp.reference")] == _bvp_field()
    assert record.metadata[SUBJECT_ID] == "subject01"
    assert record.metadata[SPLIT] == "train"
    assert record.metadata[GROUP] == "subject01"
    assert not hasattr(record, "subject_id")
    assert not hasattr(record, "split")
    assert not hasattr(record, "group")


def test_record_ref_has_value_equality_without_public_hash_contract() -> None:
    record = _record()

    assert record == _record()
    with pytest.raises(FrozenInstanceError):
        record.record_id = "mutated"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(record)


def test_record_ref_round_trips_through_primitive_dict() -> None:
    record = _record()
    serialized = record.to_dict()

    assert serialized["datasource"] == _datasource().to_dict()
    assert serialized["record_id"] == "subject01/vid01"
    assert set(serialized["fields"]) == {"video.rgb", "signal.bvp.reference"}
    assert serialized["metadata"] == {
        "subject_id": "subject01",
        "split": "train",
        "group": "subject01",
    }
    assert RecordRef.from_dict(serialized) == record
    assert "fingerprint" not in serialized
    assert "validation_status" not in serialized


def test_record_ref_rejects_invalid_components_and_field_mismatches() -> None:
    with pytest.raises(InvalidRecordRefError):
        RecordRef("datasource", "record-1", {"video.rgb": _video_field()})  # type: ignore[arg-type]
    with pytest.raises(InvalidRecordRefError):
        RecordRef(_datasource(), "", {"video.rgb": _video_field()})
    with pytest.raises(InvalidRecordRefError):
        RecordRef(_datasource(), "record-1", {})
    with pytest.raises(InvalidRecordRefError):
        RecordRef(_datasource(), "record-1", {"video.rgb": object()})  # type: ignore[dict-item]
    with pytest.raises(InvalidRecordRefError):
        RecordRef(_datasource(), "record-1", {"video.rgb": _bvp_field()})


def test_record_ref_from_dict_rejects_manifest_or_validation_shapes() -> None:
    serialized = _record().to_dict()
    serialized["fingerprint"] = "abc"

    with pytest.raises(InvalidRecordRefError):
        RecordRef.from_dict(serialized)
    with pytest.raises(InvalidRecordRefError):
        RecordRef.from_dict({"record_id": "r001", "fields": {}})


def test_datasource_and_record_refs_have_no_builder_or_runtime_hooks() -> None:
    for descriptor in [_datasource(), _record()]:
        for name in ["scan", "filter", "split", "build", "load", "validate_payload"]:
            assert not hasattr(descriptor, name)
