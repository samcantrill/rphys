"""Non-mutating datasource views and descriptor filter chains.

Views select ``RecordRef`` descriptors from a scan result without changing the
original descriptors. Filter chains operate over explicit target sequences and
return new result objects with included targets, excluded IDs, and reasons.
They do not load payloads, apply runtime sample operations, assign splits, or
create durable index-entry identity.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Protocol, Self

from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidDataSourceFilterError, InvalidDataSourceViewError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive, thaw_primitive

from .adapters import DataSourceScanResult
from .refs import DataSourceRef, RecordRef

__all__ = [
    "DataSourceFilter",
    "DataSourceView",
    "DataSourceViewPlan",
    "DataSourceViewResult",
    "FilterChain",
    "FilterDecision",
    "FilterResult",
    "build_view",
]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceViewPlan:
    """Descriptor-only record selection request for a scan result.

    ``include_record_ids`` narrows accepted scan records by exact record ID.
    Missing requested IDs are reported in ``DataSourceViewResult`` and do not
    mutate the scan result.
    """

    include_record_ids: tuple[str, ...] | None
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        *,
        include_record_ids: Sequence[str] | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "include_record_ids",
            _optional_record_ids(include_record_ids),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata, InvalidDataSourceViewError)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the view plan without filter or index-builder state."""

        return {
            "include_record_ids": (
                list(self.include_record_ids)
                if self.include_record_ids is not None
                else None
            ),
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a view plan from primitive values."""

        if not isinstance(value, Mapping) or set(value) != {
            "include_record_ids",
            "metadata",
        }:
            raise InvalidDataSourceViewError(
                "Serialized DataSourceViewPlan keys do not match Stage 5.",
                field="view_plan",
                actual=type(value).__name__,
            )
        return cls(
            include_record_ids=value["include_record_ids"],  # type: ignore[arg-type]
            metadata=value["metadata"],  # type: ignore[arg-type]
        )


DataSourceViewPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceView:
    """Immutable descriptor view over accepted scan records."""

    datasource: DataSourceRef
    records: tuple[RecordRef, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        datasource: DataSourceRef,
        records: Sequence[RecordRef],
        *,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise InvalidDataSourceViewError(
                "DataSourceView datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(self, "records", _coerce_records(records, datasource))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata, InvalidDataSourceViewError)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize selected descriptors without filters, splits, or indexes."""

        return {
            "datasource": self.datasource.to_dict(),
            "records": [record.to_dict() for record in self.records],
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }


DataSourceView.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceViewResult:
    """Result of building a non-mutating datasource view."""

    view: DataSourceView
    included_count: int
    excluded_record_ids: Mapping[str, str]
    warnings: tuple[str, ...]

    def __init__(
        self,
        view: DataSourceView,
        *,
        included_count: int,
        excluded_record_ids: Mapping[str, str] | None = None,
        warnings: Sequence[str] = (),
    ) -> None:
        if not isinstance(view, DataSourceView):
            raise InvalidDataSourceViewError(
                "DataSourceViewResult view must be a DataSourceView.",
                field="view",
                actual=type(view).__name__,
            )
        object.__setattr__(self, "view", view)
        object.__setattr__(
            self,
            "included_count",
            _non_negative_int(
                included_count,
                field="included_count",
                error_type=InvalidDataSourceViewError,
            ),
        )
        object.__setattr__(
            self,
            "excluded_record_ids",
            MappingProxyType(
                _coerce_reason_mapping(
                    excluded_record_ids,
                    error_type=InvalidDataSourceViewError,
                    field="excluded_record_ids",
                )
            ),
        )
        object.__setattr__(
            self,
            "warnings",
            _coerce_strings(
                warnings,
                field="warnings",
                error_type=InvalidDataSourceViewError,
            ),
        )


DataSourceViewResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class FilterDecision:
    """Single filter decision for one descriptor or candidate target."""

    include: bool
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.include, bool):
            raise InvalidDataSourceFilterError(
                "FilterDecision include must be a bool.",
                field="include",
                actual=type(self.include).__name__,
            )
        if not isinstance(self.reason, str):
            raise InvalidDataSourceFilterError(
                "FilterDecision reason must be a string.",
                field="reason",
                actual=type(self.reason).__name__,
            )


