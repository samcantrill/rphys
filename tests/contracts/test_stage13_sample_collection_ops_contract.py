from __future__ import annotations

from rphys.collections import CollectionItem
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    SampleCollection,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionViewPlan,
)
from rphys.ops import (
    OperationContext,
    OperationPipeline,
    SampleCollectionConcatOperation,
    SampleCollectionGroupOperation,
    SampleCollectionViewOperation,
)
from rphys.data.collections import PlannedSampleCollectionView


def _entry(value: int, window_start: int) -> CollectionItem[Sample]:
    return CollectionItem(
        Sample({"inputs/signal.bvp": FieldValue([value])}),
        metadata={"record_id": "r1", "window_start": window_start},
    )


def test_sample_collection_operations_compose_through_operation_pipeline() -> None:
    group = SampleCollectionGroupOperation(SampleCollectionGroupPlan("group-records", group_keys=("record_id",)))
    view = SampleCollectionViewOperation(
        PlannedSampleCollectionView(
            SampleCollectionViewPlan("sort-windows", sort_keys=("window_start",))
        )
    )
    concat = SampleCollectionConcatOperation(
        SampleCollectionConcatPlan(
            "stitch-bvp",
            field_map={"inputs/signal.bvp": "outputs/signal.bvp"},
        ),
        payload_joiner=lambda payloads: tuple(payload[0] for payload in payloads),
    )

    grouped = group((_entry(2, 2), _entry(1, 1)), OperationContext())
    result = OperationPipeline((view, concat))(grouped.output[0])

    assert isinstance(grouped.output[0], SampleCollection)
    assert result.output.get("outputs/signal.bvp") == (1, 2)
    assert result.metadata["output_fields"] == ("outputs/signal.bvp",)
