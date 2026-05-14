from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.metadata import SOURCE_ID, SUBJECT_ID
from rphys.data.splits import SplitName
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.index_items import IndexItem
from rphys.datasources.indexes import (
    DataSourceIndex,
    DataSourceIndexEntry,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.errors import InvalidIndexCandidateError
from rphys.io.indexes import TemporalIndexSlice
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _index_result():
    datasource = synthetic_datasource_ref()
    records = [
        synthetic_record_ref(datasource, "subject-001/record-001", subject_id="subject-001"),
        synthetic_record_ref(datasource, "subject-002/record-001", subject_id="subject-002"),
    ]
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, records)).view,
        IndexCandidatePlan(
            {
                "inputs/video.rgb": "video.rgb",
                "targets/signal.bvp.reference": "signal.bvp.reference",
            },
            field_indexes={"video.rgb": TemporalIndexSlice(0, 10)},
            metadata={"window": "native-0-10"},
        ),
    ).view
    groups = GroupBuilder(GroupPlan({"subject": SUBJECT_ID, "source": SOURCE_ID})).build(
        candidates
    )
    splits = SplitBuilder(
        SplitPlan(
            split_group="subject",
            group_to_split={"subject-001": "train", "subject-002": "valid"},
        )
    ).build(groups)
    return IndexBuilder(IndexPlan("synthetic-index", metadata={"stage": 5})).build(
        candidates,
        group_result=groups,
        split_result=splits,
    )


def test_index_builder_returns_ordered_items_and_sidecar_entries() -> None:
    result = _index_result()
    index = result.index

    assert len(index) == 2
    assert result.report.accepted_count == 2
    assert isinstance(index[0], IndexItem)
    assert list(iter(index)) == [index[0], index[1]]
    assert index[0].metadata == {}

    entry = index.entry_at(0)
    assert entry.position == 0
    assert entry.entry_id == "synthetic-index:0"
    assert entry.candidate_id == "subject-001/record-001"
    assert entry.split == "train"
    assert entry.groups == {"subject": "subject-001", "source": "synthetic"}
    assert entry.field_windows["inputs/video.rgb"] == {
        "type": "temporal_index_slice",
        "start": 0,
        "stop": 10,
        "step": 1,
    }
    assert len(entry.fingerprint) == 64


def test_index_entries_are_stable_sidecars_not_item_metadata() -> None:
    index = _index_result().index
    item = index[0]
    entry = index.entry_at(0)

    assert entry.record_id == item.record.record_id
    assert "entry_id" not in item.to_dict()["metadata"]
    assert "fingerprint" not in item.to_dict()["metadata"]
    assert not hasattr(item, "entry_id")
    assert not hasattr(item, "fingerprint")


def test_entry_fingerprint_is_deterministic_for_stable_payload() -> None:
    entry = _index_result().index.entry_at(0)
    clone = DataSourceIndexEntry(
        index_id=entry.index_id,
        entry_id=entry.entry_id,
        position=entry.position,
        candidate_id=entry.candidate_id,
        record_id=entry.record_id,
        datasource_id=entry.datasource_id,
        source_id=entry.source_id,
        groups=entry.groups,
        split=entry.split,
        split_group=entry.split_group,
        split_group_value=entry.split_group_value,
        field_windows=entry.field_windows,
        metadata=entry.metadata,
    )

    assert clone.fingerprint == entry.fingerprint
    assert clone.to_dict() == entry.to_dict()


def test_index_objects_are_immutable_and_validate_alignment() -> None:
    index = _index_result().index
    entry = index.entry_at(0)

    with pytest.raises(FrozenInstanceError):
        entry.position = 3  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(index)
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndex("bad", [index[0]], [])
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndex("bad", [object()], [])  # type: ignore[list-item]


def test_index_builder_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidIndexCandidateError):
        IndexPlan("")
    with pytest.raises(InvalidIndexCandidateError):
        IndexBuilder(object())  # type: ignore[arg-type]
    with pytest.raises(InvalidIndexCandidateError):
        IndexBuilder(IndexPlan("idx")).build(object())  # type: ignore[arg-type]
    assert SplitName("train") == "train"
