"""Datasource index-candidate construction.

Phase 3 exposes provisional index candidates from non-mutating datasource
views. Candidates map role-qualified ``FieldLocator`` values to lazy
``FieldView`` descriptors and carry primitive provenance only. They do not
assign splits, load payloads, create runtime samples, allocate durable entry
identity, compute fingerprints, persist manifests, or mutate ``IndexItem``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Self

from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidIndexCandidateError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive, thaw_primitive
from rphys.io.fields import FieldView
from rphys.io.indexes import FieldIndex

from .filters import DataSourceView, FilterChain
from .refs import RecordRef

__all__ = [
    "IndexCandidate",
    "IndexCandidatePlan",
    "IndexCandidateResult",
    "IndexCandidateView",
    "build_index_candidates",
    "filter_index_candidates",
]


@dataclass(frozen=True, init=False, slots=True)
class IndexCandidatePlan:
    """Plan for mapping record fields into prospective sample locators."""

    fields: Mapping[FieldLocator, DataKey]
    field_indexes: Mapping[DataKey, FieldIndex]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        fields: Mapping[FieldLocator | str, DataKey | str],
        *,
        field_indexes: Mapping[DataKey | str, FieldIndex] | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "fields", MappingProxyType(_coerce_plan_fields(fields)))
        object.__setattr__(
            self,
            "field_indexes",
            MappingProxyType(_coerce_field_indexes(field_indexes)),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )


IndexCandidatePlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IndexCandidate:
    """Provisional loadable unit before group/split and final index identity."""

    candidate_id: str
    record: RecordRef
    fields: Mapping[FieldLocator, FieldView]
    source_id: str | None
    metadata: Mapping[MetadataKey, FrozenPrimitive]
    validation_evidence: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        candidate_id: str,
        record: RecordRef,
        fields: Mapping[FieldLocator | str, FieldView],
        *,
        source_id: str | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
        validation_evidence: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "candidate_id", _non_empty_string(candidate_id))
        if not isinstance(record, RecordRef):
            raise InvalidIndexCandidateError(
                "IndexCandidate record must be a RecordRef.",
                field="record",
                actual=type(record).__name__,
            )
        object.__setattr__(self, "record", record)
        object.__setattr__(
            self,
            "fields",
            MappingProxyType(_coerce_candidate_fields(fields, record)),
        )
        if source_id is not None:
            source_id = _non_empty_string(source_id)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )
        object.__setattr__(
            self,
            "validation_evidence",
            MappingProxyType(_coerce_string_metadata(validation_evidence)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize candidate provenance without final index-entry identity."""

        return {
            "candidate_id": self.candidate_id,
            "record": self.record.to_dict(),
            "fields": {
                str(locator): view.to_dict()
                for locator, view in self.fields.items()
            },
            "source_id": self.source_id,
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
            "validation_evidence": {
                key: thaw_primitive(value)
                for key, value in self.validation_evidence.items()
            },
        }


IndexCandidate.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IndexCandidateView:
    """Ordered selected candidates before grouping, splitting, or final indexing."""

    candidates: tuple[IndexCandidate, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        candidates: Sequence[IndexCandidate],
        *,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "candidates", _coerce_candidates(candidates))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )


IndexCandidateView.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IndexCandidateResult:
    """Candidate construction or filtering result."""

    view: IndexCandidateView
    included_count: int
    rejected_candidate_ids: Mapping[str, str]
    warnings: tuple[str, ...]

    def __init__(
        self,
        view: IndexCandidateView,
        *,
        included_count: int,
        rejected_candidate_ids: Mapping[str, str] | None = None,
        warnings: Sequence[str] = (),
    ) -> None:
        if not isinstance(view, IndexCandidateView):
            raise InvalidIndexCandidateError(
                "IndexCandidateResult view must be an IndexCandidateView.",
                field="view",
                actual=type(view).__name__,
            )
        object.__setattr__(self, "view", view)
        object.__setattr__(
            self,
            "included_count",
            _non_negative_int(included_count, field="included_count"),
        )
        object.__setattr__(
            self,
            "rejected_candidate_ids",
            MappingProxyType(_coerce_reason_mapping(rejected_candidate_ids)),
        )
        object.__setattr__(
            self,
            "warnings",
            _coerce_strings(warnings, field="warnings"),
        )


