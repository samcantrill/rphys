from __future__ import annotations

import pytest

from rphys.datasources.refs import DataSourceRef, RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io.codecs import MetadataSavePolicy
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef
from rphys.ops.export import ExportSpec, ExportTarget, OutputLayout


def _record() -> RecordRef:
    source = ResourceRef("file:///source/records/r001.bvp", "file")
    field = FieldRef("signal.bvp", (source,), schema="signal.bvp.v1")
    datasource = DataSourceRef("synthetic")
    return RecordRef(datasource, "record-001", {"signal.bvp": field})


def test_output_layout_derives_deterministic_field_ref_without_io() -> None:
    record = _record()
    spec = ExportSpec(
        ("signal.bvp",),
        schema_requests={"signal.bvp": "signal.bvp.filtered.v1"},
        output_options={"window": {"seconds": 8}},
    )
    target = ExportTarget(ResourceRef("file:///exports", "file"), "exp-001")
    layout = OutputLayout()

    first = layout.derive_target(record, "signal.bvp", spec=spec, target=target)
    second = layout.derive_target(record, "signal.bvp", spec=spec, target=target)

    assert first == second
    assert first.key == "signal.bvp"
    assert str(first.schema) == "signal.bvp.filtered.v1"
    assert first.resources[0].protocol == "file"
    assert first.resources[0].uri == (
        "file:///exports/synthetic/record-001/signal.bvp/exp-001/stage8.v1/"
        f"{spec.fingerprint(layout)}.field"
    )
    assert first.metadata["export_spec_fingerprint"] == spec.fingerprint(layout)
    assert not hasattr(layout, "scan")
    assert not hasattr(first, "save")


def test_export_fingerprint_uses_only_stable_representation_inputs() -> None:
    layout = OutputLayout()
    baseline = ExportSpec(
        ("signal.bvp", "video.rgb"),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        output_options={"scale": "unit"},
    )

    assert baseline.fingerprint(layout) == ExportSpec(
        ("video.rgb", "signal.bvp"),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        output_options={"scale": "unit"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != ExportSpec(
        ("signal.bvp",),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        output_options={"scale": "unit"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != ExportSpec(
        ("signal.bvp", "video.rgb"),
        codec_requests={"signal.bvp": "zarr"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        output_options={"scale": "unit"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != ExportSpec(
        ("signal.bvp", "video.rgb"),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.filtered.v1"},
        output_options={"scale": "unit"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != ExportSpec(
        ("signal.bvp", "video.rgb"),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        metadata_policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA,
        output_options={"scale": "unit"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != ExportSpec(
        ("signal.bvp", "video.rgb"),
        codec_requests={"signal.bvp": "npy"},
        schema_requests={"signal.bvp": "signal.bvp.v1"},
        output_options={"scale": "raw"},
    ).fingerprint(layout)
    assert baseline.fingerprint(layout) != baseline.fingerprint(
        OutputLayout(layout_version="stage8.v2")
    )


def test_export_fingerprint_excludes_target_identity_and_runtime_objects() -> None:
    record = _record()
    spec = ExportSpec(("signal.bvp",), output_options={"scale": "unit"})
    layout = OutputLayout()
    first_target = ExportTarget(ResourceRef("file:///exports-a", "file"), "exp-a")
    second_target = ExportTarget(ResourceRef("file:///exports-b", "file"), "exp-b")

    first = layout.derive_target(record, "signal.bvp", spec=spec, target=first_target)
    second = layout.derive_target(record, "signal.bvp", spec=spec, target=second_target)

    assert spec.fingerprint(layout) == spec.fingerprint(layout)
    assert first.metadata["export_spec_fingerprint"] == second.metadata["export_spec_fingerprint"]
    assert first.resources[0].uri != second.resources[0].uri


def test_layout_rejects_absent_or_unrequested_fields() -> None:
    record = _record()
    target = ExportTarget(ResourceRef("file:///exports", "file"), "exp-001")
    layout = OutputLayout()

    with pytest.raises(RemotePhysOperationError):
        layout.derive_target(
            record,
            "video.rgb",
            spec=ExportSpec(("signal.bvp",)),
            target=target,
        )

    with pytest.raises(RemotePhysOperationError):
        layout.derive_target(
            record,
            "video.rgb",
            spec=ExportSpec(("video.rgb",)),
            target=target,
        )


def test_export_specs_reject_invalid_request_shapes() -> None:
    with pytest.raises(RemotePhysOperationError):
        ExportSpec(())
    with pytest.raises(RemotePhysOperationError):
        ExportSpec(("signal.bvp", "signal.bvp"))
    with pytest.raises(RemotePhysOperationError):
        ExportSpec(("signal.bvp",), codec_requests={"video.rgb": "npy"})
    with pytest.raises(RemotePhysOperationError):
        ExportSpec(("signal.bvp",), schema_requests={"video.rgb": "video.rgb.v1"})
    with pytest.raises(RemotePhysOperationError):
        OutputLayout(resource_suffix="bad/suffix")
