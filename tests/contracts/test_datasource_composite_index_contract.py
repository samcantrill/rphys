from __future__ import annotations

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    DataSourceIndexCodec,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _one_record_index(index_id: str, datasource_id: str):
    datasource = synthetic_datasource_ref(datasource_id)
    record = synthetic_record_ref(datasource, f"{datasource_id}/record-001")
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    return IndexBuilder(IndexPlan(index_id)).build(candidates).index


def test_composite_index_contract_preserves_child_identity_outside_items() -> None:
    left = _one_record_index("left-index", "left-source")
    right = _one_record_index("right-index", "right-source")
    composite = CompositeDataSourceIndex("combined", {"left": left, "right": right})

    assert [item.to_dict() for item in composite] == [
        left[0].to_dict(),
        right[0].to_dict(),
    ]
    assert composite.entry_at(0).source_key == "left"
    assert composite.entry_at(0).child_index_id == "left-index"
    assert composite.entry_at(0).child_position == 0
    assert composite.entry_at(1).source_key == "right"
    assert composite.entry_at(1).child_index_fingerprint
    assert composite[0].metadata == {}


def test_composite_index_contract_round_trips_through_manifest() -> None:
    left = _one_record_index("left-index", "left-source")
    right = _one_record_index("right-index", "right-source")
    composite = CompositeDataSourceIndex("combined", {"left": left, "right": right})
    codec = DataSourceIndexCodec()

    loaded = codec.loads(codec.dumps(composite))

    assert isinstance(loaded, CompositeDataSourceIndex)
    assert list(loaded.sources) == ["left", "right"]
    assert [entry.to_dict() for entry in loaded.entries] == [
        entry.to_dict() for entry in composite.entries
    ]
