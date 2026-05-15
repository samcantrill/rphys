from __future__ import annotations

import pytest

from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io.codecs import CodecSaveResult
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    ExportReport,
    ExportResult,
    ExportSpec,
    ExportTarget,
    FieldExportOutcome,
    FieldExportResult,
    OutputLayout,
    RecordExportResult,
)


FIELD_KEYS = (
    "signal.bvp",
    "video.rgb",
    "timestamps.reference",
    "label.heart_rate",
    "quality.signal",
    "annotation.event",
)


def _record() -> RecordRef:
    fields = {
        key: FieldRef(
            key,
            (ResourceRef(f"file:///source/r001/{key}.bin", "file"),),
            schema=f"{key}.v1",
        )
        for key in FIELD_KEYS
    }
    return RecordRef(DataSourceRef("synthetic"), "record-001", fields)


def _field_result(
    record: RecordRef,
    key: str,
    outcome: FieldExportOutcome,
    *,
    failure: str | None = None,
    codec_result: CodecSaveResult | None = None,
) -> FieldExportResult:
    target = FieldRef(
        key,
        (ResourceRef(f"file:///exports/r001/{key}.bin", "file"),),
        schema=f"{key}.v1",
    )
    return FieldExportResult(
        source_record=record,
        source_field=record.fields[key],
        target=target,
        outcome=outcome,
        codec_result=codec_result,
        failure=failure,
    )


def test_field_export_result_preserves_source_target_and_codec_evidence() -> None:
    record = _record()
    target = FieldRef(
        "signal.bvp",
        (ResourceRef("file:///exports/r001/signal.bvp.bin", "file"),),
        schema="signal.bvp.v1",
    )
    codec_result = CodecSaveResult(
        target,
        resources=(ResourceRef("file:///exports/r001/signal.bvp.sidecar", "file"),),
        metadata={"codec": "synthetic"},
    )

    result = FieldExportResult(
        source_record=record,
        source_field=record.fields["signal.bvp"],
        target=target,
        outcome=FieldExportOutcome.WRITTEN,
        codec_result=codec_result,
        metadata={"operation": "save"},
    )

    assert result.source_record == record
    assert result.source_field == record.fields["signal.bvp"]
    assert result.target == target
    assert result.codec_result == codec_result
    assert result.target_resources == codec_result.resources
    assert result.source_resources == record.fields["signal.bvp"].resources
    assert result.metadata == {"operation": "save"}
    assert result.succeeded is True
    assert not hasattr(result, "to_dict")


def test_record_export_result_and_report_counts_all_outcomes() -> None:
    record = _record()
    outcomes = (
        FieldExportOutcome.WRITTEN,
        FieldExportOutcome.SKIPPED,
        FieldExportOutcome.LINKED,
        FieldExportOutcome.COPIED,
        FieldExportOutcome.REPLACED,
        FieldExportOutcome.FAILED,
    )
    field_results = tuple(
        _field_result(
            record,
            key,
            outcome,
            failure="codec failure" if outcome == FieldExportOutcome.FAILED else None,
        )
        for key, outcome in zip(FIELD_KEYS, outcomes, strict=True)
    )
    record_result = RecordExportResult(record, field_results)
    export_result = ExportResult(
        spec=ExportSpec(FIELD_KEYS),
        target=ExportTarget(ResourceRef("file:///exports", "file"), "exp-001"),
        layout=OutputLayout(),
        record_results=(record_result,),
    )
    report = ExportReport(export_result)

    assert record_result.total_count == 6
    assert record_result.count(FieldExportOutcome.FAILED) == 1
    assert export_result.field_results == field_results
    assert export_result.count(FieldExportOutcome.WRITTEN) == 1
    assert report.record_count == 1
    assert report.field_count == 6
    assert report.written_count == 1
    assert report.skipped_count == 1
    assert report.linked_count == 1
    assert report.copied_count == 1
    assert report.replaced_count == 1
    assert report.failed_count == 1
    assert not hasattr(export_result, "to_dict")
    assert not hasattr(report, "to_dict")
    assert not hasattr(report, "json")


def test_field_export_result_requires_failure_evidence_for_failed_outcomes() -> None:
    record = _record()

    with pytest.raises(RemotePhysOperationError):
        _field_result(record, "signal.bvp", FieldExportOutcome.FAILED)


def test_record_and_export_results_reject_mismatched_or_empty_inputs() -> None:
    record = _record()
    other_record = RecordRef(
        DataSourceRef("synthetic"),
        "record-002",
        {"signal.bvp": record.fields["signal.bvp"]},
    )
    result = _field_result(record, "signal.bvp", FieldExportOutcome.WRITTEN)

    with pytest.raises(RemotePhysOperationError):
        RecordExportResult(record, ())
    with pytest.raises(RemotePhysOperationError):
        RecordExportResult(other_record, (result,))
    with pytest.raises(RemotePhysOperationError):
        ExportResult(
            spec=ExportSpec(("signal.bvp",)),
            target=ExportTarget(ResourceRef("file:///exports", "file"), "exp-001"),
            layout=OutputLayout(),
            record_results=(),
        )
