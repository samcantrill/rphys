from __future__ import annotations

import pytest

from rphys.data.containers import Sample
from rphys.data.locators import FieldLocator
from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.indexes import DataSourceIndex, DataSourceIndexEntry
from rphys.datasources.sources import IndexSampleSource, SampleRequest, WorkerContextFactory
import rphys.datasources as datasources
from rphys.errors import MissingFieldError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO, make_builder_fixture


def test_sample_source_exports_are_module_scoped() -> None:
    from rphys.datasources import sources

    assert sources.__all__ == [
        "SampleRequest",
        "SampleRuntimeContext",
        "WorkerContextFactory",
        "SampleSource",
        "IndexSampleSource",
    ]
    for public_name in sources.__all__:
        assert hasattr(sources, public_name)


def test_sample_source_names_are_not_parent_exports() -> None:
    assert not hasattr(datasources, "SampleRequest")
    assert not hasattr(datasources, "SampleRuntimeContext")
    assert not hasattr(datasources, "WorkerContextFactory")
    assert not hasattr(datasources, "SampleSource")
    assert not hasattr(datasources, "IndexSampleSource")


def test_sample_request_string_locator_round_trips() -> None:
    source = __import__("rphys.datasources.sources", fromlist=["SampleRequest"]).SampleRequest
    request = source(requested=("inputs/video.rgb", FieldLocator.parse("targets/signal.bvp.reference")))

    assert str(request.requested[0]) == "inputs/video.rgb"
    assert str(request.requested[1]) == "targets/signal.bvp.reference"


def test_index_sample_source_contract_returns_field_locator_keyed_samples() -> None:
    fixture = make_builder_fixture()
    source = _index_source("contract-source", fixture)

    sample = source[0]

    assert isinstance(sample, Sample)
    assert not isinstance(sample, tuple)
    assert not isinstance(sample, dict)
    assert [locator for locator, _ in sample.field_items()] == [VIDEO, BVP]
    assert sample.field(VIDEO).state is SampleFieldState.UNLOADED
    assert sample.field(BVP).state is SampleFieldState.UNLOADED


def test_index_sample_source_contract_preserves_requested_order_and_eager_mode() -> None:
    fixture = make_builder_fixture()
    source = _index_source("contract-source-request", fixture)

    sample = source.sample_at(
        0,
        request=SampleRequest(["targets/signal.bvp.reference", "inputs/video.rgb"], eager=True),
    )

    assert [locator for locator, _ in sample.field_items()] == [BVP, VIDEO]
    assert sample.field(BVP).state is SampleFieldState.LOADED
    assert sample.field(VIDEO).state is SampleFieldState.LOADED


def test_index_sample_source_contract_fails_loudly_for_missing_locators() -> None:
    source = _index_source("contract-source-missing", make_builder_fixture())

    with pytest.raises(MissingFieldError):
        source.sample_at(0, request="targets/signal.unknown")


def test_index_sample_source_contract_accepts_aligned_context_evidence() -> None:
    fixture = make_builder_fixture()
    index = _index_from_fixture("contract-source-context", fixture.item)
    source = IndexSampleSource(index, fixture.builder)
    request = SampleRequest(VIDEO)
    context = WorkerContextFactory(epoch=2, worker_id=1, worker_count=4).make_context(
        index_entry=index.entry_at(0),
        request=request,
    )

    sample = source.sample_at(0, request=request, context=context)

    assert isinstance(sample, Sample)
    assert context.position == 0
    assert context.split == "train"
    assert context.groups["subject"] == "subject-001"
    assert context.request_fingerprint == request.fingerprint
    assert context.worker_id == 1
    assert context.worker_count == 4


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
        source_key="contract-source",
        field_windows={"inputs/video.rgb": {"type": "full"}},
        metadata={"contract": "sample-source"},
    )
