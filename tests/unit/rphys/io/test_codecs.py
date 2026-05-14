from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rphys.data.fields import FieldSpec, FieldValue
from rphys.errors import RemotePhysCodecError
from rphys.io.codecs import (
    CodecCapabilities,
    CodecLoadResult,
    CodecProbeResult,
    CodecSaveResult,
    FieldCodec,
    IOContext,
    LoadContext,
    MetadataSavePolicy,
    SaveContext,
)
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


def _resource(uri: str = "file:///records/r001/video.mp4") -> ResourceRef:
    return ResourceRef(uri, "file", {"mode": "rb"})


def _field_ref() -> FieldRef:
    return FieldRef(
        "video.rgb",
        [_resource(), _resource("file:///records/r001/video.json")],
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )


def _field_view() -> FieldView:
    return FieldView(_field_ref(), TemporalIndexSlice(0, 60, 2))


def test_metadata_save_policy_is_narrow_and_explicit() -> None:
    assert MetadataSavePolicy.REFERENCE_ONLY.value == "reference_only"
    assert MetadataSavePolicy.INCLUDE_FIELD_METADATA.value == "include_field_metadata"
    assert [policy.value for policy in MetadataSavePolicy] == [
        "reference_only",
        "include_field_metadata",
    ]


def test_codec_capabilities_record_operation_support_without_matching_behavior() -> None:
    capabilities = CodecCapabilities(
        can_probe=True,
        can_load=True,
        metadata_policies=["reference_only"],
    )

    assert capabilities.can_probe is True
    assert capabilities.can_load is True
    assert capabilities.can_save is False
    assert capabilities.metadata_policies == (MetadataSavePolicy.REFERENCE_ONLY,)
    assert not hasattr(capabilities, "priority")
    assert not hasattr(capabilities, "match")
    assert not hasattr(capabilities, "register")
    with pytest.raises(FrozenInstanceError):
        capabilities.can_save = True  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(capabilities)


def test_codec_capabilities_reject_invalid_declarations() -> None:
    with pytest.raises(RemotePhysCodecError) as wrong_flag:
        CodecCapabilities(can_probe=1)  # type: ignore[arg-type]
    assert wrong_flag.value.context["field"] == "can_probe"

    with pytest.raises(RemotePhysCodecError) as empty_policies:
        CodecCapabilities(metadata_policies=[])
    assert empty_policies.value.context["field"] == "metadata_policies"

    with pytest.raises(RemotePhysCodecError) as unknown_policy:
        CodecCapabilities(metadata_policies=["manifest"])
    assert unknown_policy.value.context["field"] == "metadata_policy"


