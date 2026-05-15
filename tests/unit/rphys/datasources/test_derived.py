from __future__ import annotations

import inspect

import pytest

from rphys.data.metadata import MetadataKey, SUBJECT_ID
from rphys.datasources.derived import (
    DerivedDataSourceAssembly,
    DerivedDataSourceBuilder,
)
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysDataSourceError
from rphys.io.codecs import CodecSaveResult
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    ExportSpec,
    ExportTarget,
    FieldExportOutcome,
    FieldExportResult,
    OutputLayout,
    RecordExportResult,
    ExportResult,
)


def test_builder_assembles_ordered_derived_records_from_successful_results() -> None:
    source = DataSourceRef("source-ds", metadata={"source_id": "fixture"})
    first = _source_record(source, "subject-001/record-001")
    second = _source_record(source, "subject-002/record-001")
    first_result = _field_result(first, "file:///derived/first.bvp")
    second_result = _field_result(second, "file:///derived/second.bvp")

    assembly = DerivedDataSourceBuilder(
        "derived-ds",
        source=ResourceRef("file:///derived", "file"),
        metadata={"stage": 8},
    ).from_record_results(
        (
            RecordExportResult(first, (first_result,)),
            RecordExportResult(second, (second_result,)),
        )
    )

    assert isinstance(assembly, DerivedDataSourceAssembly)
    assert assembly.datasource.datasource_id == "derived-ds"
    assert assembly.datasource.source == ResourceRef("file:///derived", "file")
    assert assembly.records[0].record_id == "subject-001/record-001"
    assert assembly.records[1].record_id == "subject-002/record-001"
    assert assembly.records[0].fields["signal.bvp.reference"] == first_result.target
    assert assembly.records[0].datasource == assembly.datasource
    assert assembly.records[0].metadata[SUBJECT_ID] == "subject-001"
    assert (
        assembly.records[0].metadata[MetadataKey("derived.source_datasource_id")]
        == "source-ds"
    )
    assert assembly.source_records == (first, second)
    assert assembly.source_datasources == (source,)
    assert assembly.field_results == (first_result, second_result)
    assert assembly.record_count == 2
    assert assembly.field_count == 2


def test_builder_uses_codec_result_resources_without_rescanning_outputs() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")
    target = FieldRef(
        "signal.bvp.reference",
        (ResourceRef("file:///declared-target.bvp", "file"),),
        schema="signal.bvp.v1",
    )
    written = ResourceRef("file:///codec-target.bvp", "file")
    result = FieldExportResult(
        source_record=record,
        source_field=record.fields["signal.bvp.reference"],
        target=target,
        outcome=FieldExportOutcome.WRITTEN,
        codec_result=CodecSaveResult(target, resources=(written,)),
    )

    assembly = DerivedDataSourceBuilder("derived-ds").from_field_results((result,))

    derived_field = assembly.records[0].fields["signal.bvp.reference"]
    assert derived_field is not target
    assert derived_field.resources == (written,)
    assert derived_field.schema == target.schema


def test_builder_filters_failed_results_and_keeps_explicit_skips() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")
    failed = _field_result(
        record,
        "file:///derived/failed.bvp",
        outcome=FieldExportOutcome.FAILED,
        failure="codec failed",
    )
    skipped = _field_result(
        record,
        "file:///derived/skipped.bvp",
        outcome=FieldExportOutcome.SKIPPED,
    )

    assembly = DerivedDataSourceBuilder("derived-ds").from_field_results((failed, skipped))

    assert assembly.field_results == (skipped,)
    assert assembly.records[0].fields["signal.bvp.reference"] == skipped.target


def test_builder_rejects_assembly_without_successful_field_results() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")
    failed = _field_result(
        record,
        "file:///derived/failed.bvp",
        outcome=FieldExportOutcome.FAILED,
        failure="codec failed",
    )

    with pytest.raises(RemotePhysDataSourceError):
        DerivedDataSourceBuilder("derived-ds").from_field_results((failed,))


def test_builder_rejects_duplicate_target_fields_for_one_source_record() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")

    with pytest.raises(RemotePhysDataSourceError):
        DerivedDataSourceBuilder("derived-ds").from_field_results(
            (
                _field_result(record, "file:///derived/a.bvp"),
                _field_result(record, "file:///derived/b.bvp"),
            )
        )


def test_builder_from_export_result_preserves_source_descriptors() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")
    before = dict(record.fields)
    result = _field_result(record, "file:///derived/record.bvp")
    export_result = ExportResult(
        spec=ExportSpec(("signal.bvp.reference",)),
        target=ExportTarget(ResourceRef("file:///derived", "file"), "exp-001"),
        layout=OutputLayout(resource_suffix="bvp"),
        record_results=(RecordExportResult(record, (result,)),),
    )

    assembly = DerivedDataSourceBuilder("derived-ds").from_export_result(export_result)

    assert record.datasource == source
    assert dict(record.fields) == before
    assert assembly.records[0] is not record
    assert assembly.records[0].datasource.datasource_id == "derived-ds"


def test_derived_module_has_no_rescan_or_manifest_surface() -> None:
    import rphys.datasources.derived as derived

    source = inspect.getsource(derived)

    assert "DataSourceIndexManifest" not in source
    assert "iterdir" not in source
    assert "glob" not in source
    assert "walk" not in source
    assert not hasattr(derived, "DataSourceManifestWriter")
    assert not hasattr(derived, "SaveOperation")
    assert not hasattr(derived, "CodecSelectionOperation")


def test_assembly_rejects_invalid_shapes() -> None:
    source = DataSourceRef("source-ds")
    record = _source_record(source, "subject-001/record-001")
    result = _field_result(record, "file:///derived/record.bvp")

    with pytest.raises(RemotePhysDataSourceError):
        DerivedDataSourceAssembly(
            datasource=object(),  # type: ignore[arg-type]
            records=(record,),
            field_results=(result,),
            source_records=(record,),
            source_datasources=(source,),
        )
    with pytest.raises(RemotePhysDataSourceError):
        DerivedDataSourceBuilder("derived-ds").from_field_results((object(),))  # type: ignore[list-item]


def _source_record(source: DataSourceRef, record_id: str) -> RecordRef:
    subject_id = record_id.split("/", 1)[0]
    field = FieldRef(
        "signal.bvp.reference",
        (ResourceRef(f"memory://{record_id}/bvp", "memory"),),
        schema="signal.bvp.v1",
    )
    return RecordRef(
        source,
        record_id,
        {"signal.bvp.reference": field},
        metadata={SUBJECT_ID: subject_id},
    )


def _field_result(
    record: RecordRef,
    target_uri: str,
    *,
    outcome: FieldExportOutcome = FieldExportOutcome.WRITTEN,
    failure: str | None = None,
) -> FieldExportResult:
    target = FieldRef(
        "signal.bvp.reference",
        (ResourceRef(target_uri, "file"),),
        schema="signal.bvp.v1",
    )
    return FieldExportResult(
        source_record=record,
        source_field=record.fields["signal.bvp.reference"],
        target=target,
        outcome=outcome,
        failure=failure,
    )
