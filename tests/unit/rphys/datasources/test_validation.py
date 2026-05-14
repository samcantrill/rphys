from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.keys import DataKey
from rphys.datasources.adapters import DataSourceScanResult, DataSourceSpec
from rphys.datasources.validation import (
    DataSourceValidationReport,
    ValidationIOPolicy,
    ValidationIssue,
    validate_scan_result,
)
from rphys.errors import InvalidDataSourceValidationError
from tests.support.synthetic_datasources import (
    synthetic_datasource_ref,
    synthetic_record_ref,
)


def test_validation_io_policy_modes_are_explicit() -> None:
    no_io = ValidationIOPolicy.no_io()
    probe_only = ValidationIOPolicy.probe_only()
    explicit = ValidationIOPolicy.explicit_validation_io()

    assert no_io.mode == "no_io"
    assert not no_io.allows_probe
    assert not no_io.allows_validation_io
    assert probe_only.allows_probe
    assert not probe_only.allows_validation_io
    assert explicit.allows_probe
    assert explicit.allows_validation_io
    assert ValidationIOPolicy.from_dict(explicit.to_dict()) == explicit


def test_validation_io_policy_rejects_hidden_probe_or_payload_io() -> None:
    with pytest.raises(InvalidDataSourceValidationError):
        validate_scan_result(
            DataSourceScanResult(synthetic_datasource_ref()),
            policy=ValidationIOPolicy.no_io(),
            require_probe=True,
        )

    with pytest.raises(InvalidDataSourceValidationError):
        validate_scan_result(
            DataSourceScanResult(synthetic_datasource_ref()),
            policy=ValidationIOPolicy.probe_only(),
            require_validation_io=True,
        )


def test_validation_issue_preserves_primitive_context_and_round_trips() -> None:
    issue = ValidationIssue(
        "field.missing",
        "missing BVP",
        severity="error",
        scope="field",
        datasource_id="synthetic-rppg",
        record_id="subject-001/record-001",
        field_key="signal.bvp.reference",
        context={"candidates": ["video.rgb"]},
    )

    assert issue.field_key == DataKey("signal.bvp.reference")
    assert issue.context["candidates"] == ("video.rgb",)
    assert ValidationIssue.from_dict(issue.to_dict()) == issue
    with pytest.raises(FrozenInstanceError):
        issue.code = "mutated"  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(issue)


def test_validate_scan_result_reports_descriptor_warnings_and_rejections() -> None:
    datasource = synthetic_datasource_ref()
    result = DataSourceScanResult(
        datasource,
        [synthetic_record_ref(datasource)],
        validation_evidence={"records_seen": 2},
        warnings=["scan skipped optional sidecar"],
        rejected_record_ids={"subject-002/record-001": "missing video"},
    )

    report = validate_scan_result(
        result,
        spec=DataSourceSpec(datasource, required_fields=["video.rgb"]),
        policy=ValidationIOPolicy.no_io(),
    )

    assert report.record_count == 1
    assert report.field_count == 2
    assert not report.passed
    assert [issue.code for issue in report.warnings] == ["scan.warning"]
    assert [issue.code for issue in report.errors] == ["record.rejected"]
    assert report.rejected_record_ids == {
        "subject-002/record-001": "missing video",
    }
    assert report.validation_evidence["records_seen"] == 2


def test_validate_scan_result_reports_missing_schema_source_fields_and_metadata() -> None:
    datasource = synthetic_datasource_ref(with_schema=False, with_source=False)
    result = DataSourceScanResult(
        datasource,
        [synthetic_record_ref(datasource, include_bvp=False)],
    )

    report = validate_scan_result(
        result,
        required_fields=["video.rgb", "signal.bvp.reference"],
        required_metadata=["group"],
    )

    assert not report.passed
    assert [issue.code for issue in report.issues] == [
        "datasource.source_missing",
        "schema.missing",
        "field.missing",
        "metadata.missing",
    ]
    assert report.errors[0].field_key == DataKey("signal.bvp.reference")
    assert report.errors[1].context["metadata_key"] == "group"


def test_validate_scan_result_uses_schema_fields_when_no_required_fields_are_given() -> None:
    datasource = synthetic_datasource_ref()
    result = DataSourceScanResult(
        datasource,
        [synthetic_record_ref(datasource, include_bvp=False)],
    )

    report = validate_scan_result(result)

    assert not report.passed
    assert [issue.code for issue in report.errors] == ["field.missing"]
    assert report.errors[0].field_key == DataKey("signal.bvp.reference")


def test_validate_scan_result_reports_empty_accepted_record_set() -> None:
    datasource = synthetic_datasource_ref()

    report = validate_scan_result(DataSourceScanResult(datasource))

    assert not report.passed
    assert [issue.code for issue in report.errors] == ["records.empty"]


def test_validation_report_serializes_primitive_evidence() -> None:
    datasource = synthetic_datasource_ref()
    issue = ValidationIssue(
        "scan.warning",
        "minor issue",
        severity="warning",
        scope="datasource",
        datasource_id=datasource.datasource_id,
    )
    report = DataSourceValidationReport(
        datasource,
        policy=ValidationIOPolicy.no_io(),
        issues=[issue],
        record_count=1,
        field_count=2,
        rejected_record_ids={"bad": "reason"},
        validation_evidence={"nested": {"ok": True}},
    )

    payload = report.to_dict()

    assert payload["policy"] == {"mode": "no_io"}
    assert payload["issues"] == [issue.to_dict()]
    assert payload["validation_evidence"] == {"nested": {"ok": True}}


def test_validation_rejects_invalid_shapes() -> None:
    with pytest.raises(InvalidDataSourceValidationError):
        ValidationIOPolicy("full_load")
    with pytest.raises(InvalidDataSourceValidationError):
        ValidationIssue("", "message", severity="error", scope="field")
    with pytest.raises(InvalidDataSourceValidationError):
        ValidationIssue("code", "message", severity="info", scope="field")  # type: ignore[arg-type]
    with pytest.raises(InvalidDataSourceValidationError):
        DataSourceValidationReport(
            synthetic_datasource_ref(),
            policy=ValidationIOPolicy.no_io(),
            record_count=-1,
        )
    with pytest.raises(InvalidDataSourceValidationError):
        validate_scan_result(object())  # type: ignore[arg-type]
