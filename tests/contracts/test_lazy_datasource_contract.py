from __future__ import annotations

import json

import rphys.datasources as datasources
from rphys.data.fields import FieldSpec
from rphys.data.metadata import GROUP, SOURCE_ID, SPLIT, SUBJECT_ID
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.datasources.schemas import DataSourceSchema
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef


def test_datasource_record_schema_contract_preserves_leakage_metadata() -> None:
    schema = DataSourceSchema(
        {
            "video.rgb": FieldSpec("video.rgb", "video", "video.rgb.v1"),
            "signal.bvp.reference": FieldSpec(
                "signal.bvp.reference",
                "signal",
                "signal.bvp.v1",
            ),
        },
        metadata={SOURCE_ID: "ubfc"},
    )
    datasource = DataSourceRef(
        "ubfc-rppg",
        source=ResourceRef("file:///datasets/ubfc", "file"),
        schema=schema,
        metadata={SOURCE_ID: "ubfc"},
    )
    record = RecordRef(
        datasource,
        "subject01/vid01",
        {
            "video.rgb": FieldRef(
                "video.rgb",
                [ResourceRef("file:///datasets/ubfc/subject01/vid01.avi", "file")],
                schema="video.rgb.v1",
            ),
            "signal.bvp.reference": FieldRef(
                "signal.bvp.reference",
                [ResourceRef("file:///datasets/ubfc/subject01/bvp.csv", "file")],
                schema="signal.bvp.v1",
            ),
        },
        metadata={SUBJECT_ID: "subject01", SPLIT: "train", GROUP: "subject01"},
    )

    assert record.datasource.datasource_id == "ubfc-rppg"
    assert record.metadata[SUBJECT_ID] == "subject01"
    assert record.metadata[SPLIT] == "train"
    assert record.metadata[GROUP] == "subject01"
    assert not hasattr(record, "subject_id")
    assert not hasattr(record, "split")
    assert not hasattr(datasource, "fingerprint")


def test_datasource_descriptors_round_trip_through_json_primitives() -> None:
    schema = DataSourceSchema(
        {"video.rgb": FieldSpec("video.rgb", "video", "video.rgb.v1")}
    )
    datasource = DataSourceRef("fixture", schema=schema, metadata={"source_id": "fx"})
    record = RecordRef(
        datasource,
        "record-1",
        {
            "video.rgb": FieldRef(
                "video.rgb",
                [ResourceRef("archive://fixture.zip#record-1/video.mp4", "archive")],
                schema="video.rgb.v1",
            )
        },
    )

    payload = json.loads(json.dumps(record.to_dict()))

    assert RecordRef.from_dict(payload) == record
    assert "schema_version" not in payload
    assert "fingerprint" not in payload
    assert "validation_status" not in payload


def test_datasource_public_surface_has_no_builder_manifest_or_registry_hooks() -> None:
    assert set(datasources.__all__) == {
        "DataSourceRef",
        "RecordRef",
        "DataSourceSchema",
    }
    assert not hasattr(datasources, "registry")
    assert not hasattr(datasources, "IndexItem")

    for name in datasources.__all__:
        public = getattr(datasources, name)
        for forbidden in ["scan", "filter", "build", "load", "manifest"]:
            assert not hasattr(public, forbidden)
