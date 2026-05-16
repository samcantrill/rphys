from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Generic, TypeVar

import pytest

from rphys.collections import (
    Collection,
    CollectionContext,
    CollectionItem,
    CollectionView,
    CollectionViewPlan,
    Collector,
    CollectorResult,
)
from rphys.errors import (
    InvalidCollectionContextError,
    InvalidCollectionItemError,
    InvalidCollectionViewPlanError,
    InvalidCollectorResultError,
)

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class FakeCollection(Generic[T]):
    _entries: tuple[CollectionItem[T], ...]
    metadata: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))
    provenance: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))

    @property
    def entries(self) -> Sequence[CollectionItem[T]]:
        return self._entries

    def __iter__(self) -> Iterator[T]:
        for entry in self._entries:
            yield entry.value

    def __len__(self) -> int:
        return len(self._entries)

    def __getitem__(self, index: int) -> T:
        return self._entries[index].value


class FakeCollector:
    def __call__(self, values):
        collection = FakeCollection(
            tuple(
                CollectionItem(value, metadata={"index": index})
                for index, value in enumerate(values)
            ),
            metadata=MappingProxyType({"source": "fake"}),
            provenance=MappingProxyType({"collector": "fake"}),
        )
        return CollectorResult(collection, metadata={"policy": "fail-loud"})


class FakeView:
    plan = CollectionViewPlan("reverse", metadata={"order": "reverse"})

    def __call__(self, collection: FakeCollection[str]) -> FakeCollection[str]:
        return FakeCollection(tuple(reversed(collection.entries)))


def test_collection_item_preserves_value_with_immutable_metadata() -> None:
    metadata = {"subject_id": "s1"}
    item = CollectionItem("sample-a", metadata=metadata, provenance={"source": "fixture"})
    metadata["subject_id"] = "mutated"

    assert item.value == "sample-a"
    assert item.metadata == {"subject_id": "s1"}
    assert item.provenance == {"source": "fixture"}
    with pytest.raises(TypeError):
        item.metadata["subject_id"] = "s2"  # type: ignore[index]


def test_collection_item_rejects_non_string_metadata_keys() -> None:
    with pytest.raises(InvalidCollectionItemError) as exc_info:
        CollectionItem("sample-a", metadata={1: "bad"})

    assert exc_info.value.context["owner"] == "CollectionItem"
    assert exc_info.value.context["field"] == "metadata"


def test_context_and_view_plan_validate_names_and_mapping_keys() -> None:
    context = CollectionContext(
        "windows",
        metadata={"level": "record"},
        provenance={"source": "collector"},
    )
    plan = CollectionViewPlan(
        "group-by-record",
        metadata={"group_keys": ("record_id",)},
        provenance={"author": "test"},
    )

    assert context.name == "windows"
    assert context.metadata == {"level": "record"}
    assert plan.name == "group-by-record"
    assert plan.metadata == {"group_keys": ("record_id",)}

    with pytest.raises(InvalidCollectionContextError):
        CollectionContext("")
    with pytest.raises(InvalidCollectionViewPlanError):
        CollectionViewPlan("view", provenance={"": "bad"})


def test_fake_collection_is_value_iterable_with_entry_metadata_access() -> None:
    entries = (
        CollectionItem("sample-a", metadata={"record_id": "r1", "window_start": 0}),
        CollectionItem("sample-b", metadata={"record_id": "r1", "window_start": 1}),
    )
    collection = FakeCollection(
        entries,
        metadata=MappingProxyType({"ordered": True}),
        provenance=MappingProxyType({"source": "unit"}),
    )

    assert isinstance(collection, Collection)
    assert list(collection) == ["sample-a", "sample-b"]
    assert collection[1] == "sample-b"
    assert collection.entries[0].metadata["record_id"] == "r1"
    assert collection.metadata == {"ordered": True}


def test_collector_result_records_materialization_diagnostics() -> None:
    collection = FakeCollection((CollectionItem("a"), CollectionItem("b")))

    result = CollectorResult(
        collection,
        metadata={"materialized": True},
        provenance={"collector": "fake"},
    )

    assert result.collection is collection
    assert result.accepted_count == 2
    assert result.skipped == ()
    assert result.rejected == ()
    assert result.metadata == {"materialized": True}


def test_collector_result_requires_collection_shape_and_matching_count() -> None:
    collection = FakeCollection((CollectionItem("a"),))

    with pytest.raises(InvalidCollectorResultError):
        CollectorResult(object())
    with pytest.raises(InvalidCollectorResultError):
        CollectorResult(collection, accepted_count=2)


def test_collector_result_requires_explicit_skip_and_reject_policies() -> None:
    collection = FakeCollection((CollectionItem("a"),))
    skipped = (CollectionItem("b", metadata={"reason": "missing id"}),)
    rejected = (CollectionItem("c", metadata={"reason": "bad payload"}),)

    with pytest.raises(InvalidCollectorResultError):
        CollectorResult(collection, skipped=skipped)
    with pytest.raises(InvalidCollectorResultError):
        CollectorResult(collection, rejected=rejected)

    result = CollectorResult(
        collection,
        skipped=skipped,
        rejected=rejected,
        skip_policy="drop-missing-id",
        reject_policy="record-invalid-payload",
    )

    assert result.skip_policy == "drop-missing-id"
    assert result.reject_policy == "record-invalid-payload"
    assert result.skipped[0].metadata["reason"] == "missing id"
    assert result.rejected[0].metadata["reason"] == "bad payload"


def test_fake_collector_and_view_satisfy_structural_protocols() -> None:
    collector = FakeCollector()
    view = FakeView()

    assert isinstance(collector, Collector)
    assert isinstance(view, CollectionView)

    result = collector(["a", "b", "c"])
    viewed = view(result.collection)

    assert isinstance(result, CollectorResult)
    assert list(result.collection) == ["a", "b", "c"]
    assert list(viewed) == ["c", "b", "a"]
    assert viewed.entries[0].metadata["index"] == 2
