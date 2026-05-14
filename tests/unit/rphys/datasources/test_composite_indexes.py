from __future__ import annotations

import json

import pytest

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.index_items import IndexItem
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    DataSourceIndex,
    DataSourceIndexCodec,
    IndexBuilder,
    IndexCandidatePlan,
    IndexPlan,
    build_index_candidates,
)
from rphys.errors import InvalidIndexCandidateError
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def _index(
    index_id: str,
    *,
    datasource_id: str,
    record_id: str,
    subject_id: str,
    metadata: dict[str, object] | None = None,
) -> DataSourceIndex:
    datasource = synthetic_datasource_ref(datasource_id)
    record = synthetic_record_ref(
        datasource,
        record_id,
        subject_id=subject_id,
    )
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan({"inputs/video.rgb": "video.rgb"}),
    ).view
    return IndexBuilder(IndexPlan(index_id, metadata=metadata)).build(candidates).index


def test_composite_index_yields_ordered_items_and_source_sidecars() -> None:
    child_a = _index(
        "child-a",
        datasource_id="dataset-a",
        record_id="subject-a/record-001",
        subject_id="subject-a",
        metadata={"member": "a"},
    )
    child_b = _index(
        "child-b",
        datasource_id="dataset-b",
        record_id="subject-b/record-001",
        subject_id="subject-b",
        metadata={"member": "b"},
    )

    composite = CompositeDataSourceIndex(
        "combined",
        {"a": child_a, "b": child_b},
        metadata={"cohort": "synthetic"},
    )

    assert len(composite) == 2
    assert isinstance(composite[0], IndexItem)
    assert [item.to_dict() for item in composite] == [
        child_a[0].to_dict(),
        child_b[0].to_dict(),
    ]

    first_entry = composite.entry_at(0)
    assert first_entry.index_id == "combined"
    assert first_entry.position == 0
    assert first_entry.source_key == "a"
    assert first_entry.child_index_id == child_a.index_id
    assert first_entry.child_entry_id == child_a.entry_at(0).entry_id
    assert first_entry.child_position == 0
    assert first_entry.to_dict()["child_metadata"] == {"member": "a"}
    assert first_entry.child_index_fingerprint

    assert composite[0].metadata == child_a[0].metadata == {}
    assert "source_key" not in composite[0].to_dict()["metadata"]


def test_composite_index_fingerprint_reflects_child_order() -> None:
    child_a = _index(
        "child-a",
        datasource_id="dataset-a",
        record_id="subject-a/record-001",
        subject_id="subject-a",
    )
    child_b = _index(
        "child-b",
        datasource_id="dataset-b",
        record_id="subject-b/record-001",
        subject_id="subject-b",
    )

    ab = CompositeDataSourceIndex("combined", {"a": child_a, "b": child_b})
    ba = CompositeDataSourceIndex("combined", {"b": child_b, "a": child_a})

    assert ab.fingerprint != ba.fingerprint
    assert [entry.source_key for entry in ab.entries] == ["a", "b"]
    assert [entry.source_key for entry in ba.entries] == ["b", "a"]


def test_composite_manifest_round_trip_preserves_source_provenance() -> None:
    child_a = _index(
        "child-a",
        datasource_id="dataset-a",
        record_id="subject-a/record-001",
        subject_id="subject-a",
        metadata={"member": "a"},
    )
    child_b = _index(
        "child-b",
        datasource_id="dataset-b",
        record_id="subject-b/record-001",
        subject_id="subject-b",
        metadata={"member": "b"},
    )
    composite = CompositeDataSourceIndex("combined", {"a": child_a, "b": child_b})
    codec = DataSourceIndexCodec()

    payload = codec.dumps(composite)
    loaded = codec.loads(payload)
    manifest = codec.to_manifest(composite)

    assert isinstance(loaded, CompositeDataSourceIndex)
    assert manifest.index_kind == "composite_datasource_index"
    assert [dict(child)["source_key"] for child in manifest.children] == ["a", "b"]
    assert list(loaded.sources) == ["a", "b"]
    assert [entry.to_dict() for entry in loaded.entries] == [
        entry.to_dict() for entry in composite.entries
    ]
    assert loaded[1].to_dict() == child_b[0].to_dict()
    assert "ConcatDataSourceIndex" not in payload


def test_composite_index_rejects_invalid_sources_and_corrupt_manifests() -> None:
    child = _index(
        "child-a",
        datasource_id="dataset-a",
        record_id="subject-a/record-001",
        subject_id="subject-a",
    )
    composite = CompositeDataSourceIndex("combined", {"a": child})
    codec = DataSourceIndexCodec()

    with pytest.raises(InvalidIndexCandidateError):
        CompositeDataSourceIndex("bad", {})
    with pytest.raises(InvalidIndexCandidateError):
        CompositeDataSourceIndex("bad", {"a": object()})  # type: ignore[dict-item]

    manifest = json.loads(codec.dumps(composite))
    manifest["children"][0]["child_index_fingerprint"] = "0" * 64
    with pytest.raises(InvalidIndexCandidateError):
        codec.loads(json.dumps(manifest))
