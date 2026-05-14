from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.metadata import MetadataKey, SUBJECT_ID
from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import (
    DataSourceView,
    DataSourceViewPlan,
    FilterChain,
    FilterDecision,
    build_view,
)
from rphys.errors import InvalidDataSourceFilterError, InvalidDataSourceViewError
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _scan() -> DataSourceScanResult:
    datasource = synthetic_datasource_ref()
    return DataSourceScanResult(
        datasource,
        [
            synthetic_record_ref(datasource, "subject-001/record-001"),
            synthetic_record_ref(datasource, "subject-002/record-001", subject_id="subject-002"),
        ],
    )


def test_view_plan_selects_records_without_mutating_scan_result() -> None:
    scan = _scan()
    original_records = scan.records
    plan = DataSourceViewPlan(
        include_record_ids=["subject-001/record-001", "missing"],
        metadata={"cohort": "tiny"},
    )

    result = build_view(scan, plan)

    assert scan.records is original_records
    assert result.included_count == 1
    assert [record.record_id for record in result.view.records] == [
        "subject-001/record-001"
    ]
    assert result.excluded_record_ids == {
        "subject-002/record-001": "not_selected",
        "missing": "missing_from_scan",
    }
    assert result.view.metadata[MetadataKey("cohort")] == "tiny"
    assert result.view.records[0] is scan.records[0]


def test_view_plan_round_trips_and_stays_immutable() -> None:
    plan = DataSourceViewPlan(include_record_ids=["record-1"], metadata={"fold": 1})

    assert DataSourceViewPlan.from_dict(plan.to_dict()) == plan
    with pytest.raises(FrozenInstanceError):
        plan.include_record_ids = None  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(plan)


def test_view_rejects_invalid_inputs() -> None:
    scan = _scan()
    other = synthetic_record_ref(synthetic_datasource_ref("other"))

    with pytest.raises(InvalidDataSourceViewError):
        DataSourceView("datasource", scan.records)  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceViewError):
        DataSourceView(scan.datasource, [object()])  # type: ignore[list-item]
    with pytest.raises(InvalidDataSourceViewError):
        DataSourceView(scan.datasource, [other])
    with pytest.raises(InvalidDataSourceViewError):
        DataSourceViewPlan(include_record_ids=["record-1", "record-1"])
    with pytest.raises(InvalidDataSourceViewError):
        build_view(object())  # type: ignore[arg-type]


def test_filter_chain_applies_structural_filters_in_order() -> None:
    scan = _scan()
    view = build_view(scan).view

    class SubjectFilter:
        def evaluate(self, record: object) -> FilterDecision:
            subject = record.metadata[SUBJECT_ID]  # type: ignore[attr-defined]
            if subject == "subject-001":
                return FilterDecision(True)
            return FilterDecision(False, "subject_not_selected")

    result = FilterChain([SubjectFilter()], target_kind="record").apply(
        view.records,
        id_of=lambda record: record.record_id,  # type: ignore[attr-defined]
    )

    assert result.target_kind == "record"
    assert result.included == (view.records[0],)
    assert result.excluded_ids == {
        "subject-002/record-001": "subject_not_selected",
    }


def test_filter_chain_accepts_callables_and_tuple_decisions() -> None:
    scan = _scan()
    view = build_view(scan).view
    chain = FilterChain(
        [
            lambda record: (
                record.record_id.endswith("record-001"),  # type: ignore[attr-defined]
                "not_record_001",
            )
        ],
        target_kind="record",
    )

    result = chain.apply(view.records, id_of=lambda record: record.record_id)  # type: ignore[attr-defined]

    assert result.included == view.records
    assert result.excluded_ids == {}


def test_filter_chain_rejects_invalid_filters_or_results() -> None:
    with pytest.raises(InvalidDataSourceFilterError):
        FilterChain([object()], target_kind="record")
    with pytest.raises(InvalidDataSourceFilterError):
        FilterChain([lambda target: "yes"], target_kind="record").apply(
            [object()],
            id_of=lambda _: "target",
        )
    with pytest.raises(InvalidDataSourceFilterError):
        FilterChain([lambda target: True], target_kind="")
