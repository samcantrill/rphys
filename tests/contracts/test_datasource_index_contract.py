from __future__ import annotations

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.index_items import IndexItem
from rphys.datasources.indexes import (
    DataSourceIndex,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_datasource_index_contract_yields_items_and_entries_separately() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    index = IndexBuilder(IndexPlan("idx")).build(candidates).index

    assert isinstance(index, DataSourceIndex)
    assert isinstance(index[0], IndexItem)
    assert index.entry_at(0).candidate_id == record.record_id
    assert index[0].metadata == {}
    assert index.entry_at(0).fingerprint


def test_datasource_index_contract_preserves_field_native_windows_only() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    entry = IndexBuilder(IndexPlan("idx")).build(candidates).index.entry_at(0)

    assert entry.field_windows == {"inputs/video.rgb": None}
    assert not hasattr(entry, "seconds")
    assert not hasattr(entry, "alignment")
