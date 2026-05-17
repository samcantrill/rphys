from __future__ import annotations

import pytest

from rphys.collections import CollectionItem, CollectorResult
from rphys.data import FieldValue, Sample
from rphys.data.collections import (
    PlannedSampleCollectionView,
    SampleCollection,
    SampleCollectionConcatPlan,
    SampleCollectionGroupPlan,
    SampleCollectionSortPlan,
    SampleCollectionView,
    SampleCollectionViewPlan,
    SampleCollector,
    concat_sample_collection_fields,
    filter_sample_collection,
    group_sample_collections,
    project_sample_collection,
    sort_sample_collection,
)
from rphys.errors import (
    InvalidCollectionContextError,
    InvalidCollectionViewPlanError,
)


def _sample(value: int) -> Sample:
    return Sample({"inputs/signal.bvp": FieldValue([value])})


def _entry(
    value: int,
    *,
    subject_id: str = "s1",
    record_id: str = "r1",
    window_start: int = 0,
) -> CollectionItem[Sample]:
    return CollectionItem(
        _sample(value),
        metadata={
            "subject_id": subject_id,
            "record_id": record_id,
            "sample_id": f"{record_id}-{window_start}",
            "window_start": window_start,
            "window_stop": window_start + 1,
            "split": "train",
        },
        provenance={"source": "unit"},
    )


def test_sample_collection_iterates_samples_and_preserves_entries() -> None:
    entries = (_entry(1, window_start=1), _entry(2, window_start=2))
    collection = SampleCollection(
        entries,
        metadata={"level": "window"},
        provenance={"collector": "fixture"},
    )

    assert list(collection) == [entries[0].value, entries[1].value]
    assert collection[0] is entries[0].value
    assert collection.entries[1].metadata["window_start"] == 2
    assert collection.metadata == {"level": "window"}
    with pytest.raises(TypeError):
        collection.metadata["level"] = "mutated"  # type: ignore[index]


def test_sample_collection_rejects_non_sample_entries() -> None:
    with pytest.raises(InvalidCollectionContextError):
        SampleCollection((object(),))  # type: ignore[arg-type]
    with pytest.raises(InvalidCollectionContextError):
        SampleCollection((CollectionItem(object()),))  # type: ignore[arg-type]


def test_sample_collector_materializes_existing_collection_and_iterables() -> None:
    entries = (_entry(1), _entry(2, window_start=1))
    collection = SampleCollection(entries)
    collector = SampleCollector(required_metadata=("record_id",), metadata={"policy": "fail"})

    existing_result = collector(collection)
    collected_result = collector(entries)

    assert isinstance(existing_result, CollectorResult)
    assert existing_result.collection is collection
    assert list(collected_result.collection) == [entry.value for entry in entries]
    assert collected_result.accepted_count == 2
    assert collected_result.metadata == {"policy": "fail"}


def test_sample_collector_fails_loud_by_default_and_records_explicit_skips() -> None:
    valid = _entry(1)
    invalid = CollectionItem(_sample(2), metadata={"record_id": "r1"})

    collector = SampleCollector(required_metadata=("subject_id", "record_id"))
    with pytest.raises(InvalidCollectionContextError):
        collector((valid, invalid))

    skipping = SampleCollector(
        required_metadata=("subject_id", "record_id"),
        skip_policy="skip-missing-metadata",
    )
    result = skipping((valid, invalid))

    assert list(result.collection) == [valid.value]
    assert result.skipped[0].metadata["index"] == 1
    assert result.skipped[0].metadata["missing"] == ("subject_id",)
    assert result.skip_policy == "skip-missing-metadata"


def test_sample_collection_view_plan_validates_policies_and_descriptors() -> None:
    plan = SampleCollectionViewPlan(
        "sort-windows",
        group_keys=("subject_id", "record_id"),
        sort_keys=("window_start",),
        selected_fields=("inputs/signal.bvp",),
        stitch_policy="identity",
        missing_window_policy="error",
        overlap_policy="keep",
        metadata={"purpose": "pre-metric"},
    )

    assert plan.group_keys == ("subject_id", "record_id")
    assert str(plan.selected_fields[0]) == "inputs/signal.bvp"
    assert plan.metadata == {"purpose": "pre-metric"}

    with pytest.raises(InvalidCollectionViewPlanError):
        SampleCollectionViewPlan("bad", group_keys=("record_id", "record_id"))
    with pytest.raises(InvalidCollectionViewPlanError):
        SampleCollectionViewPlan("bad", stitch_policy="real_filtering")


def test_planned_sample_collection_view_sorts_selects_fields_and_preserves_source() -> None:
    entries = (_entry(2, window_start=2), _entry(1, window_start=1))
    collection = SampleCollection(entries, metadata={"level": "window"})
    plan = SampleCollectionViewPlan(
        "ordered-selected",
        group_keys=("record_id",),
        sort_keys=("window_start",),
        selected_fields=("inputs/signal.bvp",),
    )
    view = PlannedSampleCollectionView(plan)

    assert isinstance(view, SampleCollectionView)
    output = view(collection)

    assert len(output) == 2
    assert output.entries[0].metadata["window_start"] == 1
    assert output.entries[0].metadata["view"] == "ordered-selected"
    assert output[0] is not entries[1].value
    assert output[0].field("inputs/signal.bvp") is entries[1].value.field("inputs/signal.bvp")
    assert entries[1].value.field_items() == output[0].field_items()