IndexCandidateResult.__hash__ = None  # type: ignore[assignment]


def build_index_candidates(
    view: DataSourceView,
    plan: IndexCandidatePlan,
) -> IndexCandidateResult:
    """Construct provisional candidates from a datasource view."""

    if not isinstance(view, DataSourceView):
        raise InvalidIndexCandidateError(
            "build_index_candidates view must be a DataSourceView.",
            field="view",
            actual=type(view).__name__,
        )
    if not isinstance(plan, IndexCandidatePlan):
        raise InvalidIndexCandidateError(
            "build_index_candidates plan must be an IndexCandidatePlan.",
            field="plan",
            actual=type(plan).__name__,
        )
    candidates: list[IndexCandidate] = []
    rejected: dict[str, str] = {}
    for record in view.records:
        missing = [key for key in plan.fields.values() if key not in record.fields]
        if missing:
            rejected[record.record_id] = "missing_fields:" + ",".join(
                str(key) for key in missing
            )
            continue
        candidate_fields = {
            locator: FieldView(
                record.fields[key],
                plan.field_indexes.get(key),
            )
            for locator, key in plan.fields.items()
        }
        candidates.append(
            IndexCandidate(
                record.record_id,
                record,
                candidate_fields,
                source_id=record.datasource.datasource_id,
                metadata=plan.metadata,
            )
        )
    candidate_view = IndexCandidateView(candidates)
    return IndexCandidateResult(
        candidate_view,
        included_count=len(candidates),
        rejected_candidate_ids=rejected,
    )


def filter_index_candidates(
    candidate_view: IndexCandidateView,
    filter_chain: FilterChain,
) -> IndexCandidateResult:
    """Apply a filter chain to provisional candidates before group/split."""

    if not isinstance(candidate_view, IndexCandidateView):
        raise InvalidIndexCandidateError(
            "filter_index_candidates requires an IndexCandidateView.",
            field="candidate_view",
            actual=type(candidate_view).__name__,
        )
    if not isinstance(filter_chain, FilterChain):
        raise InvalidIndexCandidateError(
            "filter_index_candidates requires a FilterChain.",
            field="filter_chain",
            actual=type(filter_chain).__name__,
        )
    result = filter_chain.apply(
        candidate_view.candidates,
        id_of=lambda candidate: candidate.candidate_id,
    )
    selected = IndexCandidateView(result.included, metadata=candidate_view.metadata)  # type: ignore[arg-type]
    return IndexCandidateResult(
        selected,
        included_count=len(selected.candidates),
        rejected_candidate_ids=result.excluded_ids,
        warnings=result.warnings,
    )


def _coerce_plan_fields(
    fields: Mapping[FieldLocator | str, DataKey | str],
) -> dict[FieldLocator, DataKey]:
    if not isinstance(fields, Mapping) or not fields:
        raise InvalidIndexCandidateError(
            "IndexCandidatePlan fields must be a non-empty mapping.",
            field="fields",
            actual=type(fields).__name__,
        )
    result: dict[FieldLocator, DataKey] = {}
    for locator, key in fields.items():
        field_locator = locator if isinstance(locator, FieldLocator) else FieldLocator.parse(locator)
        data_key = DataKey(key)
        if field_locator.key != data_key:
            raise InvalidIndexCandidateError(
                "IndexCandidatePlan locator key must match target field key.",
                field="fields",
                locator=str(field_locator),
                key=str(data_key),
            )
        result[field_locator] = data_key
    return result


def _coerce_field_indexes(
    value: Mapping[DataKey | str, FieldIndex] | None,
) -> dict[DataKey, FieldIndex]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidIndexCandidateError(
            "IndexCandidatePlan field_indexes must be a mapping.",
            field="field_indexes",
            actual=type(value).__name__,
        )
    result: dict[DataKey, FieldIndex] = {}
    for key, field_index in value.items():
        data_key = DataKey(key)
        if not isinstance(field_index, FieldIndex):
            raise InvalidIndexCandidateError(
                "IndexCandidatePlan field_indexes must contain FieldIndex values.",
                field="field_indexes",
                key=str(data_key),
                actual=type(field_index).__name__,
            )
        result[data_key] = field_index
    return result


