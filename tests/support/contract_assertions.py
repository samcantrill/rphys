"""Private assertion helpers for repeated public-object contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.indexes import (
    DataSourceIndex,
    DataSourceIndexCodec,
    DataSourceIndexManifest,
)
from rphys.datasources.refs import RecordRef
from rphys.datasources.validation import DataSourceValidationReport


def assert_record_ref_round_trips(
    record: RecordRef,
    *,
    required_fields: Sequence[str],
) -> None:
    """Assert one public record descriptor serializes without payload state."""

    serialized = record.to_dict()
    restored = RecordRef.from_dict(serialized)

    assert restored.to_dict() == serialized
    assert set(serialized["fields"]).issuperset(required_fields)  # type: ignore[arg-type]
    assert_manifest_has_no_loaded_payloads(serialized)


def assert_scan_report_passed(
    report: DataSourceValidationReport,
    *,
    expected_record_count: int,
    required_evidence: Mapping[str, object],
) -> None:
    """Assert descriptor-only scan validation preserves expected evidence."""

    assert report.passed
    assert report.record_count == expected_record_count
    for key, expected in required_evidence.items():
        assert report.validation_evidence[key] == expected


def assert_index_manifest_round_trips(
    index: DataSourceIndex,
    *,
    expected_schema_version: str,
    expected_index_kind: str = "datasource_index",
) -> DataSourceIndexManifest:
    """Assert a public datasource index manifest is durable and payload-free."""

    codec = DataSourceIndexCodec()
    manifest = codec.to_manifest(index)
    serialized = manifest.to_dict()
    restored = DataSourceIndexManifest.from_dict(serialized)
    reloaded = codec.from_manifest(restored)

    assert restored.to_dict() == serialized
    assert reloaded.entry_at(0).to_dict() == index.entry_at(0).to_dict()
    assert manifest.schema_version == expected_schema_version
    assert manifest.index_kind == expected_index_kind
    assert manifest.content_fingerprint
    assert manifest.checksum
    assert_manifest_has_no_loaded_payloads(serialized)
    return manifest


def assert_manifest_matches_golden(
    manifest: DataSourceIndexManifest,
    golden: Mapping[str, object],
) -> None:
    """Assert a narrow golden freezes durable manifest facts only."""

    serialized = manifest.to_dict()

    assert golden["schema_version"] == serialized["schema_version"]
    assert golden["index_kind"] == serialized["index_kind"]
    assert golden["index_id"] == serialized["index_id"]
    assert golden["content_fingerprint"] == serialized["content_fingerprint"]
    assert golden["checksum"] == serialized["checksum"]
    assert golden["item_count"] == len(serialized["items"])  # type: ignore[arg-type]
    assert golden["entry_count"] == len(serialized["entries"])  # type: ignore[arg-type]
    for key in golden["forbidden_manifest_keys"]:  # type: ignore[index]
        assert not _contains_key(serialized, str(key))


def assert_sample_materializes_expected_fields(
    sample: object,
    expected_payloads: Mapping[str, object],
) -> None:
    """Assert public sample fields stay lazy until materialized."""

    for locator, expected_payload in expected_payloads.items():
        field = sample.field(locator)  # type: ignore[attr-defined]
        assert field.state is SampleFieldState.UNLOADED
        assert sample.require(locator) == expected_payload  # type: ignore[attr-defined]


def assert_manifest_has_no_loaded_payloads(value: object) -> None:
    """Assert durable descriptors contain no loaded payload or handle keys."""

    for forbidden_key in ("payload", "payloads", "loaded_payload", "open_handle"):
        assert not _contains_key(value, forbidden_key)


def _contains_key(value: object, target: str) -> bool:
    if isinstance(value, Mapping):
        return any(
            key == target or _contains_key(item, target)
            for key, item in value.items()
        )
    if isinstance(value, list | tuple):
        return any(_contains_key(item, target) for item in value)
    return False
