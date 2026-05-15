from __future__ import annotations

from pathlib import Path

import pytest

from rphys.data.fields import FieldValue
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io.codecs import CodecRegistry
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportMaterialization,
    ExportPolicy,
    ExportSpec,
    ExportTarget,
    FieldExportOutcome,
    RecordExportRequest,
    SaveOperation,
)
from tests.support.synthetic_codecs import SyntheticCodec


def _request(
    source_resource: ResourceRef,
    tmp_path: Path,
    *,
    target_protocol: str = "file",
    materialization: ExportMaterialization = ExportMaterialization.LINK,
) -> RecordExportRequest:
    source_field = FieldRef("video.rgb", (source_resource,), schema="video.rgb.v1")
    return RecordExportRequest(
        source_record=RecordRef(
            DataSourceRef("synthetic"),
            "record-001",
            {"video.rgb": source_field},
        ),
        field_values={"video.rgb": FieldValue("payload", schema="video.rgb.v1")},
        spec=ExportSpec(("video.rgb",), codec_requests={"video.rgb": "video"}),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), target_protocol), "exp-001"),
        policy=ExportPolicy(materialization=materialization),
    )


def _run(request: RecordExportRequest):
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry((codec,))
    selection = CodecSelectionOperation(registry).run(request).output
    return SaveOperation(registry).run(selection).output, codec


def test_link_export_records_ordered_source_and_target_lineage(tmp_path: Path) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")
    source_resource = ResourceRef(source_path.as_uri(), "file")

    record_result, codec = _run(_request(source_resource, tmp_path / "exports"))
    field_result = record_result.field_results[0]

    assert field_result.outcome == FieldExportOutcome.LINKED
    assert field_result.source_resources == (source_resource,)
    assert field_result.target_resources == field_result.target.resources
    assert Path(field_result.target.resources[0].uri.removeprefix("file://")).is_symlink()
    assert codec.save_calls == 0


def test_copy_export_records_copied_outcome_and_lineage(tmp_path: Path) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")
    source_resource = ResourceRef(source_path.as_uri(), "file")

    record_result, codec = _run(
        _request(
            source_resource,
            tmp_path / "exports",
            materialization=ExportMaterialization.COPY,
        )
    )
    field_result = record_result.field_results[0]
    target_path = Path(field_result.target.resources[0].uri.removeprefix("file://"))

    assert field_result.outcome == FieldExportOutcome.COPIED
    assert target_path.read_text(encoding="utf-8") == "payload"
    assert not target_path.is_symlink()
    assert field_result.source_resources == (source_resource,)
    assert codec.save_calls == 0


def test_link_copy_requires_ordered_one_to_one_lineage(tmp_path: Path) -> None:
    first = tmp_path / "source" / "video.bin"
    second = tmp_path / "source" / "video.json"
    first.parent.mkdir()
    first.write_text("payload", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    source_field = FieldRef(
        "video.rgb",
        (ResourceRef(first.as_uri(), "file"), ResourceRef(second.as_uri(), "file")),
        schema="video.rgb.v1",
    )
    request = RecordExportRequest(
        source_record=RecordRef(
            DataSourceRef("synthetic"),
            "record-001",
            {"video.rgb": source_field},
        ),
        field_values={"video.rgb": FieldValue("payload", schema="video.rgb.v1")},
        spec=ExportSpec(("video.rgb",), codec_requests={"video.rgb": "video"}),
        target=ExportTarget(ResourceRef((tmp_path / "exports").as_uri(), "file"), "exp-001"),
        policy=ExportPolicy(materialization=ExportMaterialization.COPY),
    )
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry((codec,))
    selection = CodecSelectionOperation(registry).run(request).output

    with pytest.raises(RemotePhysOperationError):
        SaveOperation(registry).run(selection)


def test_link_copy_rejects_cross_protocol_and_unsupported_protocols(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")

    with pytest.raises(RemotePhysOperationError):
        _run(
            _request(
                ResourceRef(source_path.as_uri(), "file"),
                tmp_path / "exports",
                target_protocol="s3",
            )
        )

    with pytest.raises(RemotePhysOperationError):
        _run(
            _request(
                ResourceRef("s3://bucket/video.bin", "s3"),
                tmp_path / "exports",
                target_protocol="s3",
            )
        )