def test_io_context_copies_and_freezes_metadata() -> None:
    metadata = {"source": {"path": "fixture"}, "chunks": [1, 2]}
    context = IOContext(metadata)
    metadata["source"]["path"] = "mutated"
    metadata["chunks"].append(3)

    assert context.metadata == {"source": {"path": "fixture"}, "chunks": (1, 2)}
    with pytest.raises(TypeError):
        context.metadata["source"] = {}  # type: ignore[index]
    with pytest.raises(TypeError):
        context.metadata["source"]["path"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        context.metadata = {}  # type: ignore[misc]
    with pytest.raises(TypeError):
        hash(context)


def test_load_context_is_datasource_neutral_field_view_context() -> None:
    view = _field_view()
    context = LoadContext(view, metadata={"operation": "probe"})

    assert context.field_view is view
    assert context.field_view.field_ref.resources == view.field_ref.resources
    assert context.metadata == {"operation": "probe"}
    assert not hasattr(context, "record")
    assert not hasattr(context, "index_item")
    assert not hasattr(context, "locator")


def test_save_context_requires_field_ref_target_and_metadata_policy() -> None:
    target = _field_ref()
    context = SaveContext(
        target,
        metadata_policy="include_field_metadata",
        metadata={"operation": "save"},
    )

    assert context.target is target
    assert context.metadata_policy is MetadataSavePolicy.INCLUDE_FIELD_METADATA
    assert context.metadata == {"operation": "save"}
    assert not hasattr(context, "export_layout")
    assert not hasattr(context, "manifest")
    assert not hasattr(context, "record")

    with pytest.raises(RemotePhysCodecError) as invalid_target:
        SaveContext(object())  # type: ignore[arg-type]
    assert invalid_target.value.context["field"] == "target"

    with pytest.raises(RemotePhysCodecError) as invalid_policy:
        SaveContext(target, metadata_policy="manifest")
    assert invalid_policy.value.context["field"] == "metadata_policy"


def test_load_context_rejects_non_field_view() -> None:
    with pytest.raises(RemotePhysCodecError) as exc_info:
        LoadContext(_field_ref())  # type: ignore[arg-type]

    assert exc_info.value.context["field"] == "field_view"


def test_probe_load_and_save_results_preserve_typed_field_evidence() -> None:
    spec = FieldSpec("video.rgb", "video", "video.rgb.v1")
    value = FieldValue("payload", schema="video.rgb.v1", metadata={"source_id": "r001"})
    target = _field_ref()
    replacement_resource = ResourceRef("file:///derived/video.bin", "file")

    probe = CodecProbeResult(spec, metadata={"frames": 60})
    load = CodecLoadResult(value, metadata={"decoded": True})
    save = CodecSaveResult(
        target,
        resources=[replacement_resource],
        metadata={"written": True},
    )

    assert probe.field_spec is spec
    assert probe.metadata == {"frames": 60}
    assert load.field_value is value
    assert load.metadata == {"decoded": True}
    assert save.target is target
    assert save.resources == (replacement_resource,)
    assert save.metadata == {"written": True}
    with pytest.raises(TypeError):
        hash(probe)
    with pytest.raises(TypeError):
        hash(load)
    with pytest.raises(TypeError):
        hash(save)


def test_save_result_defaults_to_target_resources_and_rejects_invalid_resources() -> None:
    target = _field_ref()
    result = CodecSaveResult(target)

    assert result.resources == target.resources

    with pytest.raises(RemotePhysCodecError) as empty_resources:
        CodecSaveResult(target, resources=[])
    assert empty_resources.value.context["field"] == "resources"

    with pytest.raises(RemotePhysCodecError) as invalid_resource:
        CodecSaveResult(target, resources=[object()])  # type: ignore[list-item]
    assert invalid_resource.value.context["field"] == "resources"


def test_codec_results_reject_invalid_typed_components() -> None:
    with pytest.raises(RemotePhysCodecError) as invalid_probe:
        CodecProbeResult(object())  # type: ignore[arg-type]
    assert invalid_probe.value.context["field"] == "field_spec"

    with pytest.raises(RemotePhysCodecError) as invalid_load:
        CodecLoadResult(object())  # type: ignore[arg-type]
    assert invalid_load.value.context["field"] == "field_value"

    with pytest.raises(RemotePhysCodecError) as invalid_save:
        CodecSaveResult(object())  # type: ignore[arg-type]
    assert invalid_save.value.context["field"] == "target"

    with pytest.raises(RemotePhysCodecError) as invalid_metadata:
        CodecProbeResult(metadata={"obj": object()})
    assert invalid_metadata.value.context["field"] == "metadata"


def test_field_codec_is_structural_without_inheritance_requirement() -> None:
    class DuckCodec:
        capabilities = CodecCapabilities(can_probe=True, can_load=True, can_save=True)

        def probe(self, context: LoadContext) -> CodecProbeResult:
            return CodecProbeResult(FieldSpec("video.rgb", "video", "video.rgb.v1"))

        def load(self, context: LoadContext) -> CodecLoadResult:
            return CodecLoadResult(FieldValue("payload", schema="video.rgb.v1"))

        def save(self, value: FieldValue, context: SaveContext) -> CodecSaveResult:
            return CodecSaveResult(context.target)

    codec = DuckCodec()

    assert isinstance(codec, FieldCodec)
    assert codec.__class__.__mro__ == (DuckCodec, object)


def test_descriptors_do_not_gain_runtime_codec_hooks() -> None:
    resource = _resource()
    field_ref = _field_ref()
    field_view = _field_view()

    LoadContext(field_view)
    SaveContext(field_ref)
    CodecSaveResult(field_ref)

    for descriptor in [resource, field_ref, field_view]:
        for name in ["load", "save", "probe", "codec", "payload", "registry"]:
            assert not hasattr(descriptor, name)
