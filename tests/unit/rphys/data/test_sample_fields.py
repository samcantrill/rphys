from __future__ import annotations

import copy

import pytest

from rphys.data.collation import CollatePolicy, collate_samples
from rphys.data.containers import FieldContainer, Sample
from rphys.data.contracts import FieldRequirement, SampleContract
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.errors import CodecOperationError
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


VIDEO = FieldLocator.parse("inputs/video.rgb")
BVP = FieldLocator.parse("targets/signal.bvp.reference")


class CountingLoader:
    def __init__(self, result: CodecLoadResult | BaseException | object) -> None:
        self.result = result
        self.calls = 0
        self.contexts: list[LoadContext] = []

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        self.contexts.append(context)
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result  # type: ignore[return-value]


def _load_context(
    key: str = "video.rgb",
    *,
    schema: str = "video.rgb.v1",
) -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                key,
                [ResourceRef("file:///records/r001/video.bin", "file")],
                schema=schema,
                metadata={"source_id": "camera-front"},
            ),
            TemporalIndexSlice(0, 2),
        )
    )


def _load_result(
    payload: object = ("f0", "f1"),
    *,
    schema: str = "video.rgb.v1",
    collate_policy: object | None = None,
) -> CodecLoadResult:
    return CodecLoadResult(
        FieldValue(
            payload,
            schema=schema,
            metadata={"loaded_by": "unit"},
            collate_policy=collate_policy,
        ),
        metadata={"codec": "unit"},
    )


def _sample_field(
    loader: CountingLoader | None = None,
    *,
    collate_policy: object | None = None,
) -> tuple[SampleField, CountingLoader]:
    actual_loader = loader or CountingLoader(_load_result(collate_policy=collate_policy))
    return (
        SampleField(
            _load_context(),
            actual_loader,
            collate_policy=collate_policy,
        ),
        actual_loader,
    )


def test_sample_field_initial_state_is_inspectable_without_loading() -> None:
    field, loader = _sample_field()

    assert isinstance(field, FieldValue)
    assert field.state is SampleFieldState.UNLOADED
    assert field.loaded is False
    assert field.failed is False
    assert field.load_result is None
    assert field.load_error is None
    assert field.field_value is None
    assert field.load_context.field_view.field_ref.key == "video.rgb"
    assert field.schema == "video.rgb.v1"
    assert field.metadata[MetadataKey("source_id")] == "camera-front"
    assert loader.calls == 0


def test_payload_access_loads_once_and_retains_result() -> None:
    field, loader = _sample_field()

    assert field.payload == ("f0", "f1")
    assert field.payload == ("f0", "f1")

    assert loader.calls == 1
    assert field.state is SampleFieldState.LOADED
    assert field.loaded is True
    assert field.load_result is not None
    assert field.field_value is field.load_result.field_value
    assert field.metadata == {MetadataKey("loaded_by"): "unit"}
    assert loader.contexts == [field.load_context]


def test_eager_load_uses_same_state_machine_as_payload_access() -> None:
    field, loader = _sample_field()

    result = field.eager_load()

    assert result is field.load_result
    assert field.payload == ("f0", "f1")
    assert loader.calls == 1


def test_failed_load_is_retained_and_reraised_without_retry() -> None:
    error = RuntimeError("decode failed")
    field, loader = _sample_field(CountingLoader(error))

    with pytest.raises(RuntimeError) as first:
        _ = field.payload
    with pytest.raises(RuntimeError) as second:
        field.load()

    assert first.value is error
    assert second.value is error
    assert field.state is SampleFieldState.FAILED
    assert field.failed is True
    assert field.load_error is error
    assert loader.calls == 1


def test_loader_result_type_is_validated_and_failure_is_retained() -> None:
    field, loader = _sample_field(CountingLoader(object()))

    with pytest.raises(CodecOperationError) as exc_info:
        field.load()
    with pytest.raises(CodecOperationError) as retained:
        _ = field.payload

    assert exc_info.value is retained.value
    assert exc_info.value.context["actual"] == "object"
    assert field.state is SampleFieldState.FAILED
    assert loader.calls == 1


def test_sample_stores_lazy_handle_as_field_object_without_loading() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})

    assert isinstance(sample, FieldContainer)
    assert sample.field(VIDEO) is field
    assert sample.field_items() == ((VIDEO, field),)
    assert sample.role("inputs")[VIDEO] is field
    assert sample.field(VIDEO).field_value is None
    assert loader.calls == 0


def test_payload_demanding_sample_accessors_load_once() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})

    assert sample.get(VIDEO, expected_type=tuple, schema="video.rgb.v1") == (
        "f0",
        "f1",
    )
    assert sample.require(VIDEO, expected_type=tuple) == ("f0", "f1")

    assert loader.calls == 1
    assert sample.field(VIDEO) is field


def test_sample_contract_validation_loads_lazy_required_payloads() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})
    contract = SampleContract(
        [FieldRequirement(VIDEO, expected_type=tuple, schema="video.rgb.v1")]
    )

    assert contract.validate(sample) is sample
    assert loader.calls == 1


def test_lazy_fields_collate_through_payload_demanding_list_policy() -> None:
    first, first_loader = _sample_field(collate_policy=CollatePolicy.LIST)
    second, second_loader = _sample_field(
        CountingLoader(_load_result(("g0", "g1"), collate_policy=CollatePolicy.LIST)),
        collate_policy=CollatePolicy.LIST,
    )

    batch = collate_samples([Sample({VIDEO: first}), Sample({VIDEO: second})])

    assert batch.require(VIDEO) == [("f0", "f1"), ("g0", "g1")]
    assert batch.field(VIDEO).schema == "video.rgb.v1"
    assert batch.field(VIDEO).metadata[MetadataKey("loaded_by")] == ["unit", "unit"]
    assert first_loader.calls == 1
    assert second_loader.calls == 1


def test_shallow_and_deep_copy_do_not_force_load() -> None:
    field, loader = _sample_field()

    shallow = copy.copy(field)
    deep = copy.deepcopy(field)

    assert shallow is not field
    assert deep is not field
    assert shallow.state is SampleFieldState.UNLOADED
    assert deep.state is SampleFieldState.UNLOADED
    assert loader.calls == 0


def test_deep_copy_of_loaded_field_copies_loaded_payload_without_reloading() -> None:
    payload = [["f0"]]
    field, loader = _sample_field(CountingLoader(_load_result(payload)))
    field.eager_load()

    copied = copy.deepcopy(field)

    assert copied.state is SampleFieldState.LOADED
    assert copied.payload == [["f0"]]
    assert copied.payload is not payload
    assert loader.calls == 1


def test_container_copy_preserves_lazy_handles_without_forcing_load() -> None:
    field, loader = _sample_field()
    sample = Sample({VIDEO: field})

    shallow = sample.shallow_copy()
    deep = sample.deep_copy()

    assert shallow.field(VIDEO) is field
    assert deep.field(VIDEO) is not field
    assert deep.field(VIDEO).state is SampleFieldState.UNLOADED
    assert loader.calls == 0


def test_sample_field_constructor_rejects_invalid_inputs() -> None:
    with pytest.raises(CodecOperationError) as invalid_context:
        SampleField(object(), lambda context: _load_result())  # type: ignore[arg-type]
    assert invalid_context.value.context["field"] == "load_context"

    with pytest.raises(CodecOperationError) as invalid_loader:
        SampleField(_load_context(), object())  # type: ignore[arg-type]
    assert invalid_loader.value.context["field"] == "loader"
