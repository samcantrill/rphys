from __future__ import annotations

import pytest

from rphys.data.collation import CollatePolicy, collate_samples
from rphys.data.containers import Sample
from rphys.data.contracts import FieldRequirement, SampleContract
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleField, SampleFieldState
from rphys.io.codecs import CodecLoadResult, LoadContext
from rphys.io.fields import FieldRef, FieldView
from rphys.io.indexes import TemporalIndexSlice
from rphys.io.resources import ResourceRef


VIDEO = FieldLocator.parse("inputs/video.rgb")


class Loader:
    def __init__(self, payload: object | BaseException) -> None:
        self.payload = payload
        self.calls = 0

    def __call__(self, context: LoadContext) -> CodecLoadResult:
        self.calls += 1
        if isinstance(self.payload, BaseException):
            raise self.payload
        return CodecLoadResult(
            FieldValue(
                self.payload,
                schema="video.rgb.v1",
                metadata={"source_id": "loaded"},
                collate_policy=CollatePolicy.LIST,
            ),
            metadata={"codec": "contract"},
        )


class CopyingMappedPayload:
    def __init__(self, value: str) -> None:
        self.value = value

    def map_tensors(self, mapper):
        return type(self)(mapper(self.value))


def _context() -> LoadContext:
    return LoadContext(
        FieldView(
            FieldRef(
                "video.rgb",
                [ResourceRef("file:///records/r001/video.bin", "file")],
                schema="video.rgb.v1",
                metadata={"source_id": "descriptor"},
            ),
            TemporalIndexSlice(0, 2),
        )
    )


def test_lazy_sample_field_contract_loads_on_payload_demand_only() -> None:
    loader = Loader(("f0", "f1"))
    field = SampleField(_context(), loader, collate_policy=CollatePolicy.LIST)
    sample = Sample({VIDEO: field})

    assert sample.field(VIDEO) is field
    assert field.state is SampleFieldState.UNLOADED
    assert loader.calls == 0

    assert sample.require(VIDEO, expected_type=tuple, schema="video.rgb.v1") == (
        "f0",
        "f1",
    )
    assert sample.field(VIDEO) is field
    assert field.state is SampleFieldState.LOADED
    assert field.load_result is not None
    assert loader.calls == 1


def test_lazy_sample_field_contract_retains_failures_without_retry() -> None:
    error = RuntimeError("decode failed")
    loader = Loader(error)
    field = SampleField(_context(), loader)
    sample = Sample({VIDEO: field})

    with pytest.raises(RuntimeError):
        sample.require(VIDEO)
    with pytest.raises(RuntimeError):
        field.eager_load()

    assert field.state is SampleFieldState.FAILED
    assert field.load_error is error
    assert loader.calls == 1


def test_lazy_sample_field_contract_works_with_contracts_and_list_collation() -> None:
    first_loader = Loader(("f0", "f1"))
    second_loader = Loader(("g0", "g1"))
    first = SampleField(_context(), first_loader, collate_policy=CollatePolicy.LIST)
    second = SampleField(_context(), second_loader, collate_policy=CollatePolicy.LIST)
    contract = SampleContract(
        [FieldRequirement(VIDEO, expected_type=tuple, schema="video.rgb.v1")]
    )

    first_sample = Sample({VIDEO: first})
    second_sample = Sample({VIDEO: second})

    assert contract.validate(first_sample) is first_sample
    batch = collate_samples([first_sample, second_sample])

    assert batch.require(VIDEO) == [("f0", "f1"), ("g0", "g1")]
    assert first_loader.calls == 1
    assert second_loader.calls == 1


def test_lazy_sample_field_contract_map_tensors_preserves_handle() -> None:
    loader = Loader(CopyingMappedPayload("f0"))
    field = SampleField(_context(), loader, collate_policy=CollatePolicy.LIST)
    sample = Sample({VIDEO: field})

    assert sample.map_tensors_(lambda value: f"{value}:mapped") is sample

    assert sample.field(VIDEO) is field
    assert field.state is SampleFieldState.LOADED
    assert loader.calls == 1
    assert field.load_result is not None
    assert field.load_result.metadata["codec"] == "contract"
    assert field.payload.value == "f0:mapped"
