from __future__ import annotations

from rphys.data.sample_fields import SampleFieldState
from rphys.datasources.indexes import CompositeDataSourceIndex, DataSourceIndex
from rphys.datasources.indexes import DataSourceIndexEntry
from rphys.datasources.sources import IndexSampleSource
from tests.support.lazy_sample_builder_fixtures import (
    BVP,
    VIDEO,
    make_builder_fixture,
)


def test_stage9_sample_source_flow_builds_samples_from_data_source_index() -> None:
    fixture = make_builder_fixture()
    index = DataSourceIndex("stage9-index", [fixture.item], [_entry_for_item("stage9-index", 0, fixture.item)])
    source = IndexSampleSource(index, fixture.builder)

    sample = source.sample_at(0, request=[VIDEO, BVP])

    assert sample.field(VIDEO).state is SampleFieldState.UNLOADED
    assert sample.field(BVP).state is SampleFieldState.UNLOADED
    assert sample.require(VIDEO) == ("f1", "f2")
    assert sample.require(BVP) == (0.1, 0.2, 0.3)


def test_stage9_sample_source_flow_builds_samples_from_composite_index_with_ordered_subset() -> None:
    left = make_builder_fixture()
    right = make_builder_fixture(video_index=left.item.fields[VIDEO].field_index, bvp_index=left.item.fields[BVP].field_index)
    left_index = DataSourceIndex("left", [left.item], [_entry_for_item("left", 0, left.item)])
    right_index = DataSourceIndex("right", [right.item], [_entry_for_item("right", 0, right.item)])
    composite = CompositeDataSourceIndex(
        "stage9-composite",
        {"left": left_index, "right": right_index},
        metadata={"split": "stage9"},
    )
    source = IndexSampleSource(composite, left.builder)

    sample_left = source.sample_at(0, request=["targets/signal.bvp.reference", "inputs/video.rgb"])
    sample_right = source.sample_at(1, request=[VIDEO, BVP])

    assert [str(locator) for locator, _ in sample_left.field_items()] == [
        "targets/signal.bvp.reference",
        "inputs/video.rgb",
    ]
    assert [str(locator) for locator, _ in sample_right.field_items()] == [
        "inputs/video.rgb",
        "targets/signal.bvp.reference",
    ]


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
        source_key=index_id,
        field_windows={"targets/signal.bvp.reference": {"type": "full"}},
        metadata={"flow": "stage9"},
    )
