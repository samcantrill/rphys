from __future__ import annotations

import json
from collections.abc import Mapping

import rphys
import rphys.datasources as datasources
import rphys.io as io
from rphys.data.fields import FieldSpec
from rphys.data.locators import FieldLocator
from rphys.data.metadata import GROUP, SOURCE_ID, SPLIT, SUBJECT_ID


FORBIDDEN_DESCRIPTOR_KEYS = {
    "schema_version",
    "version",
    "fingerprint",
    "item_id",
    "member",
    "payload",
    "manifest",
    "validation_status",
    "observed_fields",
    "expected_fields",
}


def test_complete_lazy_reference_graph_round_trips_through_public_imports() -> None:
    schema = datasources.DataSourceSchema(
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
    datasource = datasources.DataSourceRef(
        "ubfc-rppg",
        source=io.ResourceRef("file:///datasets/ubfc", "file"),
        schema=schema,
        metadata={SOURCE_ID: "ubfc"},
    )
    record = datasources.RecordRef(
        datasource,
        "subject01/vid01",
        {
            "video.rgb": io.FieldRef(
                "video.rgb",
                [io.ResourceRef("file:///datasets/ubfc/subject01/vid01.avi", "file")],
                schema="video.rgb.v1",
            ),
            "signal.bvp.reference": io.FieldRef(
                "signal.bvp.reference",
                [io.ResourceRef("file:///datasets/ubfc/subject01/bvp.csv", "file")],
                schema="signal.bvp.v1",
            ),
        },
        metadata={SUBJECT_ID: "subject01", SPLIT: "train", GROUP: "subject01"},
    )
    item = datasources.IndexItem(
        {
            "inputs/video.rgb": io.FieldView(
                record.fields["video.rgb"],
                io.TemporalIndexSlice(0, 60, 2),
            ),
            "targets/signal.bvp.reference": io.FieldView(
                record.fields["signal.bvp.reference"],
                io.TemporalIndexSlice(120, 240),
            ),
        },
        record,
        metadata={"source_id": "window-1"},
    )

    payload = json.loads(json.dumps(item.to_dict()))

    assert datasources.IndexItem.from_dict(payload) == item
    assert item.record.metadata[SUBJECT_ID] == "subject01"
    assert item.record.metadata[SPLIT] == "train"
    video_locator = FieldLocator.parse("inputs/video.rgb")
    bvp_locator = FieldLocator.parse("targets/signal.bvp.reference")

    assert item.fields[video_locator].field_ref.key != item.fields[bvp_locator].field_ref.key
    assert item.fields[video_locator].field_index != item.fields[bvp_locator].field_index
    _assert_forbidden_keys_absent(payload)


def test_stage_3_public_packages_are_intentional_and_root_stays_empty() -> None:
    assert rphys.__all__ == []
    assert io.__all__ == [
        "ResourceRef",
        "FieldRef",
        "FieldIndex",
        "TemporalIndexSlice",
        "FieldView",
    ]
    assert datasources.__all__ == [
        "DataSourceRef",
        "RecordRef",
        "DataSourceSchema",
        "IndexItem",
    ]
    assert "_primitives" not in io.__all__
    assert not hasattr(datasources, "registry")


def test_stage_3_descriptors_exclude_runtime_and_builder_hooks() -> None:
    descriptor_classes = [
        io.ResourceRef,
        io.FieldRef,
        io.TemporalIndexSlice,
        io.FieldView,
        datasources.DataSourceRef,
        datasources.RecordRef,
        datasources.DataSourceSchema,
        datasources.IndexItem,
    ]
    forbidden = [
        "load",
        "save",
        "probe",
        "scan",
        "filter",
        "build",
        "to_sample",
        "transform",
        "augment",
        "export",
        "train",
        "register",
        "registry",
    ]

    for descriptor_class in descriptor_classes:
        for name in forbidden:
            assert not hasattr(descriptor_class, name)


def _assert_forbidden_keys_absent(value: object) -> None:
    if isinstance(value, Mapping):
        assert FORBIDDEN_DESCRIPTOR_KEYS.isdisjoint(value)
        for item in value.values():
            _assert_forbidden_keys_absent(item)
    elif isinstance(value, list):
        for item in value:
            _assert_forbidden_keys_absent(item)
