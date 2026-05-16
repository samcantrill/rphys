"""Dependency-light collection, view, and collector contracts.

Collections are immutable snapshots that iterate over member values while
exposing explicit ``entries`` for item metadata and provenance. Views transform
collections into collections. Collectors materialize iterables into collection
snapshots and return ``CollectorResult`` only for materialization diagnostics;
operation wrappers can still place a collection on ``OperationResult.output``.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Generic, Protocol, TypeVar, runtime_checkable

from rphys.errors import (
    InvalidCollectionContextError,
    InvalidCollectionItemError,
    InvalidCollectionViewPlanError,
    InvalidCollectorResultError,
)

__all__ = [
    "Collection",
    "CollectionContext",
    "CollectionItem",
    "CollectionView",
    "CollectionViewPlan",
    "Collector",
    "CollectorResult",
]

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
C_co = TypeVar("C_co", covariant=True)
C_in = TypeVar("C_in")
C_out = TypeVar("C_out", covariant=True)


@dataclass(frozen=True, init=False, slots=True)
class CollectionItem(Generic[T]):
    """One collection member plus item-level metadata and provenance.

    The wrapped value is the value yielded by collection iteration. Metadata and
    provenance are shallow immutable mappings with string keys so grouping,
    ordering, split labels, source references, and rejection diagnostics remain
    inspectable without forcing a domain-specific row type.
    """

    value: T
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        value: T,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="CollectionItem",
                field="metadata",
                error_type=InvalidCollectionItemError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="CollectionItem",
                field="provenance",
                error_type=InvalidCollectionItemError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class CollectionContext:
    """Collection-level metadata and provenance for a materialized snapshot."""

    name: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="CollectionContext",
                field="name",
                error_type=InvalidCollectionContextError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="CollectionContext",
                field="metadata",
                error_type=InvalidCollectionContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="CollectionContext",
                field="provenance",
                error_type=InvalidCollectionContextError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class CollectionViewPlan:
    """Inspectable descriptor for collection-to-collection view behavior."""

    name: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="CollectionViewPlan",
                field="name",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="CollectionViewPlan",
                field="metadata",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="CollectionViewPlan",
                field="provenance",
                error_type=InvalidCollectionViewPlanError,
            ),
        )


@runtime_checkable
class Collection(Protocol[T_co]):
    """Structural sequence-like collection snapshot.

    Iteration yields member values. ``entries`` exposes ``CollectionItem``
    records when item-level metadata or provenance is needed for scientific
    grouping, ordering, diagnostics, or later report adapters.
    """

    @property
    def metadata(self) -> Mapping[str, object]:
        ...

    @property
    def provenance(self) -> Mapping[str, object]:
        ...

    @property
    def entries(self) -> Sequence[CollectionItem[T_co]]:
        ...

    def __iter__(self) -> Iterator[T_co]:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, index: int) -> T_co:
        ...


@runtime_checkable
class CollectionView(Protocol[C_in, C_out]):
    """Structural behavior that transforms one collection into another."""

    @property
    def plan(self) -> CollectionViewPlan:
        ...

    def __call__(self, collection: C_in) -> C_out:
        ...


@runtime_checkable
class Collector(Protocol[T, C_co]):
    """Structural behavior that materializes iterable values into a snapshot."""

    def __call__(self, values: Iterable[T]) -> "CollectorResult[C_co]":
        ...


@dataclass(frozen=True, init=False, slots=True)
class CollectorResult(Generic[C_co]):
    """Materialization diagnostics returned by collectors.

    ``CollectorResult`` is not an operation result and is not the normal output
    of collection views. It records accepted counts plus explicit skip/reject
    diagnostics when a caller configures those policies. Default collectors
    should fail loudly before constructing a result for invalid items.
    """

    collection: C_co
    accepted_count: int
    skipped: tuple[CollectionItem[object], ...]
    rejected: tuple[CollectionItem[object], ...]
    skip_policy: str | None
    reject_policy: str | None
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        collection: C_co,
        *,
        accepted_count: int | None = None,
        skipped: Iterable[CollectionItem[object]] = (),
        rejected: Iterable[CollectionItem[object]] = (),
        skip_policy: str | None = None,
        reject_policy: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        collection_size = _validate_collection_shape(collection)
        resolved_accepted = collection_size if accepted_count is None else accepted_count
        _validate_count(
            resolved_accepted,
            collection_size=collection_size,
            error_type=InvalidCollectorResultError,
        )
        skipped_items = _coerce_issue_items(
            skipped,
            owner="CollectorResult",
            field="skipped",
        )
        rejected_items = _coerce_issue_items(
            rejected,
            owner="CollectorResult",
            field="rejected",
        )
        resolved_skip_policy = _coerce_optional_non_empty_string(
            skip_policy,
            owner="CollectorResult",
            field="skip_policy",
            error_type=InvalidCollectorResultError,
        )
        resolved_reject_policy = _coerce_optional_non_empty_string(
            reject_policy,
            owner="CollectorResult",
            field="reject_policy",
            error_type=InvalidCollectorResultError,
        )
        if skipped_items and resolved_skip_policy is None:
            raise InvalidCollectorResultError(
                "CollectorResult skipped items require an explicit skip_policy.",
                owner="CollectorResult",
                field="skipped",
            )
        if rejected_items and resolved_reject_policy is None:
            raise InvalidCollectorResultError(
                "CollectorResult rejected items require an explicit reject_policy.",
                owner="CollectorResult",
                field="rejected",
            )

        object.__setattr__(self, "collection", collection)
        object.__setattr__(self, "accepted_count", resolved_accepted)
        object.__setattr__(self, "skipped", skipped_items)
        object.__setattr__(self, "rejected", rejected_items)
        object.__setattr__(self, "skip_policy", resolved_skip_policy)
        object.__setattr__(self, "reject_policy", resolved_reject_policy)
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="CollectorResult",
                field="metadata",
                error_type=InvalidCollectorResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="CollectorResult",
                field="provenance",
                error_type=InvalidCollectorResultError,
            ),
        )


def _coerce_non_empty_string(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[Exception],
) -> str:
    if isinstance(value, str) and value:
        return value
    raise error_type(
        f"{owner} {field} must be a non-empty string.",
        owner=owner,
        field=field,
        expected="non-empty string",
        actual=repr(value),
    )


def _coerce_optional_non_empty_string(
    value: object | None,
    *,
    owner: str,
    field: str,
    error_type: type[Exception],
) -> str | None:
    if value is None:
        return None
    return _coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        error_type=error_type,
    )


def _coerce_string_mapping(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
    error_type: type[Exception],
) -> Mapping[str, object]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise error_type(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping with string keys",
            actual=type(value).__name__,
        )
    coerced: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise error_type(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                key=repr(key),
                expected="non-empty string",
                actual=type(key).__name__,
            )
        coerced[key] = item
    return MappingProxyType(coerced)


def _validate_collection_shape(collection: object) -> int:
    missing: list[str] = []
    for attr_name in ("metadata", "provenance", "entries"):
        if not hasattr(collection, attr_name):
            missing.append(attr_name)
    for method_name in ("__iter__", "__len__", "__getitem__"):
        if not callable(getattr(collection, method_name, None)):
            missing.append(method_name)
    if missing:
        raise InvalidCollectorResultError(
            "CollectorResult collection must satisfy the Collection protocol.",
            owner="CollectorResult",
            field="collection",
            missing=tuple(missing),
            actual=type(collection).__name__,
        )
    collection_size = len(collection)  # type: ignore[arg-type]
    if collection_size < 0:
        raise InvalidCollectorResultError(
            "Collection length must not be negative.",
            owner="CollectorResult",
            field="collection",
            actual=collection_size,
        )
    entries = getattr(collection, "entries")
    if len(entries) != collection_size:
        raise InvalidCollectorResultError(
            "Collection entries must align with collection length.",
            owner="CollectorResult",
            field="entries",
            expected=collection_size,
            actual=len(entries),
        )
    for index, entry in enumerate(entries):
        if not isinstance(entry, CollectionItem):
            raise InvalidCollectorResultError(
                "Collection entries must be CollectionItem records.",
                owner="CollectorResult",
                field="entries",
                index=index,
                actual=type(entry).__name__,
            )
    return collection_size


def _validate_count(
    value: object,
    *,
    collection_size: int,
    error_type: type[Exception],
) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise error_type(
            "CollectorResult accepted_count must be a non-negative integer.",
            owner="CollectorResult",
            field="accepted_count",
            expected="non-negative integer",
            actual=repr(value),
        )
    if value != collection_size:
        raise error_type(
            "CollectorResult accepted_count must match collection length.",
            owner="CollectorResult",
            field="accepted_count",
            expected=collection_size,
            actual=value,
        )


def _coerce_issue_items(
    value: Iterable[CollectionItem[object]],
    *,
    owner: str,
    field: str,
) -> tuple[CollectionItem[object], ...]:
    try:
        items = tuple(value)
    except TypeError as exc:
        raise InvalidCollectorResultError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of CollectionItem",
            actual=type(value).__name__,
        ) from exc
    for index, item in enumerate(items):
        if not isinstance(item, CollectionItem):
            raise InvalidCollectorResultError(
                f"{owner} {field} entries must be CollectionItem records.",
                owner=owner,
                field=field,
                index=index,
                actual=type(item).__name__,
            )
    return items


CollectionItem.__hash__ = None  # type: ignore[assignment]
CollectionContext.__hash__ = None  # type: ignore[assignment]
CollectionViewPlan.__hash__ = None  # type: ignore[assignment]
CollectorResult.__hash__ = None  # type: ignore[assignment]
