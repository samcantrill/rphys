from __future__ import annotations

import os
from pathlib import Path

import pytest

import rphys.ops.export as export_module
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
    IdempotencyPolicy,
    RecordExportRequest,
    SaveOperation,
)
from tests.support.synthetic_codecs import SyntheticCodec


def _request(
    source_path: Path,
    target_root: Path,
    *,
    policy: ExportPolicy,
) -> RecordExportRequest:
    source_field = FieldRef(
        "video.rgb",
        (ResourceRef(source_path.as_uri(), "file"),),
        schema="video.rgb.v1",
    )
    return RecordExportRequest(
        source_record=RecordRef(
            DataSourceRef("synthetic"),
            "record-001",
            {"video.rgb": source_field},
        ),
        field_values={"video.rgb": FieldValue("payload", schema="video.rgb.v1")},
        spec=ExportSpec(("video.rgb",), codec_requests={"video.rgb": "video"}),
        target=ExportTarget(ResourceRef(target_root.as_uri(), "file"), "exp-001"),
        policy=policy,
    )


def _selection(request: RecordExportRequest):
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry((codec,))
    return CodecSelectionOperation(registry).run(request).output, registry


def _target_path(selection) -> Path:
    return Path(selection.selected_fields[0].target.resources[0].uri.removeprefix("file://"))


def test_symlink_failure_requires_explicit_copy_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")
    selection, registry = _selection(
        _request(
            source_path,
            tmp_path / "exports",
            policy=ExportPolicy(materialization=ExportMaterialization.LINK),
        )
    )

    def fail_symlink(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        raise OSError("symlink disabled")

    monkeypatch.setattr(export_module.os, "symlink", fail_symlink)

    with pytest.raises(RemotePhysOperationError):
        SaveOperation(registry).run(selection)


def test_symlink_failure_copy_fallback_counts_as_copied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")
    selection, registry = _selection(
        _request(
            source_path,
            tmp_path / "exports",
            policy=ExportPolicy(
                materialization=ExportMaterialization.LINK,
                allow_link_copy_fallback=True,
            ),
        )
    )

    def fail_symlink(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        raise OSError("symlink disabled")

    monkeypatch.setattr(export_module.os, "symlink", fail_symlink)

    result = SaveOperation(registry).run(selection).output
    target_path = _target_path(selection)

    assert result.field_results[0].outcome == FieldExportOutcome.COPIED
    assert target_path.read_text(encoding="utf-8") == "payload"
    assert not target_path.is_symlink()


def test_link_copy_existing_target_skip_and_replace_are_explicit(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source" / "video.bin"
    source_path.parent.mkdir()
    source_path.write_text("payload", encoding="utf-8")

    skip_selection, skip_registry = _selection(
        _request(
            source_path,
            tmp_path / "exports-skip",
            policy=ExportPolicy(
                materialization=ExportMaterialization.COPY,
                idempotency=IdempotencyPolicy.SKIP_EXISTING,
            ),
        )
    )
    skip_target = _target_path(skip_selection)
    skip_target.parent.mkdir(parents=True)
    skip_target.write_text("existing", encoding="utf-8")

    skipped = SaveOperation(skip_registry).run(skip_selection).output
    assert skipped.field_results[0].outcome == FieldExportOutcome.SKIPPED
    assert skip_target.read_text(encoding="utf-8") == "existing"

    replace_selection, replace_registry = _selection(
        _request(
            source_path,
            tmp_path / "exports-replace",
            policy=ExportPolicy(
                materialization=ExportMaterialization.COPY,
                idempotency=IdempotencyPolicy.REPLACE_EXISTING,
            ),
        )
    )
    replace_target = _target_path(replace_selection)
    replace_target.parent.mkdir(parents=True)
    replace_target.write_text("existing", encoding="utf-8")

    replaced = SaveOperation(replace_registry).run(replace_selection).output
    assert replaced.field_results[0].outcome == FieldExportOutcome.REPLACED
    assert replace_target.read_text(encoding="utf-8") == "payload"


def test_local_link_copy_helpers_remain_private() -> None:
    for helper_name in [
        "_copy_local_resources",
        "_link_local_resources",
        "_resource_lineage_pairs",
        "_validate_local_resource_pair",
    ]:
        assert helper_name not in export_module.__all__
    for public_name in ["StorageAdapter", "StorageProtocol", "LinkCopyHelper"]:
        assert not hasattr(export_module, public_name)
