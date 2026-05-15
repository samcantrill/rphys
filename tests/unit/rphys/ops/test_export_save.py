from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

import pytest

from rphys.data.fields import FieldValue
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysCodecError, RemotePhysOperationError
from rphys.io.codecs import CodecRegistry
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops import OperationPipeline
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportMaterialization,
    ExportPolicy,
    ExportSelection,
    ExportSpec,
    ExportTarget,
    FieldExportOutcome,
    IdempotencyPolicy,
    RecordExportRequest,
    RecordExportResult,
    SaveOperation,
)
from tests.support.synthetic_codecs import SyntheticCodec


def _record() -> RecordRef:
    source = ResourceRef("file:///source/r001/video.bin", "file")
    field = FieldRef("video.rgb", (source,), schema="video.rgb.v1")
    return RecordRef(DataSourceRef("synthetic"), "record-001", {"video.rgb": field})


def _request(
    tmp_path: Path,
    *,
    policy: ExportPolicy | None = None,
) -> RecordExportRequest:
    return RecordExportRequest(
        source_record=_record(),
        field_values={"video.rgb": FieldValue("payload", schema="video.rgb.v1")},
        spec=ExportSpec(("video.rgb",), codec_requests={"video.rgb": "video"}),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        policy=policy,
    )


def _selection(
    tmp_path: Path,
    codec: SyntheticCodec,
    *,
    policy: ExportPolicy | None = None,
) -> ExportSelection:
    return CodecSelectionOperation(CodecRegistry((codec,))).run(
        _request(tmp_path, policy=policy)
    ).output  # type: ignore[return-value]


def _touch_target(selection: ExportSelection) -> Path:
    uri = selection.selected_fields[0].target.resources[0].uri
    path = Path(unquote(urlparse(uri).path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("existing", encoding="utf-8")
    return path


def test_save_operation_writes_selected_field_through_codec(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    selection = _selection(tmp_path, codec)
    result = SaveOperation(CodecRegistry((codec,))).run(selection)

    assert isinstance(result.output, RecordExportResult)
    field_result = result.output.field_results[0]
    assert field_result.outcome == FieldExportOutcome.WRITTEN
    assert field_result.codec_result is not None
    assert field_result.codec_result.target == selection.selected_fields[0].target
    assert field_result.target_resources == field_result.codec_result.resources
    assert codec.save_calls == 1
    saved_value, save_context = codec.saved[0]
    assert saved_value is selection.selected_fields[0].field_value
    assert save_context.target is selection.selected_fields[0].target
    assert save_context.metadata_policy == selection.selected_fields[0].metadata_policy
    assert result.side_effect_evidence["field_save"] == {"attempted": 1, "skipped": 0}


def test_selection_to_save_pipeline_forwards_record_result(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry((codec,))
    pipeline = OperationPipeline(
        (
            CodecSelectionOperation(registry),
            SaveOperation(registry),
        )
    )

    result = pipeline.run(_request(tmp_path))

    assert isinstance(result.output, RecordExportResult)
    assert result.output.field_results[0].outcome == FieldExportOutcome.WRITTEN
    assert codec.save_calls == 1


def test_save_operation_conflicts_by_default_on_existing_targets(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    selection = _selection(tmp_path, codec)
    _touch_target(selection)

    with pytest.raises(RemotePhysOperationError):
        SaveOperation(CodecRegistry((codec,))).run(selection)
    assert codec.save_calls == 0


def test_save_operation_skips_existing_targets_without_codec_save(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    selection = _selection(
        tmp_path,
        codec,
        policy=ExportPolicy(idempotency=IdempotencyPolicy.SKIP_EXISTING),
    )
    _touch_target(selection)

    result = SaveOperation(CodecRegistry((codec,))).run(selection)

    assert result.output.field_results[0].outcome == FieldExportOutcome.SKIPPED
    assert codec.save_calls == 0
    assert result.side_effect_evidence["field_save"] == {"attempted": 0, "skipped": 1}


def test_save_operation_replaces_existing_targets_through_codec_save(
    tmp_path: Path,
) -> None:
    codec = SyntheticCodec(name="video")
    selection = _selection(
        tmp_path,
        codec,
        policy=ExportPolicy(idempotency=IdempotencyPolicy.REPLACE_EXISTING),
    )
    _touch_target(selection)

    result = SaveOperation(CodecRegistry((codec,))).run(selection)

    assert result.output.field_results[0].outcome == FieldExportOutcome.REPLACED
    assert codec.save_calls == 1


def test_save_operation_rejects_link_or_copy_materialization(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    selection = _selection(
        tmp_path,
        codec,
        policy=ExportPolicy(materialization=ExportMaterialization.LINK),
    )

    with pytest.raises(RemotePhysOperationError):
        SaveOperation(CodecRegistry((codec,))).run(selection)
    assert codec.save_calls == 0


def test_save_operation_codec_failures_abort_by_default(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video", dependency_available=False)
    selection = _selection(tmp_path, codec)

    with pytest.raises(RemotePhysCodecError):
        SaveOperation(CodecRegistry((codec,))).run(selection)


def test_save_operation_can_record_explicit_partial_field_failures(
    tmp_path: Path,
) -> None:
    codec = SyntheticCodec(name="video", dependency_available=False)
    selection = _selection(
        tmp_path,
        codec,
        policy=ExportPolicy(continue_on_field_error=True),
    )

    result = SaveOperation(CodecRegistry((codec,))).run(selection)

    field_result = result.output.field_results[0]
    assert field_result.outcome == FieldExportOutcome.FAILED
    assert "CodecDependencyError" in field_result.failure
    assert result.metadata["failed_count"] == 1


def test_save_operation_rejects_invalid_inputs() -> None:
    with pytest.raises(RemotePhysOperationError):
        SaveOperation("registry")  # type: ignore[arg-type]
    with pytest.raises(RemotePhysOperationError):
        SaveOperation(CodecRegistry()).run(object())
