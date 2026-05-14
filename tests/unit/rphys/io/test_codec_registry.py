from __future__ import annotations

import pytest

from rphys.data.fields import FieldValue
from rphys.errors import (
    CodecDependencyError,
    CodecOperationError,
    CodecResolutionError,
    InvalidCodecError,
    UnsupportedCodecIndexError,
    UnsupportedCodecOperationError,
)
from rphys.io.codecs import (
    CodecCapabilities,
    CodecLoadResult,
    CodecProbeResult,
    CodecRegistry,
    LoadContext,
    MetadataSavePolicy,
    SaveContext,
)
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import FieldIndex, TemporalIndexSlice
from rphys.io.resources import ResourceRef
from tests.support.synthetic_codecs import SyntheticCodec


class UnsupportedSyntheticIndex(FieldIndex):
    def to_dict(self) -> dict[str, object]:
        return {"type": "unsupported_synthetic_index"}


def _resource(uri: str = "file:///records/r001/video.bin") -> ResourceRef:
    return ResourceRef(uri, "file")


def _field_ref(key: str = "video.rgb") -> FieldRef:
    return FieldRef(
        key,
        [
            _resource(),
            _resource("file:///records/r001/video.meta.json"),
        ],
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )


def _load_context(
    key: str = "video.rgb",
    field_index: FieldIndex | None = None,
) -> LoadContext:
    return LoadContext(FieldView(_field_ref(key), field_index))


def _save_context(
    key: str = "video.rgb",
    policy: MetadataSavePolicy = MetadataSavePolicy.REFERENCE_ONLY,
) -> SaveContext:
    return SaveContext(_field_ref(key), metadata_policy=policy)


def test_registry_stores_codecs_in_registration_order_without_global_state() -> None:
    first = SyntheticCodec(name="first")
    second = SyntheticCodec(name="second", key="signal.bvp.reference")
    registry = CodecRegistry([first])

    returned = registry.register(second)

    assert returned is second
    assert registry.codecs == (first, second)
    assert CodecRegistry().codecs == ()
    with pytest.raises(AttributeError):
        registry.codecs.append(first)  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        hash(registry)


def test_registry_probe_resolves_one_codec_without_loading_payload() -> None:
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry([codec])

    result = registry.probe(_load_context())

    assert isinstance(result, CodecProbeResult)
    assert result.field_spec is not None
    assert str(result.field_spec.key) == "video.rgb"
    assert result.metadata == {"codec": "video", "resource_count": 2}
    assert codec.probe_calls == 1
    assert codec.load_calls == 0
    assert codec.save_calls == 0


def test_registry_load_preserves_field_index_without_full_load_fallback() -> None:
    codec = SyntheticCodec(name="video", payload=("f0", "f1", "f2", "f3"))
    registry = CodecRegistry([codec])

    result = registry.load(_load_context(field_index=TemporalIndexSlice(1, 3)))

    assert isinstance(result, CodecLoadResult)
    assert result.field_value.payload == ("f1", "f2")
    assert result.field_value.schema == "video.rgb.v1"
    assert result.metadata == {"codec": "video", "field_key": "video.rgb"}
    assert codec.load_calls == 1


def test_registry_rejects_unsupported_index_without_calling_load() -> None:
    codec = SyntheticCodec(name="video", payload=("f0", "f1", "f2", "f3"))
    registry = CodecRegistry([codec])

    with pytest.raises(UnsupportedCodecIndexError) as exc_info:
        registry.load(_load_context(field_index=TemporalIndexSlice(0, 4, 2)))

    assert exc_info.value.context["field_key"] == "video.rgb"
    assert codec.load_calls == 0

    with pytest.raises(UnsupportedCodecIndexError):
        registry.load(_load_context(field_index=UnsupportedSyntheticIndex()))
    assert codec.load_calls == 0


def test_registry_reports_no_match_and_ambiguous_matches() -> None:
    context = _load_context()
    other = SyntheticCodec(name="other", key="signal.bvp.reference")
    registry = CodecRegistry([other])

    with pytest.raises(CodecResolutionError) as no_match:
        registry.probe(context)
    assert no_match.value.context["operation"] == "probe"
    assert no_match.value.context["field_key"] == "video.rgb"

    first = SyntheticCodec(name="first")
    second = SyntheticCodec(name="second")
    ambiguous = CodecRegistry([first, second])

    with pytest.raises(CodecResolutionError) as ambiguous_error:
        ambiguous.load(context)
    assert ambiguous_error.value.context["operation"] == "load"
    assert ambiguous_error.value.context["matches"] == ["0:first", "1:second"]
    assert first.load_calls == 0
    assert second.load_calls == 0


