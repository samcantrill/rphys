from __future__ import annotations

from types import ModuleType

import pytest

import rphys.datasources.torch as torch_adapters
from rphys.data.collation import BatchCollater
from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.datasources.indexes import DataSourceIndex, DataSourceIndexEntry
from rphys.datasources.sources import SampleRequest, SampleSource
from rphys.datasources.torch import (
    TorchDataLoaderBuilder,
    TorchDataLoaderPlan,
    TorchIndexSampleDataset,
    TorchSampleSourceDataset,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError, RemotePhysDependencyError
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO, make_builder_fixture


def test_torch_sample_source_dataset_delegates_length_and_default_item_access() -> None:
    source = RecordingSampleSource([_sample("frame-0"), _sample("frame-1")])
    dataset = TorchSampleSourceDataset(source)

    sample = dataset[1]

    assert len(dataset) == 2
    assert sample.require(VIDEO) == "frame-1"
    assert source.calls == [(1, None)]


def test_torch_sample_source_dataset_forwards_configured_request() -> None:
    source = RecordingSampleSource([_sample("frame-0")])
    request = SampleRequest(VIDEO, eager=True)
    dataset = TorchSampleSourceDataset(source, request=request)

    sample = dataset[0]

    assert sample.require(VIDEO) == "frame-0"
    assert source.calls == [(0, request)]


def test_torch_sample_source_dataset_rejects_non_source_inputs() -> None:
    with pytest.raises(RemotePhysDataSourceError):
        TorchSampleSourceDataset(object())  # type: ignore[arg-type]


def test_torch_index_sample_dataset_wraps_existing_index_source() -> None:
    fixture = make_builder_fixture()
    index = DataSourceIndex(
        "torch-index",
        [fixture.item],
        [_entry_for_item("torch-index", 0, fixture.item)],
    )

    dataset = TorchIndexSampleDataset(index, fixture.builder, request=SampleRequest(VIDEO, eager=True))
    sample = dataset[0]

    assert sample.require(VIDEO) == ("f1", "f2")
    assert dataset.index_source is dataset.source


def test_torch_dataloader_plan_is_data_only_and_validated() -> None:
    plan = TorchDataLoaderPlan(batch_size=4, shuffle=True, drop_last=True, num_workers=2)

    assert plan.to_kwargs() == {
        "batch_size": 4,
        "shuffle": True,
        "drop_last": True,
        "num_workers": 2,
    }

    with pytest.raises(FieldTypeError):
        TorchDataLoaderPlan(batch_size=0)
    with pytest.raises(FieldTypeError):
        TorchDataLoaderPlan(shuffle=1)  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError):
        TorchDataLoaderPlan(num_workers=-1)


def test_torch_dataloader_builder_rejects_invalid_inputs() -> None:
    with pytest.raises(FieldTypeError):
        TorchDataLoaderBuilder(plan=object())  # type: ignore[arg-type]
    with pytest.raises(FieldTypeError):
        TorchDataLoaderBuilder(collate_fn=object())  # type: ignore[arg-type]


def test_torch_dataloader_builder_raises_typed_error_when_torch_is_missing(monkeypatch) -> None:
    def missing_import(name: str):
        if name == "torch.utils.data":
            raise ImportError("missing torch")
        return __import__(name)

    monkeypatch.setattr(torch_adapters.importlib, "import_module", missing_import)

    with pytest.raises(RemotePhysDependencyError) as exc_info:
        TorchDataLoaderBuilder().build(TorchSampleSourceDataset(RecordingSampleSource([_sample("frame-0")])))

    assert exc_info.value.context["dependency"] == "torch"
    assert exc_info.value.context["operation"] == "TorchDataLoaderBuilder.build"


def test_torch_dataloader_builder_uses_fake_torch_dataloader_with_explicit_collater(monkeypatch) -> None:
    class FakeDataLoader:
        def __init__(self, dataset, **kwargs) -> None:
            self.dataset = dataset
            self.kwargs = kwargs

    fake_module = ModuleType("torch.utils.data")
    fake_module.DataLoader = FakeDataLoader

    def fake_import(name: str):
        if name == "torch.utils.data":
            return fake_module
        return __import__(name)

    monkeypatch.setattr(torch_adapters.importlib, "import_module", fake_import)
    dataset = TorchSampleSourceDataset(RecordingSampleSource([_sample("frame-0")]))
    collater = BatchCollater()
    builder = TorchDataLoaderBuilder(
        plan=TorchDataLoaderPlan(batch_size=2, shuffle=True),
        collate_fn=collater,
    )

    loader = builder.build(dataset)

    assert isinstance(loader, FakeDataLoader)
    assert loader.dataset is dataset
    assert loader.kwargs["collate_fn"] is collater
    assert loader.kwargs["batch_size"] == 2
    assert loader.kwargs["shuffle"] is True
    assert loader.kwargs["drop_last"] is False


def test_torch_dataloader_builder_rejects_malformed_fake_torch(monkeypatch) -> None:
    fake_module = ModuleType("torch.utils.data")
    fake_module.DataLoader = object()

    def fake_import(name: str):
        if name == "torch.utils.data":
            return fake_module
        return __import__(name)

    monkeypatch.setattr(torch_adapters.importlib, "import_module", fake_import)

    with pytest.raises(RemotePhysDependencyError):
        TorchDataLoaderBuilder().build(TorchSampleSourceDataset(RecordingSampleSource([_sample("frame-0")])))


class RecordingSampleSource(SampleSource):
    def __init__(self, samples: list[Sample]) -> None:
        self.samples = samples
        self.calls: list[tuple[int, object]] = []

    def __len__(self) -> int:
        return len(self.samples)

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        self.calls.append((position, request))
        return self.samples[position]


def _sample(video_payload: object) -> Sample:
    return Sample(
        {
            VIDEO: FieldValue(
                video_payload,
                schema="video.rgb.v1",
                collate_policy="list",
            ),
            BVP: FieldValue(
                [0.1],
                schema="signal.bvp.v1",
                collate_policy="list",
            ),
        }
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
        groups={"subject": "subject-001"},
        split="train",
        split_group="subject",
        split_group_value="subject-001",
        source_key="torch",
        field_windows={"inputs/video.rgb": {"type": "full"}},
        metadata={"stage": "unit"},
    )
