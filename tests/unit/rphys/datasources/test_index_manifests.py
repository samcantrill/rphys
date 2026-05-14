from __future__ import annotations

import json

import pytest

from rphys.datasources.adapters import DataSourceScanResult
from rphys.datasources.filters import build_view
from rphys.datasources.indexes import (
    DataSourceIndexCodec,
    DataSourceIndexManifest,
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


def _index():
    datasource = synthetic_datasource_ref()
    record = synthetic_record_ref(datasource)
    candidates = build_index_candidates(
        build_view(DataSourceScanResult(datasource, [record])).view,
        IndexCandidatePlan(
            {
                "inputs/video.rgb": "video.rgb",
                "targets/signal.bvp.reference": "signal.bvp.reference",
            }
        ),
    ).view
    return IndexBuilder(IndexPlan("idx", metadata={"release": "stage-5"})).build(
        candidates
    ).index


def test_manifest_round_trip_preserves_items_entries_and_resources() -> None:
    index = _index()
    codec = DataSourceIndexCodec()

    payload = codec.dumps(index)
    loaded = codec.loads(payload)

    assert payload == codec.dumps(index)
    assert loaded.index_id == index.index_id
    assert loaded[0].to_dict() == index[0].to_dict()
    assert loaded.entry_at(0).to_dict() == index.entry_at(0).to_dict()
    assert loaded[0].record.fields["video.rgb"].resources[0].uri.startswith("memory://")
    assert "pickle" not in payload


def test_manifest_fingerprint_and_checksum_are_distinct() -> None:
    manifest = DataSourceIndexCodec().to_manifest(_index())

    assert manifest.schema_version == "rphys.datasource_index.v1"
    assert len(manifest.content_fingerprint) == 64
    assert len(manifest.checksum) == 64
    assert manifest.content_fingerprint != manifest.checksum
    assert manifest.to_dict()["content_fingerprint"] == manifest.content_fingerprint


def test_manifest_rejects_unsupported_schema_and_mismatches() -> None:
    manifest = DataSourceIndexCodec().to_manifest(_index()).to_dict()

    bad_version = dict(manifest)
    bad_version["schema_version"] = "rphys.datasource_index.v0"
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexManifest.from_dict(bad_version)

    bad_fingerprint = dict(manifest)
    bad_fingerprint["content_fingerprint"] = "0" * 64
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexManifest.from_dict(bad_fingerprint)

    bad_checksum = dict(manifest)
    bad_checksum["checksum"] = "0" * 64
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexManifest.from_dict(bad_checksum)


def test_codec_rejects_ambiguous_or_corrupt_manifest_shapes() -> None:
    manifest = DataSourceIndexCodec().to_manifest(_index()).to_dict()
    manifest["unexpected"] = True

    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexManifest.from_dict(manifest)
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexCodec().loads(json.dumps({"schema_version": "rphys.datasource_index.v1"}))
    with pytest.raises(InvalidIndexCandidateError):
        DataSourceIndexCodec().to_manifest(object())  # type: ignore[arg-type]


def test_codec_writes_and_reads_json_manifest_file(tmp_path) -> None:
    index = _index()
    path = tmp_path / "index.json"
    codec = DataSourceIndexCodec()

    codec.dump(index, path)
    loaded = codec.load(path)

    assert path.read_text(encoding="utf-8").startswith("{")
    assert loaded[0].to_dict() == index[0].to_dict()
