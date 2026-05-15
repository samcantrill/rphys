from __future__ import annotations

import pytest

from rphys.data.containers import Sample
from rphys.data.sample_fields import SampleFieldState
from rphys.data.locators import FieldLocator
from rphys.datasources.indexes import DataSourceIndex, DataSourceIndexEntry
from rphys.datasources.sources import (
    IndexSampleSource,
    SampleRequest,
    SampleRuntimeContext,
    WorkerContextFactory,
)
from rphys.errors import FieldTypeError, MissingFieldError, RemotePhysDataSourceError
from tests.support.lazy_sample_builder_fixtures import VIDEO, BVP, make_builder_fixture


def test_sample_request_keeps_request_none_as_all_fields() -> None:
    request = SampleRequest()

    assert request.requested is None
    assert request.eager is False
    assert request.operation_fingerprint is None
    assert request.materialization_fingerprint is None
    assert isinstance(request.fingerprint, str)
    assert len(request.fingerprint) == 64


def test_sample_request_parse_and_preserves_string_order() -> None:
    request = SampleRequest([VIDEO, "targets/signal.bvp.reference"])

    assert request.requested == (VIDEO, FieldLocator.parse("targets/signal.bvp.reference"))
    assert [str(locator) for locator in request.requested] == [
        "inputs/video.rgb",
        "targets/signal.bvp.reference",
    ]


def test_sample_request_rejects_empty_explicit_request() -> None:
    with pytest.raises(FieldTypeError, match="Requested fields must not be empty"):
        SampleRequest([])


def test_sample_request_rejects_duplicate_locators() -> None:
    with pytest.raises(FieldTypeError, match="Requested locators must be unique"):
        SampleRequest([VIDEO, VIDEO])


def test_sample_request_rejects_non_locator_input() -> None:
    with pytest.raises(FieldTypeError):
        SampleRequest(123)  # type: ignore[arg-type]


def test_sample_request_fingerprint_is_deterministic_for_ordered_requests() -> None:
    request_first = SampleRequest(["targets/signal.bvp.reference", VIDEO])
    request_second = SampleRequest(["targets/signal.bvp.reference", VIDEO])
    assert request_first.fingerprint == request_second.fingerprint


def test_sample_request_supports_optional_primitive_fingerprints() -> None:
    request = SampleRequest(
        requested=VIDEO,
        eager=True,
        operation_fingerprint={"stage": 1},
        materialization_fingerprint=[1, 2, 3],
    )
    assert request.operation_fingerprint == {"stage": 1}
    assert request.materialization_fingerprint == (1, 2, 3)


def test_sample_request_rejects_non_primitive_metadata_fingerprint() -> None:
    with pytest.raises(FieldTypeError):
        SampleRequest(operation_fingerprint=object())  # type: ignore[arg-type]


def test_sample_request_and_context_metadata_are_primitive_and_deterministic() -> None:
    fixture = make_builder_fixture()
    entry = _entry_for_item("sample-request", 0, fixture_item=fixture.item)
    context = WorkerContextFactory(epoch=1, worker_id=3, metadata={"scope": "unit"}).make_context(
        index_entry=entry,
        request=SampleRequest(VIDEO),
    )

    assert isinstance(context.fingerprint, str)
    assert len(context.fingerprint) == 64
    assert context.epoch == 1
    assert context.worker_id == 3
    assert context.metadata["scope"] == "unit"


def test_sample_runtime_context_rejects_invalid_position_values() -> None:
    with pytest.raises(FieldTypeError):
        SampleRuntimeContext(
            index_id="idx",
            entry_id="idx:0",
            position=-1,
            candidate_id="candidate",
            record_id="record",
            datasource_id="source",
            request_fingerprint="r",
        )


def test_worker_context_factory_rejects_bad_inputs() -> None:
    with pytest.raises(RemotePhysDataSourceError):
        WorkerContextFactory().make_context(index_entry=object(), request=SampleRequest())

    with pytest.raises(FieldTypeError):
        WorkerContextFactory().make_context(index_entry=_index_entry(), request=object())  # type: ignore[arg-type]


