from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.fields import FieldSpec
from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidDataSourceSchemaError, InvalidDataKeyError
from rphys.datasources.schemas import DataSourceSchema


def _schema() -> DataSourceSchema:
    return DataSourceSchema(
        {
            "video.rgb": FieldSpec("video.rgb", "video", "video.rgb.v1"),
            "signal.bvp.reference": FieldSpec(
                "signal.bvp.reference",
                "signal",
                "signal.bvp.v1",
            ),
        },
        metadata={"source_id": "ubfc"},
    )


def test_datasource_schema_declares_non_empty_field_specs() -> None:
    schema = _schema()

    assert set(schema.fields) == {
        DataKey("video.rgb"),
        DataKey("signal.bvp.reference"),
    }
    assert schema.fields[DataKey("video.rgb")] == FieldSpec(
        "video.rgb",
        "video",
        "video.rgb.v1",
    )
    assert schema.metadata == {MetadataKey("source_id"): "ubfc"}
    assert not hasattr(schema, "validation_status")
    assert not hasattr(schema, "observed_fields")


def test_datasource_schema_copies_and_freezes_metadata() -> None:
    metadata = {"source_id": {"name": "fixture"}, "folds": [1, 2]}
    schema = DataSourceSchema(
        {"video.rgb": FieldSpec("video.rgb", "video")},
        metadata=metadata,
    )
    metadata["source_id"]["name"] = "mutated"
    metadata["folds"].append(3)

    assert schema.to_dict()["metadata"] == {
        "source_id": {"name": "fixture"},
        "folds": [1, 2],
    }
    with pytest.raises(TypeError):
        schema.metadata[MetadataKey("source_id")] = "mutated"
    with pytest.raises(TypeError):
        schema.metadata[MetadataKey("source_id")]["name"] = "mutated"  # type: ignore[index]
    with pytest.raises(AttributeError):
        schema.metadata[MetadataKey("folds")].append(3)  # type: ignore[attr-defined]


def test_datasource_schema_has_value_equality_without_public_hash_contract() -> None:
    schema = _schema()

    assert schema == _schema()
    with pytest.raises(FrozenInstanceError):
        schema.fields = {}  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(schema)


def test_datasource_schema_field_declarations_are_immutable_through_mapping() -> None:
    spec = FieldSpec("video.rgb", "video", "video.rgb.v1")
    schema = DataSourceSchema({"video.rgb": spec})
    stored = schema.fields[DataKey("video.rgb")]

    assert stored is spec
    with pytest.raises(TypeError):
        schema.fields[DataKey("signal.bvp.reference")] = FieldSpec(
            "signal.bvp.reference",
            "signal",
        )
    with pytest.raises(FrozenInstanceError):
        stored.schema = None  # type: ignore[misc]
    assert schema.fields[DataKey("video.rgb")] == FieldSpec(
        "video.rgb",
        "video",
        "video.rgb.v1",
    )
    assert not hasattr(FieldSpec, "to_dict")
    assert not hasattr(FieldSpec, "from_dict")


def test_datasource_schema_round_trips_through_primitive_dict() -> None:
    schema = _schema()
    serialized = schema.to_dict()

    assert serialized == {
        "fields": {
            "video.rgb": {
                "key": "video.rgb",
                "data_type": "video",
                "schema": "video.rgb.v1",
            },
            "signal.bvp.reference": {
                "key": "signal.bvp.reference",
                "data_type": "signal",
                "schema": "signal.bvp.v1",
            },
        },
        "metadata": {"source_id": "ubfc"},
    }
    assert DataSourceSchema.from_dict(serialized) == schema
    assert "schema_version" not in serialized
    assert "fingerprint" not in serialized
    assert "validation_status" not in serialized


def test_datasource_schema_rejects_invalid_declarations() -> None:
    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema({})
    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema({"video.rgb": object()})  # type: ignore[dict-item]
    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema(
            {"video.rgb": FieldSpec("signal.bvp.reference", "signal")}
        )
    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema(
            {"video.rgb": FieldSpec("video.rgb", "video")},
            metadata={"source_id": object()},
        )
    with pytest.raises(InvalidDataKeyError):
        DataSourceSchema({"Video.RGB": FieldSpec("video.rgb", "video")})


def test_datasource_schema_from_dict_rejects_validation_report_shapes() -> None:
    serialized = _schema().to_dict()
    serialized["validation_status"] = "passed"

    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema.from_dict(serialized)
    with pytest.raises(InvalidDataSourceSchemaError):
        DataSourceSchema.from_dict({"fields": {}})


def test_datasource_schema_has_no_scanning_or_validation_hooks() -> None:
    schema = _schema()

    for name in ["scan", "validate_payload", "validate_record", "build", "filter"]:
        assert not hasattr(schema, name)
