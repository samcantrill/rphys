"""Sample collection snapshots and descriptor-driven pre-metric views."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from rphys.collections import CollectionItem, CollectorResult
from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidCollectionContextError,
    InvalidCollectionViewPlanError,
    InvalidCollectorResultError,
)

__all__ = [
    "SampleCollection",
    "SampleCollectionView",
    "SampleCollectionViewPlan",
    "SampleCollectionConcatPlan",
    "SampleCollectionGroupPlan",
    "SampleCollectionSortPlan",
    "SampleCollector",
    "PlannedSampleCollectionView",
    "concat_sample_collection_fields",
    "filter_sample_collection",
    "group_sample_collections",
    "project_sample_collection",
    "sort_sample_collection",
]

_MISSING_WINDOW_POLICIES = frozenset({"error", "allow"})
_OVERLAP_POLICIES = frozenset({"error", "allow", "keep"})
_STITCH_POLICIES = frozenset({None, "identity", "fake"})


@dataclass(frozen=True, init=False, slots=True)
class SampleCollection:
    """Immutable-membership collection of ``Sample`` values.

    Iteration yields ``Sample`` values for metric call sites. ``entries`` keeps
    per-sample metadata and provenance such as subject, record, sample, split,
    and window ordering for grouping, sorting, diagnostics, and future
    evaluation adapters.
    """

    _entries: tuple[CollectionItem[Sample], ...]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        entries: Iterable[Sample | CollectionItem[Sample]],
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(self, "_entries", _coerce_entries(entries))
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="SampleCollection",
                field="metadata",
                error_type=InvalidCollectionContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="SampleCollection",
                field="provenance",
                error_type=InvalidCollectionContextError,
            ),
        )

    @property
    def entries(self) -> Sequence[CollectionItem[Sample]]:
        return self._entries

    def __iter__(self) -> Iterator[Sample]:
        for entry in self._entries:
            yield entry.value

    def __len__(self) -> int:
        return len(self._entries)

    def __getitem__(self, index: int) -> Sample:
        return self._entries[index].value


@dataclass(frozen=True, init=False, slots=True)
class SampleCollectionViewPlan:
    """Descriptor for grouping, sorting, field selection, and fake stitching."""

    name: str
    group_keys: tuple[str, ...]
    sort_keys: tuple[str, ...]
    selected_fields: tuple[FieldLocator, ...]
    stitch_policy: str | None
    missing_window_policy: str
    overlap_policy: str
    require_provenance: bool
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        group_keys: Iterable[str] = (),
        sort_keys: Iterable[str] = (),
        selected_fields: Iterable[FieldLocator | str] = (),
        stitch_policy: str | None = None,
        missing_window_policy: str = "error",
        overlap_policy: str = "error",
        require_provenance: bool = False,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="SampleCollectionViewPlan",
                field="name",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "group_keys",
            _coerce_key_tuple(group_keys, owner="SampleCollectionViewPlan", field="group_keys"),
        )
        object.__setattr__(
            self,
            "sort_keys",
            _coerce_key_tuple(sort_keys, owner="SampleCollectionViewPlan", field="sort_keys"),
        )
        object.__setattr__(
            self,
            "selected_fields",
            _coerce_locator_tuple(selected_fields, owner="SampleCollectionViewPlan"),
        )
        object.__setattr__(
            self,
            "stitch_policy",
            _coerce_policy(
                stitch_policy,
                allowed=_STITCH_POLICIES,
                owner="SampleCollectionViewPlan",
                field="stitch_policy",
            ),
        )
        object.__setattr__(
            self,
            "missing_window_policy",
            _coerce_policy(
                missing_window_policy,
                allowed=_MISSING_WINDOW_POLICIES,
                owner="SampleCollectionViewPlan",
                field="missing_window_policy",
            ),
        )
        object.__setattr__(
            self,
            "overlap_policy",
            _coerce_policy(
                overlap_policy,
                allowed=_OVERLAP_POLICIES,
                owner="SampleCollectionViewPlan",
                field="overlap_policy",
            ),
        )
        if not isinstance(require_provenance, bool):
            raise InvalidCollectionViewPlanError(
                "SampleCollectionViewPlan require_provenance must be a boolean.",
                owner="SampleCollectionViewPlan",
                field="require_provenance",
                expected="bool",
                actual=type(require_provenance).__name__,
            )
        object.__setattr__(self, "require_provenance", require_provenance)
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="SampleCollectionViewPlan",
                field="metadata",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="SampleCollectionViewPlan",
                field="provenance",
                error_type=InvalidCollectionViewPlanError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class SampleCollectionGroupPlan:
    """Runtime grouping descriptor for ``Sample`` streams.

    ``group_keys`` read item metadata from ``CollectionItem`` wrappers, while
    ``field_group_keys`` reads payload values from member samples under explicit
    group names. Missing metadata or fields fail unless ``missing_policy`` is
    ``"allow"``. The grouping operation materializes tuple outputs so runtime
    ordering and diagnostics are inspectable.
    """

    name: str
    group_keys: tuple[str, ...]
    field_group_keys: Mapping[str, FieldLocator]
    missing_policy: str
    empty_policy: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        group_keys: Iterable[str] = (),
        field_group_keys: Mapping[object, FieldLocator | str] | None = None,
        missing_policy: str = "error",
        empty_policy: str = "error",
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="SampleCollectionGroupPlan",
                field="name",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "group_keys",
            _coerce_key_tuple(group_keys, owner="SampleCollectionGroupPlan", field="group_keys"),
        )
        object.__setattr__(
            self,
            "field_group_keys",
            _coerce_locator_mapping(
                field_group_keys,
                owner="SampleCollectionGroupPlan",
                field="field_group_keys",
            ),
        )
        object.__setattr__(
            self,
            "missing_policy",
            _coerce_policy(
                missing_policy,
                allowed=_MISSING_WINDOW_POLICIES,
                owner="SampleCollectionGroupPlan",
                field="missing_policy",
            ),
        )
        object.__setattr__(
            self,
            "empty_policy",
            _coerce_policy(
                empty_policy,
                allowed=_MISSING_WINDOW_POLICIES,
                owner="SampleCollectionGroupPlan",
                field="empty_policy",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="SampleCollectionGroupPlan",
                field="metadata",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="SampleCollectionGroupPlan",
                field="provenance",
                error_type=InvalidCollectionViewPlanError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class SampleCollectionSortPlan:
    """Sort descriptor for collection metadata and sample field payload keys."""

    name: str
    sort_keys: tuple[str, ...]
    field_sort_keys: tuple[FieldLocator, ...]
    missing_policy: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        sort_keys: Iterable[str] = (),
        field_sort_keys: Iterable[FieldLocator | str] = (),
        missing_policy: str = "error",
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="SampleCollectionSortPlan",
                field="name",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "sort_keys",
            _coerce_key_tuple(sort_keys, owner="SampleCollectionSortPlan", field="sort_keys"),
        )
        object.__setattr__(
            self,
            "field_sort_keys",
            _coerce_locator_tuple(field_sort_keys, owner="SampleCollectionSortPlan"),
        )
        object.__setattr__(
            self,
            "missing_policy",
            _coerce_policy(
                missing_policy,
                allowed=_MISSING_WINDOW_POLICIES,
                owner="SampleCollectionSortPlan",
                field="missing_policy",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="SampleCollectionSortPlan",
                field="metadata",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="SampleCollectionSortPlan",
                field="provenance",
                error_type=InvalidCollectionViewPlanError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class SampleCollectionConcatPlan:
    """Descriptor for field-wise concatenation or stitching of a collection.

    ``field_map`` maps source sample fields to output sample fields. The
    operation gathers member payloads in collection order and calls the injected
    ``payload_joiner`` supplied to ``concat_sample_collection_fields``; the
    default joiner returns a tuple and makes no sampling-rate or axis claim.
    """

    name: str
    field_map: Mapping[FieldLocator, FieldLocator]
    empty_policy: str
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        *,
        field_map: Mapping[FieldLocator | str, FieldLocator | str],
        empty_policy: str = "error",
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            _coerce_non_empty_string(
                name,
                owner="SampleCollectionConcatPlan",
                field="name",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "field_map",
            _coerce_field_map(field_map, owner="SampleCollectionConcatPlan"),
        )
        object.__setattr__(
            self,
            "empty_policy",
            _coerce_policy(
                empty_policy,
                allowed=_MISSING_WINDOW_POLICIES,
                owner="SampleCollectionConcatPlan",
                field="empty_policy",
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _coerce_string_mapping(
                metadata,
                owner="SampleCollectionConcatPlan",
                field="metadata",
                error_type=InvalidCollectionViewPlanError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _coerce_string_mapping(
                provenance,
                owner="SampleCollectionConcatPlan",
                field="provenance",
                error_type=InvalidCollectionViewPlanError,
            ),
        )


@runtime_checkable
class SampleCollectionView(Protocol):
    """Structural behavior that maps a sample collection to a collection."""

    @property
    def plan(self) -> SampleCollectionViewPlan:
        ...

    def __call__(self, collection: SampleCollection) -> SampleCollection:
        ...


class SampleCollector:
    """Materialize samples into a ``SampleCollection`` snapshot."""

    def __init__(
        self,
        *,
        required_metadata: Iterable[str] = (),
        skip_policy: str | None = None,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        self.required_metadata = _coerce_key_tuple(
            required_metadata,
            owner="SampleCollector",
            field="required_metadata",
        )
        self.skip_policy = _coerce_optional_non_empty_string(
            skip_policy,
            owner="SampleCollector",
            field="skip_policy",
            error_type=InvalidCollectorResultError,
        )
        self.metadata = _coerce_string_mapping(
            metadata,
            owner="SampleCollector",
            field="metadata",
            error_type=InvalidCollectorResultError,
        )
        self.provenance = _coerce_string_mapping(
            provenance,
            owner="SampleCollector",
            field="provenance",
            error_type=InvalidCollectorResultError,
        )

    def __call__(
        self,
        values: Iterable[Sample | CollectionItem[Sample] | SampleCollection],
    ) -> CollectorResult[SampleCollection]:
        if isinstance(values, SampleCollection):
            return CollectorResult(
                values,
                metadata=self.metadata,
                provenance=self.provenance,
            )

        accepted: list[CollectionItem[Sample]] = []
        skipped: list[CollectionItem[object]] = []
        for index, value in enumerate(values):
            try:
                entry = _coerce_entry(value)
                _validate_required_metadata(entry, self.required_metadata)
            except InvalidCollectionContextError as exc:
                if self.skip_policy is None:
                    raise
                skipped.append(
                    CollectionItem(
                        value,
                        metadata={
                            "index": index,
                            "reason": exc.message,
                            "missing": exc.context.get("missing"),
                        },
                    )
                )
                continue
            accepted.append(entry)

        collection = SampleCollection(
            accepted,
            metadata=self.metadata,
            provenance=self.provenance,
        )
        return CollectorResult(
            collection,
            skipped=tuple(skipped),
            skip_policy=self.skip_policy,
            metadata=self.metadata,
            provenance=self.provenance,
        )


def group_sample_collections(
    values: Iterable[Sample | CollectionItem[Sample]] | SampleCollection,
    plan: SampleCollectionGroupPlan,
) -> tuple[SampleCollection, ...]:
    """Materialize grouped ``SampleCollection`` values from a sample stream."""

    if not isinstance(plan, SampleCollectionGroupPlan):
        raise InvalidCollectionViewPlanError(
            "group_sample_collections requires a SampleCollectionGroupPlan.",
            owner="group_sample_collections",
            field="plan",
            expected="SampleCollectionGroupPlan",
            actual=type(plan).__name__,
        )
    entries = tuple(values.entries) if isinstance(values, SampleCollection) else _coerce_entries(values)
    if not entries:
        if plan.empty_policy == "error":
            raise InvalidCollectionContextError(
                "Sample grouping input must not be empty.",
                owner="group_sample_collections",
                field="values",
                empty_policy=plan.empty_policy,
            )
        return ()

    grouped: dict[tuple[object, ...], list[CollectionItem[Sample]]] = {}
    group_metadata: dict[tuple[object, ...], Mapping[str, object]] = {}
    for entry in entries:
        key_metadata = _group_entry_metadata(entry, plan)
        key = tuple(key_metadata[name] for name in (*plan.group_keys, *plan.field_group_keys.keys()))
        _validate_hashable_group_key(key, owner="group_sample_collections")
        grouped.setdefault(key, []).append(entry)
        group_metadata.setdefault(key, MappingProxyType(dict(key_metadata)))

    output: list[SampleCollection] = []
    for key, group_entries in grouped.items():
        output.append(
            SampleCollection(
                tuple(group_entries),
                metadata={
                    **plan.metadata,
                    **group_metadata[key],
                    "group": key,
                    "group_by": (*plan.group_keys, *plan.field_group_keys.keys()),
                    "group_operation": plan.name,
                    "source_count": len(group_entries),
                },
                provenance={**plan.provenance, "group_operation": plan.name},
            )
        )
    return tuple(output)


def sort_sample_collection(
    collection: SampleCollection,
    plan: SampleCollectionSortPlan,
) -> SampleCollection:
    """Return a collection sorted by item metadata and explicit sample fields."""

    if not isinstance(collection, SampleCollection):
        raise InvalidCollectionContextError(
            "sort_sample_collection requires a SampleCollection.",
            owner="sort_sample_collection",
            field="collection",
            expected="SampleCollection",
            actual=type(collection).__name__,
        )
    if not isinstance(plan, SampleCollectionSortPlan):
        raise InvalidCollectionViewPlanError(
            "sort_sample_collection requires a SampleCollectionSortPlan.",
            owner="sort_sample_collection",
            field="plan",
            expected="SampleCollectionSortPlan",
            actual=type(plan).__name__,
        )
    try:
        entries = tuple(sorted(collection.entries, key=lambda entry: _sort_entry_key(entry, plan)))
    except TypeError as exc:
        raise InvalidCollectionContextError(
            "Sample collection sort keys must be mutually orderable.",
            owner="sort_sample_collection",
            field="sort_keys",
            sort_keys=plan.sort_keys,
            field_sort_keys=tuple(str(locator) for locator in plan.field_sort_keys),
        ) from exc
    return SampleCollection(
        entries,
        metadata={
            **collection.metadata,
            **plan.metadata,
            "sort_operation": plan.name,
            "sort_keys": plan.sort_keys,
            "field_sort_keys": tuple(str(locator) for locator in plan.field_sort_keys),
        },
        provenance={**collection.provenance, **plan.provenance, "sort_operation": plan.name},
    )


def project_sample_collection(
    collection: SampleCollection,
    selected_fields: Iterable[FieldLocator | str],
    *,
    name: str = "project-fields",
) -> SampleCollection:
    """Return a collection whose samples contain only selected fields."""

    plan = SampleCollectionViewPlan(name, selected_fields=selected_fields)
    return PlannedSampleCollectionView(plan)(collection)


def filter_sample_collection(
    collection: SampleCollection,
    predicate: Callable[[CollectionItem[Sample]], bool],
    *,
    name: str = "filter-samples",
    skip_policy: str | None = None,
) -> CollectorResult[SampleCollection]:
    """Filter collection entries with explicit skip diagnostics."""

    if not isinstance(collection, SampleCollection):
        raise InvalidCollectionContextError(
            "filter_sample_collection requires a SampleCollection.",
            owner="filter_sample_collection",
            field="collection",
            expected="SampleCollection",
            actual=type(collection).__name__,
        )
    if not callable(predicate):
        raise InvalidCollectionViewPlanError(
            "filter_sample_collection predicate must be callable.",
            owner="filter_sample_collection",
            field="predicate",
            expected="callable",
            actual=type(predicate).__name__,
        )
    operation_name = _coerce_non_empty_string(
        name,
        owner="filter_sample_collection",
        field="name",
        error_type=InvalidCollectionViewPlanError,
    )
    accepted: list[CollectionItem[Sample]] = []
    skipped: list[CollectionItem[object]] = []
    for index, entry in enumerate(collection.entries):
        keep = predicate(entry)
        if not isinstance(keep, bool):
            raise InvalidCollectionContextError(
                "filter_sample_collection predicate must return bool.",
                owner="filter_sample_collection",
                field="predicate",
                expected="bool",
                actual=type(keep).__name__,
            )
        if keep:
            accepted.append(entry)
            continue
        if skip_policy is None:
            continue
        skipped.append(
            CollectionItem(
                entry.value,
                metadata={
                    **entry.metadata,
                    "index": index,
                    "filter_operation": operation_name,
                    "skip_policy": skip_policy,
                },
                provenance=entry.provenance,
            )
        )
    output = SampleCollection(
        tuple(accepted),
        metadata={**collection.metadata, "filter_operation": operation_name},
        provenance={**collection.provenance, "filter_operation": operation_name},
    )
    return CollectorResult(
        output,
        skipped=tuple(skipped),
        skip_policy=skip_policy,
        metadata=output.metadata,
        provenance=output.provenance,
    )


def concat_sample_collection_fields(
    collection: SampleCollection,
    plan: SampleCollectionConcatPlan,
    *,
    payload_joiner: Callable[[tuple[object, ...]], object] | None = None,
) -> Sample:
    """Concatenate collection member field payloads into a revised sample."""

    if not isinstance(collection, SampleCollection):
        raise InvalidCollectionContextError(
            "concat_sample_collection_fields requires a SampleCollection.",
            owner="concat_sample_collection_fields",
            field="collection",
            expected="SampleCollection",
            actual=type(collection).__name__,
        )
    if not isinstance(plan, SampleCollectionConcatPlan):
        raise InvalidCollectionViewPlanError(
            "concat_sample_collection_fields requires a SampleCollectionConcatPlan.",
            owner="concat_sample_collection_fields",
            field="plan",
            expected="SampleCollectionConcatPlan",
            actual=type(plan).__name__,
        )
    if not collection and plan.empty_policy == "error":
        raise InvalidCollectionContextError(
            "Sample collection concatenation input must not be empty.",
            owner="concat_sample_collection_fields",
            field="collection",
            empty_policy=plan.empty_policy,
        )
    joiner = tuple if payload_joiner is None else payload_joiner
    if not callable(joiner):
        raise InvalidCollectionViewPlanError(
            "concat_sample_collection_fields payload_joiner must be callable.",
            owner="concat_sample_collection_fields",
            field="payload_joiner",
            expected="callable",
            actual=type(joiner).__name__,
        )
    fields: dict[FieldLocator, FieldValue] = {}
    for source, target in plan.field_map.items():
        payloads = tuple(entry.value.require(source) for entry in collection.entries)
        try:
            payload = joiner(payloads)
        except Exception as exc:
            raise InvalidCollectionContextError(
                "Sample collection payload joiner failed.",
                owner="concat_sample_collection_fields",
                field="payload_joiner",
                source=str(source),
                target=str(target),
            ) from exc
        fields[target] = FieldValue(
            payload,
            metadata={
                **plan.metadata,
                "collection.operation": plan.name,
                "collection.source_field": str(source),
                "collection.source_count": len(collection),
                "collection.joiner": getattr(joiner, "__name__", joiner.__class__.__name__),
            },
        )
    return Sample(fields)


class PlannedSampleCollectionView:
    """Concrete view executor for descriptor-driven test/sample behavior.

    ``stitcher`` is an injected fake behavior used only when
    ``plan.stitch_policy == "fake"``. It receives grouped/sorted entries and
    returns one reconstructed ``Sample`` for that group.
    """

    def __init__(
        self,
        plan: SampleCollectionViewPlan,
        *,
        stitcher: Callable[[tuple[CollectionItem[Sample], ...], SampleCollectionViewPlan], Sample]
        | None = None,
    ) -> None:
        if not isinstance(plan, SampleCollectionViewPlan):
            raise InvalidCollectionViewPlanError(
                "PlannedSampleCollectionView plan must be a SampleCollectionViewPlan.",
                owner="PlannedSampleCollectionView",
                field="plan",
                expected="SampleCollectionViewPlan",
                actual=type(plan).__name__,
            )
        if plan.stitch_policy == "fake" and stitcher is None:
            raise InvalidCollectionViewPlanError(
                "Fake sample stitching requires an injected stitcher.",
                owner="PlannedSampleCollectionView",
                field="stitcher",
            )
        if plan.stitch_policy != "fake" and stitcher is not None:
            raise InvalidCollectionViewPlanError(
                "Injected stitchers are only allowed for fake stitch policy.",
                owner="PlannedSampleCollectionView",
                field="stitcher",
            )
        self._plan = plan
        self._stitcher = stitcher

    @property
    def plan(self) -> SampleCollectionViewPlan:
        return self._plan

    def __call__(self, collection: SampleCollection) -> SampleCollection:
        if not isinstance(collection, SampleCollection):
            raise InvalidCollectionContextError(
                "SampleCollectionView requires a SampleCollection input.",
                owner="PlannedSampleCollectionView",
                field="collection",
                expected="SampleCollection",
                actual=type(collection).__name__,
            )
        output: list[CollectionItem[Sample]] = []
        for group_key, entries in _group_entries(collection.entries, self.plan.group_keys):
            sorted_entries = _sort_entries(entries, self.plan)
            if self.plan.stitch_policy == "fake":
                assert self._stitcher is not None
                sample = self._stitcher(tuple(sorted_entries), self.plan)
                if not isinstance(sample, Sample):
                    raise InvalidCollectionContextError(
                        "Injected sample stitcher must return a Sample.",
                        owner="PlannedSampleCollectionView",
                        field="stitcher",
                        expected="Sample",
                        actual=type(sample).__name__,
                    )
                output.append(
                    CollectionItem(
                        sample,
                        metadata=_view_entry_metadata(group_key, sorted_entries, self.plan),
                        provenance={"view": self.plan.name, "source_count": len(sorted_entries)},
                    )
                )
                continue
            for entry in sorted_entries:
                output.append(
                    CollectionItem(
                        _select_fields(entry.value, self.plan.selected_fields),
                        metadata={
                            **entry.metadata,
                            "view": self.plan.name,
                            "source_count": 1,
                        },
                        provenance={**entry.provenance, "view": self.plan.name},
                    )
                )
        return SampleCollection(
            output,
            metadata={**collection.metadata, "view": self.plan.name},
            provenance={**collection.provenance, "view": self.plan.name},
        )


def _coerce_entries(
    values: Iterable[Sample | CollectionItem[Sample]],
) -> tuple[CollectionItem[Sample], ...]:
    try:
        entries = tuple(_coerce_entry(value) for value in values)
    except TypeError as exc:
        raise InvalidCollectionContextError(
            "SampleCollection entries must be iterable.",
            owner="SampleCollection",
            field="entries",
            expected="iterable of Sample | CollectionItem[Sample]",
            actual=type(values).__name__,
        ) from exc
    return entries


def _coerce_entry(value: Sample | CollectionItem[Sample]) -> CollectionItem[Sample]:
    if isinstance(value, CollectionItem):
        if not isinstance(value.value, Sample):
            raise InvalidCollectionContextError(
                "Sample collection entries must wrap Sample values.",
                owner="SampleCollection",
                field="entries",
                expected="Sample",
                actual=type(value.value).__name__,
            )
        return value
    if isinstance(value, Sample):
        return CollectionItem(value)
    raise InvalidCollectionContextError(
        "Sample collection entries must be Sample values or CollectionItem records.",
        owner="SampleCollection",
        field="entries",
        expected="Sample | CollectionItem[Sample]",
        actual=type(value).__name__,
    )


def _coerce_non_empty_string(
    value: object,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidCollectionContextError | InvalidCollectionViewPlanError | InvalidCollectorResultError],
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
    error_type: type[InvalidCollectorResultError],
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
    error_type: type[InvalidCollectionContextError | InvalidCollectionViewPlanError | InvalidCollectorResultError],
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
    resolved: dict[str, object] = {}
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
        resolved[key] = item
    return MappingProxyType(resolved)


def _coerce_key_tuple(values: Iterable[str], *, owner: str, field: str) -> tuple[str, ...]:
    try:
        keys = tuple(
            _coerce_non_empty_string(
                value,
                owner=owner,
                field=field,
                error_type=InvalidCollectionViewPlanError,
            )
            for value in values
        )
    except TypeError as exc:
        raise InvalidCollectionViewPlanError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected="iterable of strings",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise InvalidCollectionViewPlanError(
            f"{owner} {field} must not contain duplicates.",
            owner=owner,
            field=field,
            duplicates=tuple(duplicates),
        )
    return keys


def _coerce_locator_tuple(
    values: Iterable[FieldLocator | str],
    *,
    owner: str,
) -> tuple[FieldLocator, ...]:
    try:
        locators = tuple(
            value if isinstance(value, FieldLocator) else FieldLocator.parse(value)
            for value in values
        )
    except TypeError as exc:
        raise InvalidCollectionViewPlanError(
            f"{owner} selected_fields must be iterable.",
            owner=owner,
            field="selected_fields",
            expected="iterable of FieldLocator | str",
            actual=type(values).__name__,
        ) from exc
    duplicates = sorted({str(locator) for locator in locators if locators.count(locator) > 1})
    if duplicates:
        raise InvalidCollectionViewPlanError(
            f"{owner} selected_fields must not contain duplicates.",
            owner=owner,
            field="selected_fields",
            duplicates=tuple(duplicates),
        )
    return locators


def _coerce_locator_mapping(
    value: Mapping[object, FieldLocator | str] | None,
    *,
    owner: str,
    field: str,
) -> Mapping[str, FieldLocator]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise InvalidCollectionViewPlanError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping of group name to FieldLocator | str",
            actual=type(value).__name__,
        )
    resolved: dict[str, FieldLocator] = {}
    for key, locator in value.items():
        name = _coerce_non_empty_string(
            key,
            owner=owner,
            field=field,
            error_type=InvalidCollectionViewPlanError,
        )
        if name in resolved:
            raise InvalidCollectionViewPlanError(
                f"{owner} {field} must not contain duplicate names.",
                owner=owner,
                field=field,
                duplicate=name,
            )
        resolved[name] = locator if isinstance(locator, FieldLocator) else FieldLocator.parse(locator)
    return MappingProxyType(resolved)


def _coerce_field_map(
    value: Mapping[FieldLocator | str, FieldLocator | str],
    *,
    owner: str,
) -> Mapping[FieldLocator, FieldLocator]:
    if not isinstance(value, Mapping):
        raise InvalidCollectionViewPlanError(
            f"{owner} field_map must be a mapping.",
            owner=owner,
            field="field_map",
            expected="mapping of source locator to target locator",
            actual=type(value).__name__,
        )
    if not value:
        raise InvalidCollectionViewPlanError(
            f"{owner} field_map must not be empty.",
            owner=owner,
            field="field_map",
            expected="non-empty mapping",
            actual="empty mapping",
        )
    resolved: dict[FieldLocator, FieldLocator] = {}
    targets: list[FieldLocator] = []
    for source, target in value.items():
        source_locator = source if isinstance(source, FieldLocator) else FieldLocator.parse(source)
        target_locator = target if isinstance(target, FieldLocator) else FieldLocator.parse(target)
        resolved[source_locator] = target_locator
        targets.append(target_locator)
    duplicates = sorted({str(locator) for locator in targets if targets.count(locator) > 1})
    if duplicates:
        raise InvalidCollectionViewPlanError(
            f"{owner} field_map target locators must be unique.",
            owner=owner,
            field="field_map",
            duplicates=tuple(duplicates),
        )
    return MappingProxyType(resolved)


def _coerce_policy(value: str | None, *, allowed: frozenset[str | None], owner: str, field: str) -> str | None:
    if value not in allowed:
        raise InvalidCollectionViewPlanError(
            f"{owner} {field} is not supported by the Stage 11 contract.",
            owner=owner,
            field=field,
            expected=tuple(sorted(item for item in allowed if item is not None)),
            actual=value,
        )
    return value


def _group_entry_metadata(
    entry: CollectionItem[Sample],
    plan: SampleCollectionGroupPlan,
) -> Mapping[str, object]:
    metadata: dict[str, object] = {}
    for key in plan.group_keys:
        if key not in entry.metadata:
            if plan.missing_policy == "allow":
                metadata[key] = None
                continue
            raise InvalidCollectionContextError(
                "Sample collection entry is missing group metadata.",
                owner="group_sample_collections",
                field="group_keys",
                missing=(key,),
            )
        metadata[key] = entry.metadata[key]
    for key, locator in plan.field_group_keys.items():
        if not entry.value.has(locator):
            if plan.missing_policy == "allow":
                metadata[key] = None
                continue
            raise InvalidCollectionContextError(
                "Sample collection entry is missing field group key.",
                owner="group_sample_collections",
                field="field_group_keys",
                missing=(str(locator),),
            )
        metadata[key] = entry.value.get(locator)
    return MappingProxyType(metadata)


def _validate_hashable_group_key(key: tuple[object, ...], *, owner: str) -> None:
    try:
        hash(key)
    except TypeError as exc:
        raise InvalidCollectionContextError(
            "Sample grouping keys must be hashable values.",
            owner=owner,
            field="group_keys",
            actual=tuple(type(value).__name__ for value in key),
        ) from exc


def _sort_entry_key(
    entry: CollectionItem[Sample],
    plan: SampleCollectionSortPlan,
) -> tuple[object, ...]:
    values: list[object] = []
    for key in plan.sort_keys:
        if key not in entry.metadata:
            if plan.missing_policy == "allow":
                values.append(None)
                continue
            raise InvalidCollectionContextError(
                "Sample collection entry is missing sort metadata.",
                owner="sort_sample_collection",
                field="sort_keys",
                missing=(key,),
            )
        values.append(entry.metadata[key])
    for locator in plan.field_sort_keys:
        if not entry.value.has(locator):
            if plan.missing_policy == "allow":
                values.append(None)
                continue
            raise InvalidCollectionContextError(
                "Sample collection entry is missing sort field.",
                owner="sort_sample_collection",
                field="field_sort_keys",
                missing=(str(locator),),
            )
        values.append(entry.value.get(locator))
    return tuple(values)


def _validate_required_metadata(
    entry: CollectionItem[Sample],
    required_metadata: tuple[str, ...],
) -> None:
    missing = tuple(key for key in required_metadata if key not in entry.metadata)
    if missing:
        raise InvalidCollectionContextError(
            "Sample collection entry is missing required metadata.",
            owner="SampleCollector",
            field="required_metadata",
            missing=missing,
        )


def _group_entries(
    entries: Sequence[CollectionItem[Sample]],
    group_keys: tuple[str, ...],
) -> tuple[tuple[tuple[object, ...], tuple[CollectionItem[Sample], ...]], ...]:
    if not group_keys:
        return (((), tuple(entries)),)
    groups: dict[tuple[object, ...], list[CollectionItem[Sample]]] = {}
    for entry in entries:
        missing = tuple(key for key in group_keys if key not in entry.metadata)
        if missing:
            raise InvalidCollectionContextError(
                "Sample collection entry is missing group metadata.",
                owner="PlannedSampleCollectionView",
                field="group_keys",
                missing=missing,
            )
        group_key = tuple(entry.metadata[key] for key in group_keys)
        groups.setdefault(group_key, []).append(entry)
    return tuple((key, tuple(group_entries)) for key, group_entries in groups.items())


def _sort_entries(
    entries: tuple[CollectionItem[Sample], ...],
    plan: SampleCollectionViewPlan,
) -> tuple[CollectionItem[Sample], ...]:
    if not plan.sort_keys:
        return entries
    for entry in entries:
        missing = tuple(key for key in plan.sort_keys if key not in entry.metadata)
        if missing and plan.missing_window_policy == "error":
            raise InvalidCollectionContextError(
                "Sample collection entry is missing sort metadata.",
                owner="PlannedSampleCollectionView",
                field="sort_keys",
                missing=missing,
            )
    return tuple(
        sorted(
            entries,
            key=lambda entry: tuple(entry.metadata.get(key) for key in plan.sort_keys),
        )
    )


def _select_fields(sample: Sample, selected_fields: tuple[FieldLocator, ...]) -> Sample:
    if not selected_fields:
        return sample
    return Sample({locator: sample.field(locator) for locator in selected_fields})


def _view_entry_metadata(
    group_key: tuple[object, ...],
    entries: tuple[CollectionItem[Sample], ...],
    plan: SampleCollectionViewPlan,
) -> Mapping[str, object]:
    metadata = {key: value for key, value in zip(plan.group_keys, group_key, strict=True)}
    metadata.update(
        {
            "view": plan.name,
            "source_count": len(entries),
            "stitch_policy": plan.stitch_policy,
        }
    )
    if entries:
        metadata["source_metadata"] = tuple(entry.metadata for entry in entries)
    return MappingProxyType(metadata)


SampleCollection.__hash__ = None  # type: ignore[assignment]
SampleCollectionViewPlan.__hash__ = None  # type: ignore[assignment]
SampleCollectionGroupPlan.__hash__ = None  # type: ignore[assignment]
SampleCollectionSortPlan.__hash__ = None  # type: ignore[assignment]
SampleCollectionConcatPlan.__hash__ = None  # type: ignore[assignment]