def test_registry_distinguishes_unsupported_operation_from_missing_match() -> None:
    class ProbeOnlyCodec:
        name = "probe-only"
        capabilities = CodecCapabilities(can_probe=True)

        def probe(self, context: LoadContext) -> CodecProbeResult:
            return CodecProbeResult()

    registry = CodecRegistry([ProbeOnlyCodec()])

    with pytest.raises(UnsupportedCodecOperationError) as exc_info:
        registry.load(_load_context())

    assert exc_info.value.context == {"operation": "load", "registered": 1}


def test_registry_validates_structural_codec_shape() -> None:
    with pytest.raises(InvalidCodecError) as missing_capabilities:
        CodecRegistry([object()])
    assert missing_capabilities.value.context["field"] == "capabilities"

    class MissingLoadMethod:
        name = "missing-load"
        capabilities = CodecCapabilities(can_load=True)

    with pytest.raises(InvalidCodecError) as missing_method:
        CodecRegistry([MissingLoadMethod()]).load(_load_context())
    assert missing_method.value.context["field"] == "load"

    class NonBoolSupport:
        name = "non-bool-support"
        capabilities = CodecCapabilities(can_probe=True)

        def supports_probe(self, context: LoadContext) -> str:
            return "yes"

        def probe(self, context: LoadContext) -> CodecProbeResult:
            return CodecProbeResult()

    with pytest.raises(InvalidCodecError) as non_bool:
        CodecRegistry([NonBoolSupport()]).probe(_load_context())
    assert non_bool.value.context["field"] == "supports_probe"


def test_registry_wraps_dependency_unavailable_at_operation_boundary() -> None:
    codec = SyntheticCodec(name="video", dependency_available=False)
    registry = CodecRegistry([codec])

    with pytest.raises(CodecDependencyError) as exc_info:
        registry.load(_load_context())

    assert exc_info.value.context["operation"] == "load"
    assert exc_info.value.context["codec"] == "video"
    assert codec.load_calls == 0


def test_registry_wraps_wrong_operation_result_type() -> None:
    class WrongResultCodec:
        name = "wrong-result"
        capabilities = CodecCapabilities(can_probe=True)

        def probe(self, context: LoadContext) -> object:
            return object()

    with pytest.raises(CodecOperationError) as exc_info:
        CodecRegistry([WrongResultCodec()]).probe(_load_context())

    assert exc_info.value.context["operation"] == "probe"
    assert exc_info.value.context["expected"] == "CodecProbeResult"


def test_registry_save_preserves_target_resources_and_metadata_policy() -> None:
    codec = SyntheticCodec(name="video")
    registry = CodecRegistry([codec])
    value = FieldValue(
        "payload",
        schema="video.rgb.v1",
        metadata={"source_id": "camera-front"},
    )

    reference_only = registry.save(value, _save_context())
    include_metadata = registry.save(
        value,
        _save_context(policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA),
    )

    assert reference_only.target == _field_ref()
    assert reference_only.resources == _field_ref().resources
    assert reference_only.metadata == {
        "codec": "video",
        "metadata_policy": "reference_only",
    }
    assert include_metadata.metadata == {
        "codec": "video",
        "metadata_policy": "include_field_metadata",
        "field_metadata": {"source_id": "camera-front"},
    }
    assert codec.save_calls == 2
    assert [context.metadata_policy for _, context in codec.saved] == [
        MetadataSavePolicy.REFERENCE_ONLY,
        MetadataSavePolicy.INCLUDE_FIELD_METADATA,
    ]


def test_registry_save_matches_declared_metadata_policies() -> None:
    codec = SyntheticCodec(
        name="reference-only",
        capabilities=CodecCapabilities(
            can_save=True,
            metadata_policies=(MetadataSavePolicy.REFERENCE_ONLY,),
        ),
    )
    registry = CodecRegistry([codec])

    with pytest.raises(CodecResolutionError) as unsupported_policy:
        registry.save(
            FieldValue("payload", metadata={"source_id": "camera-front"}),
            _save_context(policy=MetadataSavePolicy.INCLUDE_FIELD_METADATA),
        )

    assert unsupported_policy.value.context["operation"] == "save"
    assert unsupported_policy.value.context["field_key"] == "video.rgb"
    assert codec.save_calls == 0


def test_registry_save_rejects_invalid_value_and_context_types() -> None:
    registry = CodecRegistry([SyntheticCodec(name="video")])

    with pytest.raises(CodecOperationError) as invalid_value:
        registry.save(object(), _save_context())  # type: ignore[arg-type]
    assert invalid_value.value.context["field"] == "value"

    with pytest.raises(CodecOperationError) as invalid_context:
        registry.save(FieldValue("payload"), object())  # type: ignore[arg-type]
    assert invalid_context.value.context["field"] == "context"


def test_synthetic_codec_is_not_public_package_api() -> None:
    import rphys.io.codecs as codecs

    assert not hasattr(codecs, "SyntheticCodec")