class DataSourceFilter(Protocol):
    """Structural descriptor filter.

    Implementations receive the typed target chosen by the caller, such as a
    ``RecordRef`` or ``IndexCandidate``, and return either a bool or a
    ``FilterDecision``.
    """

    def evaluate(self, target: object) -> bool | FilterDecision:
        """Return whether ``target`` should be included."""


@dataclass(frozen=True, init=False, slots=True)
class FilterResult:
    """Included targets and exclusion reasons from a filter chain."""

    target_kind: str
    included: tuple[object, ...]
    excluded_ids: Mapping[str, str]
    warnings: tuple[str, ...]

    def __init__(
        self,
        target_kind: str,
        included: Sequence[object],
        *,
        excluded_ids: Mapping[str, str] | None = None,
        warnings: Sequence[str] = (),
    ) -> None:
        object.__setattr__(
            self,
            "target_kind",
            _non_empty_string(
                target_kind,
                field="target_kind",
                error_type=InvalidDataSourceFilterError,
            ),
        )
        object.__setattr__(self, "included", tuple(included))
        object.__setattr__(
            self,
            "excluded_ids",
            MappingProxyType(
                _coerce_reason_mapping(
                    excluded_ids,
                    error_type=InvalidDataSourceFilterError,
                    field="excluded_ids",
                )
            ),
        )
        object.__setattr__(
            self,
            "warnings",
            _coerce_strings(
                warnings,
                field="warnings",
                error_type=InvalidDataSourceFilterError,
            ),
        )


FilterResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class FilterChain:
    """Ordered structural filters over explicit descriptor targets."""

    filters: tuple[object, ...]
    target_kind: str

    def __init__(
        self,
        filters: Sequence[object],
        *,
        target_kind: str,
    ) -> None:
        if isinstance(filters, (str, bytes)) or not isinstance(filters, Sequence):
            raise InvalidDataSourceFilterError(
                "FilterChain filters must be a sequence.",
                field="filters",
                actual=type(filters).__name__,
            )
        for filter_obj in filters:
            if not callable(filter_obj) and not hasattr(filter_obj, "evaluate"):
                raise InvalidDataSourceFilterError(
                    "Filters must be callable or expose evaluate(target).",
                    field="filters",
                    actual=type(filter_obj).__name__,
                )
        object.__setattr__(self, "filters", tuple(filters))
        object.__setattr__(
            self,
            "target_kind",
            _non_empty_string(
                target_kind,
                field="target_kind",
                error_type=InvalidDataSourceFilterError,
            ),
        )

    def apply(
        self,
        targets: Sequence[object],
        *,
        id_of: Callable[[object], str],
    ) -> FilterResult:
        """Apply filters in order and return a non-mutating result."""

        if isinstance(targets, (str, bytes)) or not isinstance(targets, Sequence):
            raise InvalidDataSourceFilterError(
                "FilterChain targets must be a sequence.",
                field="targets",
                actual=type(targets).__name__,
            )
        included: list[object] = []
        excluded: dict[str, str] = {}
        for target in targets:
            target_id = _non_empty_string(
                id_of(target),
                field="target_id",
                error_type=InvalidDataSourceFilterError,
            )
            decision = self._decision_for(target)
            if decision.include:
                included.append(target)
            else:
                excluded[target_id] = decision.reason or "excluded"
        return FilterResult(
            self.target_kind,
            tuple(included),
            excluded_ids=excluded,
        )

    def _decision_for(self, target: object) -> FilterDecision:
        for filter_obj in self.filters:
            decision = _evaluate_filter(filter_obj, target)
            if not decision.include:
                return decision
        return FilterDecision(True)


FilterChain.__hash__ = None  # type: ignore[assignment]


def build_view(
    scan_result: DataSourceScanResult,
    plan: DataSourceViewPlan | None = None,
) -> DataSourceViewResult:
    """Build a non-mutating datasource view from scan descriptors."""

    if not isinstance(scan_result, DataSourceScanResult):
        raise InvalidDataSourceViewError(
            "build_view requires a DataSourceScanResult.",
            field="scan_result",
            actual=type(scan_result).__name__,
        )
    view_plan = plan or DataSourceViewPlan()
    if not isinstance(view_plan, DataSourceViewPlan):
        raise InvalidDataSourceViewError(
            "build_view plan must be a DataSourceViewPlan.",
            field="plan",
            actual=type(view_plan).__name__,
        )

    selected = view_plan.include_record_ids
    selected_set = set(selected) if selected is not None else None
    records: list[RecordRef] = []
    excluded: dict[str, str] = {}
    for record in scan_result.records:
        if selected_set is not None and record.record_id not in selected_set:
            excluded[record.record_id] = "not_selected"
            continue
        records.append(record)
    if selected_set is not None:
        observed = {record.record_id for record in scan_result.records}
        for missing in selected_set - observed:
            excluded[missing] = "missing_from_scan"

    view = DataSourceView(
        scan_result.datasource,
        tuple(records),
        metadata=view_plan.metadata,
    )
    return DataSourceViewResult(
        view,
        included_count=len(records),
        excluded_record_ids=excluded,
    )


