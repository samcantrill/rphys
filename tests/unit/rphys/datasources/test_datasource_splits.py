from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.metadata import GROUP, SOURCE_ID, SUBJECT_ID
from rphys.data.splits import SplitName
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import (
    IndexCandidatePlan,
    IndexCandidateView,
    build_index_candidates,
)
from rphys.datasources.splits import (
    CandidateGroupAssignment,
    GroupBuilder,
    GroupPlan,
    GroupResult,
    SplitAssignment,
    SplitBuilder,
    SplitPlan,
    SplitResult,
)
from rphys.errors import InvalidGroupAssignmentError, InvalidSplitAssignmentError
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _candidate_view() -> IndexCandidateView:
    datasource = synthetic_datasource_ref()
    records = [
        synthetic_record_ref(datasource, "subject-001/record-001", subject_id="subject-001"),
        synthetic_record_ref(datasource, "subject-002/record-001", subject_id="subject-002"),
    ]
    return build_index_candidates(
        build_view(DataSourceScanResult(datasource, records)).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view


def test_group_builder_extracts_multiple_groups_and_counts() -> None:
    result = GroupBuilder(
        GroupPlan(
            {
                "subject": SUBJECT_ID,
                "source": SOURCE_ID,
            }
        )
    ).build(_candidate_view())

    assert set(result.assignments) == {
        "subject-001/record-001",
        "subject-002/record-001",
    }
    assert result.assignments["subject-001/record-001"].groups == {
        "subject": "subject-001",
        "source": "synthetic",
    }
    assert result.counts["subject"] == {"subject-001": 1, "subject-002": 1}
    assert result.counts["source"] == {"synthetic": 2}


def test_group_builder_fails_loudly_for_missing_required_groups() -> None:
    view = _candidate_view()

    with pytest.raises(InvalidGroupAssignmentError) as exc_info:
        GroupBuilder(GroupPlan({"analysis": GROUP})).build(view)

    assert exc_info.value.context["rejected_candidate_ids"] == {
        "subject-001/record-001": "missing_groups:analysis",
        "subject-002/record-001": "missing_groups:analysis",
    }


def test_split_builder_assigns_explicit_group_disjoint_splits() -> None:
    group_result = GroupBuilder(GroupPlan({"subject": SUBJECT_ID, "source": SOURCE_ID})).build(
        _candidate_view()
    )
    split_result = SplitBuilder(
        SplitPlan(
            split_group="subject",
            group_to_split={"subject-001": "train", "subject-002": "valid"},
        )
    ).build(group_result)

    assert split_result.assignments["subject-001/record-001"].split == SplitName("train")
    assert split_result.assignments["subject-001/record-001"].groups == {
        "subject": "subject-001",
        "source": "synthetic",
    }
    assert split_result.counts == {SplitName("train"): 1, SplitName("valid"): 1}
    assert split_result.rejected_candidate_ids == {}


def test_split_builder_requires_explicit_assignments() -> None:
    group_result = GroupBuilder(GroupPlan({"subject": SUBJECT_ID})).build(_candidate_view())

    with pytest.raises(InvalidSplitAssignmentError) as exc_info:
        SplitBuilder(
            SplitPlan(split_group="subject", group_to_split={"subject-001": "train"})
        ).build(group_result)

    assert exc_info.value.context["rejected_candidate_ids"] == {
        "subject-002/record-001": "unassigned_split_group:subject-002",
    }


def test_split_result_detects_leakage_for_same_group_across_splits() -> None:
    with pytest.raises(InvalidSplitAssignmentError):
        SplitResult(
            {
                "a": SplitAssignment(
                    "a",
                    split="train",
                    split_group="subject",
                    split_group_value="subject-001",
                    groups={"subject": "subject-001"},
                ),
                "b": SplitAssignment(
                    "b",
                    split="valid",
                    split_group="subject",
                    split_group_value="subject-001",
                    groups={"subject": "subject-001"},
                ),
            }
        )


def test_group_and_split_records_are_immutable() -> None:
    assignment = CandidateGroupAssignment("candidate", {"subject": "subject-001"})
    split_assignment = SplitAssignment(
        "candidate",
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        groups=assignment.groups,
    )

    with pytest.raises(FrozenInstanceError):
        assignment.candidate_id = "mutated"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(assignment)
    with pytest.raises(FrozenInstanceError):
        split_assignment.split_group = "mutated"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(split_assignment)


def test_group_and_split_plans_reject_invalid_shapes() -> None:
    with pytest.raises(InvalidGroupAssignmentError):
        GroupPlan({})
    with pytest.raises(InvalidGroupAssignmentError):
        GroupPlan({"subject": SUBJECT_ID}, required_groups=["missing"])
    with pytest.raises(InvalidSplitAssignmentError):
        SplitPlan(split_group="subject", group_to_split={})
    with pytest.raises(InvalidSplitAssignmentError):
        SplitBuilder(object())  # type: ignore[arg-type]
