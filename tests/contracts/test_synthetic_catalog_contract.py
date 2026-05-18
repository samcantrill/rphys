from __future__ import annotations

import math

import pytest

from rphys.data.metadata import GROUP, SPLIT, SUBJECT_ID
from rphys.datasources.refs import RecordRef
from rphys.datasources.validation import ValidationIOPolicy, validate_scan_result

from tests.support.synthetic_catalog import (
    ALL_FIELD_KEYS,
    BVP_KEY,
    OPTIONAL_FIELD_KEYS,
    REQUIRED_FIELD_KEYS,
    TIMESTAMPS_KEY,
    VIDEO_KEY,
    make_synthetic_scenario,
)
from tests.support.synthetic_edges import make_edge_variant


def test_synthetic_catalog_builds_public_descriptors_with_provenance() -> None:
    scenario = make_synthetic_scenario(
        datasource_count=2,
        subjects=("subject-001", "subject-002"),
        records_per_subject=2,
    )

    assert len(scenario.datasources) == 2
    assert len(scenario.records) == 8
    assert set(str(key) for key in scenario.records[0].fields) == set(ALL_FIELD_KEYS)
    assert set(OPTIONAL_FIELD_KEYS).issubset(
        {str(key) for key in scenario.records[0].fields}
    )

    record = scenario.records[0]
    assert isinstance(RecordRef.from_dict(record.to_dict()), RecordRef)
    assert record.metadata[SUBJECT_ID] == "subject-001"
    assert record.metadata[GROUP] == "cohort-1"
    assert record.metadata[SPLIT] == "train"
    assert record.fields[VIDEO_KEY].resources[0].uri.startswith("memory://stage14/")

    video = scenario.field(record.record_id, VIDEO_KEY)
    bvp = scenario.field(record.record_id, BVP_KEY)
    timestamps = scenario.field(record.record_id, TIMESTAMPS_KEY)

    assert video.metadata["sample_rate_hz"] == 30.0
    assert video.metadata["alignment_group"] == "video_bvp"
    assert bvp.metadata["waveform.frequency_hz"] == 1.2
    assert bvp.metadata["heart_rate_bpm"] == 72.0
    assert bvp.sample_rate_hz == 30.0
    assert len(set(bvp.payload)) > 1
    assert timestamps.payload == timestamps.timestamps_s
    assert record.fields[BVP_KEY].metadata["payload_fingerprint"] == bvp.payload_fingerprint

    scan_result = scenario.scan_result_for("synthetic-source-001")
    report = validate_scan_result(
        scan_result,
        spec=scenario.spec_for("synthetic-source-001"),
        policy=ValidationIOPolicy.no_io(),
        required_metadata=(SUBJECT_ID, GROUP, SPLIT),
    )

    assert report.passed
    assert report.record_count == 4
    assert report.field_count == 4 * len(ALL_FIELD_KEYS)
    assert report.validation_evidence["fixture_catalog"] == "stage14.synthetic_catalog.v1"
    assert report.validation_evidence["datasource_count"] == 2


@pytest.mark.parametrize(
    ("name", "affected_field", "failure_family"),
    [
        ("missing_field", BVP_KEY, "missing_field"),
        ("short_record", BVP_KEY, "short_input"),
        ("flat_signal", BVP_KEY, "flat_signal"),
        ("nan_signal", BVP_KEY, "invalid_value"),
        ("inf_signal", BVP_KEY, "invalid_value"),
        ("invalid_sample_rate", BVP_KEY, "invalid_sample_rate"),
        ("timestamp_drift", TIMESTAMPS_KEY, "timestamp_drift"),
        ("irregular_timestamps", TIMESTAMPS_KEY, "irregular_timestamps"),
        ("misalignment", BVP_KEY, "field_misalignment"),
    ],
)
def test_synthetic_edge_variants_record_scientific_failure_evidence(
    name: str,
    affected_field: str,
    failure_family: str,
) -> None:
    variant = make_edge_variant(name)

    assert variant.affected_field == affected_field
    assert variant.expected_failure_family == failure_family
    assert variant.evidence
    assert variant.scan_result().validation_evidence["edge_variant"] == name


def test_missing_field_edge_variant_fails_public_scan_validation() -> None:
    variant = make_edge_variant("missing_field")

    report = validate_scan_result(
        variant.scan_result(),
        spec=variant.spec(required_fields=REQUIRED_FIELD_KEYS),
        policy=ValidationIOPolicy.no_io(),
    )

    assert not report.passed
    assert any(
        issue.code == "field.missing" and str(issue.field_key) == BVP_KEY
        for issue in report.errors
    )


def test_invalid_value_edge_payloads_stay_inspectable_without_descriptor_coercion() -> None:
    nan_variant = make_edge_variant("nan_signal")
    inf_variant = make_edge_variant("inf_signal")

    assert nan_variant.invalid_payload is not None
    assert math.isnan(nan_variant.invalid_payload[1])
    assert inf_variant.invalid_payload is not None
    assert math.isinf(inf_variant.invalid_payload[1])
    assert nan_variant.records[0].fields[BVP_KEY].metadata["edge.invalid_values"] == "nan"
    assert inf_variant.records[0].fields[BVP_KEY].metadata["edge.invalid_values"] == "inf"
