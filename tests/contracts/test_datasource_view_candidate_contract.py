from __future__ import annotations

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import FilterChain, FilterDecision, build_view
from rphys.datasources.index_items import IndexItem
from rphys.datasources.indexes import IndexCandidatePlan, build_index_candidates
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_view_candidate_pipeline_order_preserves_descriptor_purity() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    scan = DataSourceScanResult(datasource, [record])

    view = build_view(scan).view
    candidates = build_index_candidates(
        view,
        IndexCandidatePlan(
            {
                "inputs/video.rgb": "video.rgb",
                "targets/signal.bvp.reference": "signal.bvp.reference",
            }
        ),
    ).view

    assert view.records[0] is record
    assert candidates.candidates[0].record is record
    assert scan.records[0].metadata == record.metadata
    assert not hasattr(candidates.candidates[0], "split")
    assert not hasattr(candidates.candidates[0], "entry_id")


def test_record_filters_run_before_candidate_construction() -> None:
    datasource = synthetic_datasource_ref()
    records = [
        synthetic_record_ref(datasource, "subject-001/record-001"),
        synthetic_record_ref(datasource, "subject-002/record-001"),
    ]
    view = build_view(DataSourceScanResult(datasource, records)).view
    filtered = FilterChain(
        [
            lambda record: (
                record.record_id == "subject-001/record-001",  # type: ignore[attr-defined]
                "not_subject_001",
            )
        ],
        target_kind="record",
    ).apply(view.records, id_of=lambda record: record.record_id)  # type: ignore[attr-defined]
    filtered_view = type(view)(view.datasource, filtered.included)  # type: ignore[arg-type]

    candidates = build_index_candidates(
        filtered_view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view

    assert [candidate.candidate_id for candidate in candidates.candidates] == [
        "subject-001/record-001"
    ]
    assert filtered.excluded_ids == {"subject-002/record-001": "not_subject_001"}


def test_candidate_fields_can_form_index_items_without_metadata_identity() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidate = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view.candidates[0]

    item = IndexItem(candidate.fields, candidate.record)

    assert item.record is record
    assert item.metadata == {}
    assert not hasattr(item, "entry_id")
    assert not hasattr(item, "fingerprint")