def test_planned_sample_collection_view_fails_on_missing_sort_metadata() -> None:
    collection = SampleCollection((CollectionItem(_sample(1), metadata={"record_id": "r1"}),))
    view = PlannedSampleCollectionView(
        SampleCollectionViewPlan(
            "missing-sort",
            group_keys=("record_id",),
            sort_keys=("window_start",),
        )
    )

    with pytest.raises(InvalidCollectionContextError):
        view(collection)


def test_planned_sample_collection_view_uses_injected_fake_stitch_behavior() -> None:
    entries = (_entry(1, window_start=2), _entry(2, window_start=1))
    collection = SampleCollection(entries)
    plan = SampleCollectionViewPlan(
        "fake-stitch",
        group_keys=("subject_id", "record_id"),
        sort_keys=("window_start",),
        stitch_policy="fake",
    )

    def stitcher(group, view_plan):
        assert view_plan is plan
        payload = [sample.get("inputs/signal.bvp")[0] for sample in (entry.value for entry in group)]
        return Sample({"outputs/signal.bvp": FieldValue(tuple(payload))})

    view = PlannedSampleCollectionView(plan, stitcher=stitcher)
    output = view(collection)

    assert len(output) == 1
    assert output[0].get("outputs/signal.bvp") == (2, 1)
    assert output.entries[0].metadata["source_count"] == 2
    assert output.entries[0].metadata["stitch_policy"] == "fake"
    assert output.entries[0].metadata["record_id"] == "r1"


def test_group_sample_collections_materializes_grouped_runtime_collections() -> None:
    entries = (
        CollectionItem(
            Sample({"metadata/metadata.split_label": FieldValue("train")}),
            metadata={"subject_id": "s1", "record_id": "r1"},
        ),
        CollectionItem(
            Sample({"metadata/metadata.split_label": FieldValue("valid")}),
            metadata={"subject_id": "s1", "record_id": "r1"},
        ),
        CollectionItem(
            Sample({"metadata/metadata.split_label": FieldValue("train")}),
            metadata={"subject_id": "s2", "record_id": "r2"},
        ),
    )
    plan = SampleCollectionGroupPlan(
        "record-groups",
        group_keys=("subject_id", "record_id"),
        field_group_keys={"split_from_field": "metadata/metadata.split_label"},
    )

    grouped = group_sample_collections(entries, plan)

    assert len(grouped) == 3
    assert grouped[0].metadata["subject_id"] == "s1"
    assert grouped[0].metadata["record_id"] == "r1"
    assert grouped[0].metadata["split_from_field"] == "train"
    assert grouped[0].metadata["source_count"] == 1


def test_group_sample_collections_missing_policy_is_explicit() -> None:
    entry = CollectionItem(_sample(1), metadata={"record_id": "r1"})
    default_plan = SampleCollectionGroupPlan("subject-groups", group_keys=("subject_id",))
    with pytest.raises(InvalidCollectionContextError):
        group_sample_collections((entry,), default_plan)

    allowing_plan = SampleCollectionGroupPlan(
        "subject-groups",
        group_keys=("subject_id",),
        missing_policy="allow",
    )
    grouped = group_sample_collections((entry,), allowing_plan)

    assert grouped[0].metadata["subject_id"] is None


def test_sort_project_filter_and_concat_collection_operations() -> None:
    entries = (_entry(2, window_start=2), _entry(1, window_start=1), _entry(3, window_start=3))
    collection = SampleCollection(entries)

    sorted_collection = sort_sample_collection(
        collection,
        SampleCollectionSortPlan("sort-by-window", sort_keys=("window_start",)),
    )
    projected = project_sample_collection(sorted_collection, ("inputs/signal.bvp",), name="project-bvp")
    filtered = filter_sample_collection(
        projected,
        lambda entry: entry.metadata["window_start"] != 2,
        name="drop-middle",
        skip_policy="diagnose-skips",
    )
    stitched = concat_sample_collection_fields(
        filtered.collection,
        SampleCollectionConcatPlan(
            "tuple-stitch",
            field_map={"inputs/signal.bvp": "outputs/signal.bvp"},
        ),
        payload_joiner=lambda payloads: tuple(payload[0] for payload in payloads),
    )

    assert [sample.get("inputs/signal.bvp")[0] for sample in sorted_collection] == [1, 2, 3]
    assert filtered.accepted_count == 2
    assert filtered.skipped[0].metadata["filter_operation"] == "drop-middle"
    assert stitched.get("outputs/signal.bvp") == (1, 3)
    assert stitched.field("outputs/signal.bvp").metadata["collection.source_count"] == 2
