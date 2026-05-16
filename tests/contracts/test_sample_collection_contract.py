from __future__ import annotations

from rphys.collections import CollectionItem, CollectorResult
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionViewPlan,
    SampleCollector,
)


def _entry(value: int, window_start: int) -> CollectionItem[Sample]:
    return CollectionItem(
        Sample({"inputs/signal.bvp": FieldValue([value])}),
        metadata={
            "subject_id": "s1",
            "record_id": "r1",
            "window_start": window_start,
            "window_stop": window_start + 1,
        },
    )


def test_samples_materialize_to_collection_then_view_returns_collection_snapshot() -> None:
    collector = SampleCollector(required_metadata=("record_id", "window_start"))
    result = collector((_entry(3, 3), _entry(1, 1), _entry(2, 2)))
    view = PlannedSampleCollectionView(
        SampleCollectionViewPlan(
            "sort-windows",
            group_keys=("record_id",),
            sort_keys=("window_start",),
        )
    )

    output = view(result.collection)

    assert isinstance(result, CollectorResult)
    assert isinstance(result.collection, SampleCollection)
    assert isinstance(output, SampleCollection)
    assert [sample.get("inputs/signal.bvp")[0] for sample in output] == [1, 2, 3]
    assert output.entries[0].metadata["window_start"] == 1


def test_fake_stitch_contract_keeps_reconstruction_descriptor_out_of_metrics() -> None:
    result = SampleCollector(required_metadata=("record_id", "window_start"))(
        (_entry(1, 2), _entry(2, 1))
    )
    plan = SampleCollectionViewPlan(
        "fake-bvp-stitch",
        group_keys=("record_id",),
        sort_keys=("window_start",),
        stitch_policy="fake",
    )

    def stitcher(group, _plan):
        return Sample(
            {
                "outputs/signal.bvp": FieldValue(
                    tuple(entry.value.get("inputs/signal.bvp")[0] for entry in group)
                )
            }
        )

    output = PlannedSampleCollectionView(plan, stitcher=stitcher)(result.collection)

    assert len(output) == 1
    assert output[0].get("outputs/signal.bvp") == (2, 1)
    assert output.entries[0].metadata["source_count"] == 2
