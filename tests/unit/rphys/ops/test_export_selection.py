from __future__ import annotations

from pathlib import Path

import pytest

from rphys.data.fields import FieldValue
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysCodecError, RemotePhysOperationError
from rphys.io.codecs import (
    CodecCapabilities,
    CodecSaveResult,
    CodecRegistry,
    MetadataSavePolicy,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportSelection,
    ExportSpec,
    ExportTarget,
    RecordExportRequest,
)


class _RecordingCodec:
    name = "synthetic"

    def __init__(
        self,
        *,
        field_key: str = "signal.bvp",
        metadata_policies: tuple[MetadataSavePolicy, ...] = (
            MetadataSavePolicy.REFERENCE_ONLY,
        ),
    ) -> None:
        self.field_key = field_key
        self.save_called = False
        self.capabilities = CodecCapabilities(
            can_save=True,
            metadata_policies=metadata_policies,
        )

    def supports_save(self, value: FieldValue, context) -> bool:
        return str(context.target.key) == self.field_key

    def save(self, value: FieldValue, context) -> CodecSaveResult:
        self.save_called = True
        return CodecSaveResult(context.target)


def _record() -> RecordRef:
    source = ResourceRef("file:///source/r001/signal.bvp.bin", "file")
    field = FieldRef("signal.bvp", (source,), schema="signal.bvp.v1")
    return RecordRef(DataSourceRef("synthetic"), "record-001", {"signal.bvp": field})


def _request(tmp_path: Path, **spec_kwargs: object) -> RecordExportRequest:
    return RecordExportRequest(
        source_record=_record(),
        field_values={"signal.bvp": FieldValue([1.0, 2.0], schema="signal.bvp.v1")},
        spec=ExportSpec(("signal.bvp",), **spec_kwargs),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
    )


def test_codec_selection_operation_returns_no_write_selection(tmp_path: Path) -> None:
    codec = _RecordingCodec()
    operation = CodecSelectionOperation(CodecRegistry((codec,)))
    request = _request(
        tmp_path,
        codec_requests={"signal.bvp": "synthetic"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
    )

    result = operation.run(request)

    assert result.operation_name == "codec_selection"
    assert result.side_effect_evidence == {}
    assert result.metadata["write_count"] == 0
    assert isinstance(result.output, ExportSelection)
    assert len(result.output.selected_fields) == 1
    selected = result.output.selected_fields[0]
    assert selected.codec_name == "synthetic"
    assert selected.codec_request == "synthetic"
    assert selected.metadata_policy == MetadataSavePolicy.REFERENCE_ONLY
    assert selected.target.resources[0].uri.startswith(tmp_path.as_uri())
    assert codec.save_called is False
    assert list(tmp_path.iterdir()) == []


def test_codec_selection_operation_rejects_missing_field_values(tmp_path: Path) -> None:
    record = _record()

    with pytest.raises(RemotePhysOperationError):
        RecordExportRequest(
            source_record=record,
            field_values={},
            spec=ExportSpec(("signal.bvp",)),
            target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        )


def test_codec_selection_operation_rejects_absent_record_fields(tmp_path: Path) -> None:
    record = _record()
    request = RecordExportRequest(
        source_record=record,
        field_values={"signal.bvp": FieldValue([1.0], schema="signal.bvp.v1")},
        spec=ExportSpec(("video.rgb",)),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
    )

    with pytest.raises(RemotePhysOperationError):
        CodecSelectionOperation(CodecRegistry((_RecordingCodec(),))).run(request)


def test_codec_selection_operation_rejects_schema_mismatch(tmp_path: Path) -> None:
    request = _request(
        tmp_path,
        schema_requests={"signal.bvp": "signal.bvp.filtered.v1"},
    )

    with pytest.raises(RemotePhysOperationError):
        CodecSelectionOperation(CodecRegistry((_RecordingCodec(),))).run(request)


def test_codec_selection_operation_rejects_codec_request_mismatch(tmp_path: Path) -> None:
    request = _request(tmp_path, codec_requests={"signal.bvp": "other"})

    with pytest.raises(RemotePhysOperationError):
        CodecSelectionOperation(CodecRegistry((_RecordingCodec(),))).run(request)


def test_codec_selection_operation_propagates_ambiguous_or_unsupported_codecs(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    with pytest.raises(RemotePhysCodecError):
        CodecSelectionOperation(
            CodecRegistry((_RecordingCodec(), _RecordingCodec())),
        ).run(request)

    with pytest.raises(RemotePhysCodecError):
        CodecSelectionOperation(CodecRegistry(())).run(request)


def test_codec_selection_operation_rejects_unsupported_metadata_policy(
    tmp_path: Path,
) -> None:
    request = _request(
        tmp_path,
        metadata_policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA,
    )

    with pytest.raises(RemotePhysCodecError):
        CodecSelectionOperation(CodecRegistry((_RecordingCodec(),))).run(request)


def test_codec_selection_operation_rejects_invalid_inputs(tmp_path: Path) -> None:
    with pytest.raises(RemotePhysOperationError):
        CodecSelectionOperation("registry")  # type: ignore[arg-type]
    with pytest.raises(RemotePhysOperationError):
        CodecSelectionOperation(CodecRegistry((_RecordingCodec(),))).run(object())
    with pytest.raises(RemotePhysOperationError):
        RecordExportRequest(
            source_record=_record(),
            field_values={"video.rgb": FieldValue(b"payload")},
            spec=ExportSpec(("signal.bvp",)),
            target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
        )