def _evaluate_filter(filter_obj: object, target: object) -> FilterDecision:
    if hasattr(filter_obj, "evaluate"):
        raw = filter_obj.evaluate(target)  # type: ignore[attr-defined]
    elif callable(filter_obj):
        raw = filter_obj(target)
    else:
        raise InvalidDataSourceFilterError(
            "Filter object is not callable and has no evaluate method.",
            field="filters",
            actual=type(filter_obj).__name__,
        )
    if isinstance(raw, FilterDecision):
        return raw
    if isinstance(raw, bool):
        return FilterDecision(raw)
    if isinstance(raw, tuple) and len(raw) == 2 and isinstance(raw[0], bool):
        reason = raw[1]
        if not isinstance(reason, str):
            raise InvalidDataSourceFilterError(
                "Filter tuple reason must be a string.",
                field="reason",
                actual=type(reason).__name__,
            )
        return FilterDecision(raw[0], reason)
    raise InvalidDataSourceFilterError(
        "Filters must return bool, FilterDecision, or (bool, reason).",
        field="filters",
        actual=type(raw).__name__,
    )


def _coerce_records(
    records: Sequence[RecordRef],
    datasource: DataSourceRef,
) -> tuple[RecordRef, ...]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise InvalidDataSourceViewError(
            "DataSourceView records must be a sequence.",
            field="records",
            actual=type(records).__name__,
        )
    result = tuple(records)
    for position, record in enumerate(result):
        if not isinstance(record, RecordRef):
            raise InvalidDataSourceViewError(
                "DataSourceView records must contain RecordRef values.",
                field="records",
                position=position,
                actual=type(record).__name__,
            )
        if record.datasource.datasource_id != datasource.datasource_id:
            raise InvalidDataSourceViewError(
                "DataSourceView records must match datasource_id.",
                field="records",
                position=position,
                expected=datasource.datasource_id,
                actual=record.datasource.datasource_id,
            )
    return result


def _optional_record_ids(value: Sequence[str] | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    ids = _coerce_strings(
        value,
        field="include_record_ids",
        error_type=InvalidDataSourceViewError,
    )
    if len(set(ids)) != len(ids):
        raise InvalidDataSourceViewError(
            "DataSourceViewPlan include_record_ids must not contain duplicates.",
            field="include_record_ids",
            values=list(ids),
        )
    return ids


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
    error_type: type[InvalidDataSourceViewError],
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise error_type(
            "Datasource view metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=error_type,
            field="metadata",
        )
        for key, value in metadata.items()
    }


def _coerce_reason_mapping(
    value: Mapping[str, str] | None,
    *,
    error_type: type[InvalidDataSourceViewError | InvalidDataSourceFilterError],
    field: str,
) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise error_type(
            "Reason mappings must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key, field=field, error_type=error_type): _non_empty_string(
            reason,
            field=field,
            error_type=error_type,
        )
        for key, reason in value.items()
    }


def _coerce_strings(
    values: Sequence[str],
    *,
    field: str,
    error_type: type[InvalidDataSourceViewError | InvalidDataSourceFilterError],
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise error_type(
            "Expected a sequence of non-empty strings.",
            field=field,
            actual=type(values).__name__,
        )
    return tuple(
        _non_empty_string(value, field=field, error_type=error_type)
        for value in values
    )


def _non_empty_string(
    value: object,
    *,
    field: str,
    error_type: type[InvalidDataSourceViewError | InvalidDataSourceFilterError],
) -> str:
    if not isinstance(value, str) or not value:
        raise error_type(
            "Descriptor fields must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value


def _non_negative_int(
    value: object,
    *,
    field: str,
    error_type: type[InvalidDataSourceViewError],
) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise error_type(
            "Counts must be non-negative integers.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value
