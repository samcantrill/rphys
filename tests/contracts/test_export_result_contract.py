from __future__ import annotations

import dataclasses

from rphys.datasources.refs import DataSourceRef, RecordRef
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


def test_export_result_records_are_typed_in_memory_evidence_only() -> None:
    source_field = FieldRef(
        "signal.bvp",
        (ResourceRef("file:///source/r001/signal.bvp.bin", "file"),),
        schema="signal.bvp.v1",
    )
    source_record = RecordRef(
        DataSourceRef("synthetic"),
        "record-001",
        {"signal.bvp": source_field},
    )
    field_result = FieldExportResult(
        source_record=source_record,
        source_field=source_field,
        target=FieldRef(
            "signal.bvp",
            (ResourceRef("file:///exports/r001/signal.bvp.bin", "file"),),
            schema="signal.bvp.v1",
        ),
        outcome=FieldExportOutcome.WRITTEN,
    )
    record_result = RecordExportResult(source_record, (field_result,))
    export_result = ExportResult(
        spec=ExportSpec(("signal.bvp",)),
        target=ExportTarget(ResourceRef("file:///exports", "file"), "exp-001"),
        layout=OutputLayout(),
        record_results=(record_result,),
    )
    report = ExportReport(export_result)

    assert dataclasses.is_dataclass(field_result)
    assert dataclasses.is_dataclass(record_result)
    assert dataclasses.is_dataclass(export_result)
    assert dataclasses.is_dataclass(report)
    assert report.written_count == 1
    for public_record in (field_result, record_result, export_result, report):
        assert not hasattr(public_record, "to_dict")
        assert not hasattr(public_record, "json")
        assert not hasattr(public_record, "write")
