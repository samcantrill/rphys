from __future__ import annotations

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import (
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


def test_datasource_index_manifest_contract_round_trips_without_pickle() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    index = IndexBuilder(IndexPlan("idx")).build(candidates).index
    codec = DataSourceIndexCodec()

    payload = codec.dumps(index)
    loaded = codec.loads(payload)

    assert loaded[0].to_dict() == index[0].to_dict()
    assert loaded.entry_at(0).fingerprint == index.entry_at(0).fingerprint
    assert "pickle" not in payload.lower()
    assert "rphys.datasource_index.v1" in payload


def test_manifest_contract_keeps_content_fingerprint_separate_from_checksum() -> None:
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    manifest = DataSourceIndexCodec().to_manifest(
        IndexBuilder(IndexPlan("idx")).build(candidates).index
    )

    assert manifest.content_fingerprint
    assert manifest.checksum
    assert manifest.content_fingerprint != manifest.checksum