def _coerce_candidate_fields(
    fields: Mapping[FieldLocator | str, FieldView],
    record: RecordRef,
) -> dict[FieldLocator, FieldView]:
    if not isinstance(fields, Mapping) or not fields:
        raise InvalidIndexCandidateError(
            "IndexCandidate fields must be a non-empty mapping.",
            field="fields",
            actual=type(fields).__name__,
        )
    result: dict[FieldLocator, FieldView] = {}
    for locator, view in fields.items():
        field_locator = locator if isinstance(locator, FieldLocator) else FieldLocator.parse(locator)
        if not isinstance(view, FieldView):
            raise InvalidIndexCandidateError(
                "IndexCandidate fields must contain FieldView values.",
                field="fields",
                locator=str(field_locator),
                actual=type(view).__name__,
            )
        if field_locator.key != view.field_ref.key:
            raise InvalidIndexCandidateError(
                "IndexCandidate locator key must match FieldView key.",
                field="fields",
                locator=str(field_locator),
                field_key=str(view.field_ref.key),
            )
        if view.field_ref.key not in record.fields:
            raise InvalidIndexCandidateError(
                "IndexCandidate field key must exist in the record.",
                field="fields",
                locator=str(field_locator),
                field_key=str(view.field_ref.key),
            )
        result[field_locator] = view
    return result


def _coerce_candidates(
    candidates: Sequence[IndexCandidate],
) -> tuple[IndexCandidate, ...]:
    if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
        raise InvalidIndexCandidateError(
            "IndexCandidateView candidates must be a sequence.",
            field="candidates",
            actual=type(candidates).__name__,
        )
    result = tuple(candidates)
    for candidate in result:
        if not isinstance(candidate, IndexCandidate):
            raise InvalidIndexCandidateError(
                "IndexCandidateView candidates must contain IndexCandidate values.",
                field="candidates",
                actual=type(candidate).__name__,
            )
    return result


def _coerce_metadata(
    metadata: Mapping[MetadataKey | str, object] | None,
) -> dict[MetadataKey, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise InvalidIndexCandidateError(
            "Index candidate metadata must be a mapping.",
            field="metadata",
            actual=type(metadata).__name__,
        )
    return {
        MetadataKey(key): freeze_primitive(
            value,
            error_type=InvalidIndexCandidateError,
            field="metadata",
        )
        for key, value in metadata.items()
    }


def _coerce_string_metadata(
    metadata: Mapping[str, object] | None,
) -> dict[str, FrozenPrimitive]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise InvalidIndexCandidateError(
            "Index candidate validation_evidence must be a mapping.",
            field="validation_evidence",
            actual=type(metadata).__name__,
        )
    result: dict[str, FrozenPrimitive] = {}
    for key, value in metadata.items():
        result[_non_empty_string(key)] = freeze_primitive(
            value,
            error_type=InvalidIndexCandidateError,
            field="validation_evidence",
        )
    return result


def _coerce_reason_mapping(value: Mapping[str, str] | None) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidIndexCandidateError(
            "Index candidate rejection reasons must be a mapping.",
            field="rejected_candidate_ids",
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key): _non_empty_string(reason)
        for key, reason in value.items()
    }


def _coerce_strings(values: Sequence[str], *, field: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidIndexCandidateError(
            "Expected a sequence of non-empty strings.",
            field=field,
            actual=type(values).__name__,
        )
    return tuple(_non_empty_string(value) for value in values)


def _non_empty_string(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidIndexCandidateError(
            "Index candidate fields must be non-empty strings.",
            actual=type(value).__name__,
            value=value,
        )
    return value


def _non_negative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InvalidIndexCandidateError(
            "Index candidate counts must be non-negative integers.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value
