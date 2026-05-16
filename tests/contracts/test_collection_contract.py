from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Generic, TypeVar

from rphys.collections import (
    CollectionItem,
    CollectionViewPlan,
    CollectorResult,
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
        entries = tuple(
            CollectionItem(value, metadata={"position": index})
            for index, value in enumerate(values)
        )
        collection = FakeCollection(
            entries,
            metadata=MappingProxyType({"snapshot": True}),
            provenance=MappingProxyType({"collector": "fake"}),
        )
        return CollectorResult(collection, metadata={"policy": "fail-loud"})


class EveryOtherView:
    plan = CollectionViewPlan("every-other", metadata={"stride": 2})

    def __call__(self, collection: FakeCollection[str]) -> FakeCollection[str]:
        return FakeCollection(collection.entries[::2])


def test_fake_collector_and_view_compose_without_inheritance_or_operation_wrapper() -> None:
    collector = FakeCollector()
    view = EveryOtherView()

    result = collector(["a", "b", "c", "d"])
    viewed = view(result.collection)

    assert isinstance(result, CollectorResult)
    assert list(result.collection) == ["a", "b", "c", "d"]
    assert list(viewed) == ["a", "c"]
    assert viewed.entries[1].metadata == {"position": 2}
    assert view.plan.metadata == {"stride": 2}
    assert not hasattr(result, "output")


def test_explicit_skip_diagnostics_preserve_reasons_without_silent_filtering() -> None:
    collection = FakeCollection((CollectionItem("valid", metadata={"position": 0}),))
    skipped = (
        CollectionItem(
            "invalid",
            metadata={"position": 1, "reason": "missing required metadata"},
        ),
    )

    result = CollectorResult(
        collection,
        skipped=skipped,
        skip_policy="fixture-skip-missing-metadata",
    )

    assert result.accepted_count == 1
    assert result.skip_policy == "fixture-skip-missing-metadata"
    assert result.skipped[0].metadata["reason"] == "missing required metadata"
