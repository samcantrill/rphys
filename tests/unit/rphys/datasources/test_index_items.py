from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.datasources.index_items import IndexItem
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import InvalidIndexItemError
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
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


def _record() -> RecordRef:
    return RecordRef(
        DataSourceRef("fixture"),
        "record-1",
        {
            "video.rgb": _video_field(),
            "signal.bvp.reference": _bvp_field(),
        },
        metadata={"subject_id": "s1"},
    )


def _item() -> IndexItem:
    return IndexItem(
        {
            "inputs/video.rgb": FieldView(_video_field(), TemporalIndexSlice(0, 60, 2)),
            "targets/signal.bvp.reference": FieldView(
                _bvp_field(),
                TemporalIndexSlice(120, 240),
            ),
        },
        _record(),
        metadata={"source_id": "window-1"},
    )


def test_index_item_preserves_role_qualified_views_and_record_provenance() -> None:
    item = _item()

    video_locator = FieldLocator.parse("inputs/video.rgb")
    bvp_locator = FieldLocator.parse("targets/signal.bvp.reference")

    assert item.record == _record()
    assert item.fields[video_locator].field_ref.key == DataKey("video.rgb")
    assert item.fields[bvp_locator].field_ref.key == DataKey("signal.bvp.reference")
    assert item.fields[video_locator].field_index == TemporalIndexSlice(0, 60, 2)
    assert item.fields[bvp_locator].field_index == TemporalIndexSlice(120, 240)
    assert item.metadata == {MetadataKey("source_id"): "window-1"}
    assert not hasattr(item, "item_id")
    assert not hasattr(item, "fingerprint")
    assert not hasattr(item, "sample")


def test_index_item_copies_and_freezes_metadata_and_fields_mapping() -> None:
    fields = {"inputs/video.rgb": FieldView(_video_field())}
    metadata = {"source_id": {"window": "w1"}, "folds": [1, 2]}
    item = IndexItem(fields, _record(), metadata=metadata)
    metadata["source_id"]["window"] = "mutated"
    metadata["folds"].append(3)
    fields["targets/signal.bvp.reference"] = FieldView(_bvp_field())

    assert set(str(locator) for locator in item.fields) == {"inputs/video.rgb"}
    assert item.to_dict()["metadata"] == {
        "source_id": {"window": "w1"},
        "folds": [1, 2],
    }
    with pytest.raises(TypeError):
        item.fields[FieldLocator.parse("inputs/video.rgb")] = FieldView(_video_field())
    with pytest.raises(TypeError):
        item.metadata[MetadataKey("source_id")] = "mutated"
    with pytest.raises(TypeError):
        item.metadata[MetadataKey("source_id")]["window"] = "mutated"  # type: ignore[index]
    with pytest.raises(AttributeError):
        item.metadata[MetadataKey("folds")].append(3)  # type: ignore[attr-defined]


def test_index_item_has_value_equality_without_public_hash_contract() -> None:
    item = _item()

    assert item == _item()
    with pytest.raises(FrozenInstanceError):
        item.record = _record()  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(item)


def test_index_item_round_trips_through_primitive_dict() -> None:
    item = _item()
    serialized = item.to_dict()

    assert set(serialized["fields"]) == {
        "inputs/video.rgb",
        "targets/signal.bvp.reference",
    }
    assert serialized["record"] == _record().to_dict()
    assert serialized["metadata"] == {"source_id": "window-1"}
    assert IndexItem.from_dict(serialized) == item
    assert "item_id" not in serialized
    assert "fingerprint" not in serialized
    assert "payload" not in serialized


def test_index_item_rejects_invalid_record_or_empty_fields() -> None:
    with pytest.raises(InvalidIndexItemError):
        IndexItem({"inputs/video.rgb": FieldView(_video_field())}, object())  # type: ignore[arg-type]
    with pytest.raises(InvalidIndexItemError):
        IndexItem({}, _record())
    with pytest.raises(InvalidIndexItemError):
        IndexItem({"inputs/video.rgb": object()}, _record())  # type: ignore[dict-item]


def test_index_item_rejects_locator_view_key_mismatch() -> None:
    with pytest.raises(InvalidIndexItemError):
        IndexItem(
            {"inputs/video.rgb": FieldView(_bvp_field())},
            _record(),
        )


def test_index_item_rejects_views_missing_from_record_fields() -> None:
    record = RecordRef(DataSourceRef("fixture"), "record-1", {"video.rgb": _video_field()})

    with pytest.raises(InvalidIndexItemError):
        IndexItem(
            {"targets/signal.bvp.reference": FieldView(_bvp_field())},
            record,
        )


def test_index_item_rejects_invalid_metadata_and_serialized_shapes() -> None:
    with pytest.raises(InvalidIndexItemError):
        IndexItem(
            {"inputs/video.rgb": FieldView(_video_field())},
            _record(),
            metadata={"source_id": object()},
        )

    serialized = _item().to_dict()
    serialized["item_id"] = "stable-1"
    with pytest.raises(InvalidIndexItemError):
        IndexItem.from_dict(serialized)


def test_index_item_has_no_runtime_or_materialization_hooks() -> None:
    item = _item()

    for name in [
        "load",
        "build",
        "to_sample",
        "transform",
        "augment",
        "export",
        "train",
        "align",
    ]:
        assert not hasattr(item, name)
