"""Sample collection snapshots and descriptor-driven pre-metric views."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from rphys.collections import CollectionItem, CollectorResult
from rphys.data.containers import Sample
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
    "SampleCollector",
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


__all__.append("PlannedSampleCollectionView")


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
