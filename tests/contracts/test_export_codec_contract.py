from __future__ import annotations

from pathlib import Path

from rphys.data.fields import FieldValue
from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.io.codecs import CodecRegistry, MetadataSavePolicy, SaveContext
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import (
    CodecSelectionOperation,
    ExportSpec,
    ExportTarget,
    RecordExportRequest,
    SaveOperation,
)
from tests.support.synthetic_codecs import SyntheticCodec


def test_save_operation_preserves_codec_save_context_contract(tmp_path: Path) -> None:
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry((codec,))
    source_field = FieldRef(
        "video.rgb",
        (ResourceRef("file:///source/r001/video.bin", "file"),),
        schema="video.rgb.v1",
    )
    request = RecordExportRequest(
        source_record=RecordRef(
            DataSourceRef("synthetic"),
            "record-001",
            {"video.rgb": source_field},
        ),
        field_values={"video.rgb": FieldValue("payload", schema="video.rgb.v1")},
        spec=ExportSpec(
            ("video.rgb",),
            codec_requests={"video.rgb": "video"},
            metadata_policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA,
        ),
        target=ExportTarget(ResourceRef(tmp_path.as_uri(), "file"), "exp-001"),
    )

    selection = CodecSelectionOperation(registry).run(request).output
    result = SaveOperation(registry).run(selection).output

    assert codec.save_calls == 1
    saved_value, context = codec.saved[0]
    assert saved_value is selection.selected_fields[0].field_value
    assert isinstance(context, SaveContext)
    assert context.target is selection.selected_fields[0].target
    assert context.metadata_policy == MetadataSavePolicy.INCLUDE_FIELD_METADATA
    assert result.field_results[0].codec_result is not None
    assert result.field_results[0].codec_result.target is context.target
    assert not hasattr(context, "datasource")
    assert not hasattr(context, "record")
    assert not hasattr(context, "export")
