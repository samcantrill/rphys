from __future__ import annotations

import pytest

from rphys.data.metadata import SOURCE_ID, SUBJECT_ID
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import IndexCandidatePlan, build_index_candidates
from rphys.datasources.splits import GroupBuilder, GroupPlan, SplitBuilder, SplitPlan
from rphys.errors import InvalidSplitAssignmentError
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_group_disjoint_split_contract_preserves_analysis_groups() -> None:
    datasource = synthetic_datasource_ref()
    records = [
        synthetic_record_ref(datasource, "subject-001/record-001", subject_id="subject-001"),
        synthetic_record_ref(datasource, "subject-002/record-001", subject_id="subject-002"),
    ]
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, records)).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    groups = GroupBuilder(
        GroupPlan({"subject": SUBJECT_ID, "source": SOURCE_ID})
    ).build(candidates)
    splits = SplitBuilder(
        SplitPlan(
            split_group="subject",
            group_to_split={"subject-001": "train", "subject-002": "test"},
        )
    ).build(groups)

    assert splits.assignments["subject-001/record-001"].groups["source"] == "synthetic"
    assert splits.assignments["subject-002/record-001"].groups["source"] == "synthetic"


def test_split_contract_fails_before_silent_candidate_leakage() -> None:
    datasource = synthetic_datasource_ref()
    records = [
        synthetic_record_ref(datasource, "subject-001/a", subject_id="subject-001"),
        synthetic_record_ref(datasource, "subject-001/b", subject_id="subject-001"),
    ]
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, records)).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    groups = GroupBuilder(GroupPlan({"subject": SUBJECT_ID})).build(candidates)

    with pytest.raises(InvalidSplitAssignmentError):
        SplitBuilder(
            SplitPlan(split_group="session", group_to_split={"a": "train"})
        ).build(groups)
