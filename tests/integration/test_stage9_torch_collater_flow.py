from __future__ import annotations

from rphys.data import Batch, BatchCollater, CollatePolicy
from rphys.datasources.indexes import DataSourceIndex, DataSourceIndexEntry
from rphys.datasources.sources import SampleRequest
from rphys.datasources.torch import TorchIndexSampleDataset
from tests.support.lazy_sample_builder_fixtures import BVP, VIDEO, make_builder_fixture


def test_stage9_torch_dataset_to_batch_collater_flow_preserves_field_locators() -> None:
    fixture = make_builder_fixture()
    index = DataSourceIndex(
        "stage9-torch-collater",
        [fixture.item, fixture.item],
        [
            _entry_for_item("stage9-torch-collater", 0, fixture.item),
            _entry_for_item("stage9-torch-collater", 1, fixture.item),
        ],
    )
    dataset = TorchIndexSampleDataset(index, fixture.builder, request=SampleRequest([VIDEO, BVP], eager=True))
    samples = [dataset[0], dataset[1]]
    for sample in samples:
        for _, field_value in sample.field_items():
            field_value.collate_policy = "list"

    batch = BatchCollater()(samples)

    assert isinstance(batch, Batch)
    assert [locator for locator, _ in batch.field_items()] == [VIDEO, BVP]
    assert batch.field(VIDEO).collate_policy is CollatePolicy.LIST
    assert batch.require(VIDEO) == [("f1", "f2"), ("f1", "f2")]
    assert batch.require(BVP) == [(0.1, 0.2, 0.3), (0.1, 0.2, 0.3)]


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
        source_key="torch",
        field_windows={"inputs/video.rgb": {"type": "full"}},
        metadata={"flow": "stage9"},
    )
