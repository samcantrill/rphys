from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import FilterChain, FilterDecision, build_view
from rphys.datasources.indexes import (
    IndexCandidate,
    IndexCandidatePlan,
    IndexCandidateView,
    build_index_candidates,
    filter_index_candidates,
)
from rphys.errors import InvalidIndexCandidateError
from rphys.io.fields import FieldView
from rphys.io.indexes import TemporalIndexSlice
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _candidate_view() -> IndexCandidateView:
    datasource = synthetic_datasource_ref()
    scan = DataSourceScanResult(
        datasource,
        [
            synthetic_record_ref(datasource, "subject-001/record-001"),
            synthetic_record_ref(datasource, "subject-002/record-001", include_bvp=False),
        ],
    )
    view = build_view(scan).view
    plan = IndexCandidatePlan(
        {
            "inputs/video.rgb": "video.rgb",
            "targets/signal.bvp.reference": "signal.bvp.reference",
        },
        field_indexes={"video.rgb": TemporalIndexSlice(0, 10)},
        metadata={"candidate_set": "trainable"},
    )
    return build_index_candidates(view, plan).view


def test_candidate_plan_builds_field_views_without_final_identity() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    scan = DataSourceScanResult(datasource, [record])
    view = build_view(scan).view
    plan = IndexCandidatePlan(
        {
            "inputs/video.rgb": "video.rgb",
            "targets/signal.bvp.reference": "signal.bvp.reference",
        },
        field_indexes={"video.rgb": TemporalIndexSlice(5, 15)},
        metadata={"purpose": "unit-test"},
    )

    result = build_index_candidates(view, plan)
    candidate = result.view.candidates[0]

    assert result.included_count == 1
    assert candidate.candidate_id == record.record_id
    assert candidate.record is record
    assert candidate.source_id == datasource.datasource_id
    assert candidate.metadata[MetadataKey("purpose")] == "unit-test"
    assert candidate.fields[FieldLocator.parse("inputs/video.rgb")] == FieldView(
        record.fields[FieldLocator.parse("inputs/video.rgb").key],
        TemporalIndexSlice(5, 15),
    )
    assert candidate.fields[FieldLocator.parse("targets/signal.bvp.reference")] == FieldView(
        record.fields[FieldLocator.parse("targets/signal.bvp.reference").key],
    )
    for forbidden in ["split", "entry_id", "fingerprint", "payload", "sample"]:
        assert not hasattr(candidate, forbidden)


def test_candidate_build_rejects_records_missing_required_fields() -> None:
    view = _candidate_view()

    assert [candidate.candidate_id for candidate in view.candidates] == [
        "subject-001/record-001"
    ]

    datasource = synthetic_datasource_ref()
    scan = DataSourceScanResult(
        datasource,
        [synthetic_record_ref(datasource, "missing-bvp", include_bvp=False)],
    )
    result = build_index_candidates(
        build_view(scan).view,
        IndexCandidatePlan({"targets/signal.bvp.reference": "signal.bvp.reference"}),
    )

    assert result.included_count == 0
    assert result.rejected_candidate_ids == {
        "missing-bvp": "missing_fields:signal.bvp.reference",
    }


def test_candidate_filtering_is_before_group_split_and_non_mutating() -> None:
    view = _candidate_view()

    class CandidateFilter:
        def evaluate(self, candidate: object) -> FilterDecision:
            if candidate.candidate_id == "subject-001/record-001":  # type: ignore[attr-defined]
                return FilterDecision(True)
            return FilterDecision(False, "not_selected")

    result = filter_index_candidates(
        view,
        FilterChain([CandidateFilter()], target_kind="candidate"),
    )

    assert result.view is not view
    assert result.view.candidates == view.candidates
    assert result.rejected_candidate_ids == {}
    assert not hasattr(result.view.candidates[0], "split")


def test_candidate_objects_are_immutable_and_serialize_without_manifest_fields() -> None:
    candidate = _candidate_view().candidates[0]
    payload = candidate.to_dict()

    assert "entry_id" not in payload
    assert "fingerprint" not in payload
    assert "split" not in payload
    with pytest.raises(FrozenInstanceError):
        candidate.candidate_id = "mutated"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(candidate)


def test_candidate_plan_and_candidate_reject_invalid_shapes() -> None:
    record = synthetic_record_ref()

    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidatePlan({})
    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidatePlan({"inputs/video.rgb": "signal.bvp.reference"})
    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidatePlan(
            {"inputs/video.rgb": "video.rgb"},
            field_indexes={"video.rgb": object()},  # type: ignore[dict-item]
        )
    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidate("", record, {"inputs/video.rgb": FieldView(record.fields["video.rgb"])})
    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidate("candidate", object(), {})  # type: ignore[arg-type]
    with pytest.raises(InvalidIndexCandidateError):
        IndexCandidateView([object()])  # type: ignore[list-item]