def test_index_sample_source_getitem_defaults_to_all_fields() -> None:
    fixture = make_builder_fixture()
    source = _index_source(fixture.item.record.record_id, fixture)

    sample = source[0]

    assert isinstance(sample, Sample)
    assert sample.field("inputs/video.rgb").state is SampleFieldState.UNLOADED
    assert sample.field("targets/signal.bvp.reference").state is SampleFieldState.UNLOADED


def test_index_sample_source_respects_ordered_subset_request() -> None:
    fixture = make_builder_fixture()
    source = _index_source("sample-source-request", fixture)

    sample = source.sample_at(0, request=["targets/signal.bvp.reference", "inputs/video.rgb"])

    assert [str(locator) for locator, _ in sample.field_items()] == [
        "targets/signal.bvp.reference",
        "inputs/video.rgb",
    ]
    assert sample.field("targets/signal.bvp.reference").state is SampleFieldState.UNLOADED


def test_index_sample_source_eager_request_loads_requested_fields() -> None:
    fixture = make_builder_fixture()
    source = _index_source("sample-source-eager", fixture)

    sample = source.sample_at(0, request=SampleRequest([VIDEO, BVP], eager=True))

    assert sample.field(VIDEO).state is SampleFieldState.LOADED
    assert sample.field(BVP).state is SampleFieldState.LOADED


def test_index_sample_source_rejects_invalid_positions() -> None:
    source = _index_source("sample-source-pos", make_builder_fixture())

    with pytest.raises(FieldTypeError):
        source.sample_at(True)
    with pytest.raises(FieldTypeError):
        source.sample_at(-1)
    with pytest.raises(FieldTypeError):
        source.sample_at("0")  # type: ignore[arg-type]
    with pytest.raises(RemotePhysDataSourceError):
        source.sample_at(2)


def test_index_sample_source_rejects_invalid_request_and_context() -> None:
    source = _index_source("sample-source-invalid", make_builder_fixture())

    with pytest.raises(FieldTypeError, match="Requested fields must not be empty"):
        source.sample_at(0, request=[])
    with pytest.raises(FieldTypeError, match="context must be a SampleRuntimeContext"):
        source.sample_at(0, context=object())  # type: ignore[arg-type]


def test_index_sample_source_rejects_missing_request_fields() -> None:
    source = _index_source("sample-source-missing", make_builder_fixture())

    with pytest.raises(MissingFieldError):
        source.sample_at(0, request="targets/signal.foo")


def test_index_sample_source_rejects_constructor_type_errors() -> None:
    with pytest.raises(RemotePhysDataSourceError):
        IndexSampleSource(object(), object())  # type: ignore[arg-type]
    with pytest.raises(RemotePhysDataSourceError):
        IndexSampleSource(_index_object(), object())  # type: ignore[arg-type]


def _index_source(index_id: str, fixture) -> IndexSampleSource:
    return IndexSampleSource(
        _index_from_fixture(index_id, fixture.item),
        fixture.builder,
    )


def _index_from_fixture(index_id: str, fixture_item) -> DataSourceIndex:
    return DataSourceIndex(
        index_id,
        [fixture_item],
        [_entry_for_item(index_id, 0, fixture_item)],
    )


def _entry_for_item(
    index_id: str,
    position: int,
    fixture_item,
) -> DataSourceIndexEntry:
    return DataSourceIndexEntry(
        index_id=index_id,
        entry_id=f"{index_id}:{position}",
        position=position,
        candidate_id=f"candidate-{position}",
        record_id=fixture_item.record.record_id,
        datasource_id=fixture_item.record.datasource.datasource_id,
        source_id=fixture_item.record.datasource.datasource_id,
        groups={"subject": "subject-001", "source": fixture_item.record.datasource.datasource_id},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        source_key="source-key",
        field_windows={"inputs/video.rgb": {"type": "full"}},
        metadata={"stage": "unit"},
    )


def _index_entry() -> DataSourceIndexEntry:
    fixture = make_builder_fixture()
    return _entry_for_item("entry", 0, fixture.item)


def _index_object() -> DataSourceIndex:
    fixture = make_builder_fixture()
    return _index_from_fixture("other", fixture.item)
