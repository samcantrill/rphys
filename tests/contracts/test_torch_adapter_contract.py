from __future__ import annotations

import pytest

import rphys.datasources.torch as torch_adapters
from rphys.data import BatchCollater, FieldValue, Sample
from rphys.data.locators import FieldLocator
from rphys.datasources.sources import SampleRequest, SampleSource
from rphys.datasources.torch import (
    TorchDataLoaderBuilder,
    TorchSampleSourceDataset,
)
from rphys.errors import RemotePhysDependencyError


VIDEO = FieldLocator.parse("inputs/video.rgb")


def test_torch_sample_source_dataset_contract_returns_samples_without_formatting() -> None:
    source = ContractSource()
    dataset = TorchSampleSourceDataset(source, request=SampleRequest(VIDEO))

    sample = dataset[0]

    assert isinstance(sample, Sample)
    assert not isinstance(sample, tuple)
    assert not isinstance(sample, dict)
    assert sample.require(VIDEO) == "frame-0"
    assert source.requests == [SampleRequest(VIDEO)]


def test_torch_dataloader_builder_contract_uses_explicit_collation_and_typed_dependency_failure(monkeypatch) -> None:
    def missing_import(name: str):
        if name == "torch.utils.data":
            raise ImportError("missing torch")
        return __import__(name)

    monkeypatch.setattr(torch_adapters.importlib, "import_module", missing_import)
    builder = TorchDataLoaderBuilder(collate_fn=BatchCollater())

    with pytest.raises(RemotePhysDependencyError) as exc_info:
        builder.build(TorchSampleSourceDataset(ContractSource()))

    assert exc_info.value.context["dependency"] == "torch"
    assert exc_info.value.context["module"] == "torch.utils.data"


class ContractSource(SampleSource):
    def __init__(self) -> None:
        self.requests: list[object] = []

    def __len__(self) -> int:
        return 1

    def sample_at(self, position: int, request=None, context=None) -> Sample:
        self.requests.append(request)
        return Sample(
            {
                VIDEO: FieldValue(
                    f"frame-{position}",
                    schema="video.rgb.v1",
                    collate_policy="list",
                )
            }
        )
