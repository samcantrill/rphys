from __future__ import annotations

import json

from rphys.data.locators import FieldLocator
from rphys.datasources.index_items import IndexItem
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


def _record() -> RecordRef:
    return RecordRef(
        DataSourceRef("fixture"),
        "record-1",
        {
            "video.rgb": FieldRef(
                "video.rgb",
                [ResourceRef("file:///record-1/video.mp4", "file")],
                schema="video.rgb.v1",
            ),
            "signal.bvp.reference": FieldRef(
                "signal.bvp.reference",
                [ResourceRef("file:///record-1/bvp.csv", "file")],
                schema="signal.bvp.v1",
            ),
        },
        metadata={"subject_id": "s1", "split": "train", "group": "s1"},
    )


def test_role_qualified_index_item_contract_does_not_build_sample() -> None:
    record = _record()
    item = IndexItem(
        {
            "inputs/video.rgb": FieldView(
                record.fields["video.rgb"],
                TemporalIndexSlice(0, 60, 2),
            ),
            "targets/signal.bvp.reference": FieldView(
                record.fields["signal.bvp.reference"],
                TemporalIndexSlice(120, 240),
            ),
        },
        record,
        metadata={"source_id": "window-1"},
    )

    assert item.fields[FieldLocator.parse("inputs/video.rgb")].field_ref.key == "video.rgb"
    assert (
        item.fields[FieldLocator.parse("targets/signal.bvp.reference")].field_ref.key
        == "signal.bvp.reference"
    )
    assert not hasattr(item, "sample")
    assert not hasattr(item, "payload")
    assert not hasattr(item, "alignment")
    assert not hasattr(item, "item_id")


def test_index_item_round_trips_through_json_primitives() -> None:
    record = _record()
    item = IndexItem(
        {"inputs/video.rgb": FieldView(record.fields["video.rgb"])},
        record,
    )
    payload = json.loads(json.dumps(item.to_dict()))

    assert IndexItem.from_dict(payload) == item
    assert "item_id" not in payload
    assert "fingerprint" not in payload
    assert "manifest" not in payload


def test_index_item_public_surface_has_no_runtime_or_training_hooks() -> None:
    for forbidden in [
        "load",
        "build",
        "to_sample",
        "transform",
        "augment",
        "export",
        "train",
        "registry",
    ]:
        assert not hasattr(IndexItem, forbidden)
