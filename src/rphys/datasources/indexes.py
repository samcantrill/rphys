"""Datasource index-candidate construction.

Phase 3 exposes provisional index candidates from non-mutating datasource
views. Candidates map role-qualified ``FieldLocator`` values to lazy
``FieldView`` descriptors and carry primitive provenance only. They do not
assign splits, load payloads, create runtime samples, allocate durable entry
identity, compute fingerprints, persist manifests, or mutate ``IndexItem``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Self

from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidIndexCandidateError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive, thaw_primitive
from rphys.io.fields import FieldView
from rphys.io.indexes import FieldIndex

from .index_items import IndexItem
from .filters import DataSourceView, FilterChain
from .refs import RecordRef

__all__ = [
    "DataSourceIndex",
    "DataSourceIndexCodec",
    "DataSourceIndexEntry",
    "DataSourceIndexManifest",
    "IndexCandidate",
    "IndexCandidatePlan",
    "IndexCandidateResult",
    "IndexCandidateView",
    "IndexBuildReport",
    "IndexBuilder",
    "IndexPlan",
    "IndexResult",
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


@dataclass(frozen=True, init=False, slots=True)
class IndexPlan:
    """Plan for finalizing selected candidates into an ordered index."""

    index_id: str
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        index_id: str,
        *,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "index_id", _non_empty_string(index_id))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )


IndexPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceIndexEntry:
    """Sidecar identity and provenance for one ``DataSourceIndex`` position."""

    index_id: str
    entry_id: str
    position: int
    candidate_id: str
    record_id: str
    datasource_id: str
    source_id: str | None
    groups: Mapping[str, str]
    split: str | None
    split_group: str | None
    split_group_value: str | None
    field_windows: Mapping[str, object]
    metadata: Mapping[MetadataKey, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        *,
        index_id: str,
        entry_id: str,
        position: int,
        candidate_id: str,
        record_id: str,
        datasource_id: str,
        source_id: str | None,
        groups: Mapping[str, str] | None = None,
        split: str | None = None,
        split_group: str | None = None,
        split_group_value: str | None = None,
        field_windows: Mapping[str, object] | None = None,
        metadata: Mapping[MetadataKey | str, object] | None = None,
        fingerprint: str | None = None,
    ) -> None:
        object.__setattr__(self, "index_id", _non_empty_string(index_id))
        object.__setattr__(self, "entry_id", _non_empty_string(entry_id))
        object.__setattr__(self, "position", _non_negative_int(position, field="position"))
        object.__setattr__(self, "candidate_id", _non_empty_string(candidate_id))
        object.__setattr__(self, "record_id", _non_empty_string(record_id))
        object.__setattr__(self, "datasource_id", _non_empty_string(datasource_id))
        if source_id is not None:
            source_id = _non_empty_string(source_id)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(
            self,
            "groups",
            MappingProxyType(_coerce_string_mapping(groups, field="groups")),
        )
        object.__setattr__(self, "split", split if split is None else _non_empty_string(split))
        object.__setattr__(
            self,
            "split_group",
            split_group if split_group is None else _non_empty_string(split_group),
        )
        object.__setattr__(
            self,
            "split_group_value",
            (
                split_group_value
                if split_group_value is None
                else _non_empty_string(split_group_value)
            ),
        )
        object.__setattr__(
            self,
            "field_windows",
            MappingProxyType(_coerce_field_windows(field_windows)),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )
        stable = self._stable_payload()
        object.__setattr__(self, "fingerprint", fingerprint or _sha256(stable))

    def to_dict(self) -> dict[str, object]:
        """Serialize sidecar provenance without serializing payload data."""

        return {
            **self._stable_payload(),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a sidecar entry from manifest data."""

        data = _require_mapping(value, field="entry")
        _require_keys(
            data,
            {
                "index_id",
                "entry_id",
                "position",
                "candidate_id",
                "record_id",
                "datasource_id",
                "source_id",
                "groups",
                "split",
                "split_group",
                "split_group_value",
                "field_windows",
                "metadata",
                "fingerprint",
            },
            descriptor="DataSourceIndexEntry",
        )
        entry = cls(
            index_id=data["index_id"],  # type: ignore[arg-type]
            entry_id=data["entry_id"],  # type: ignore[arg-type]
            position=data["position"],  # type: ignore[arg-type]
            candidate_id=data["candidate_id"],  # type: ignore[arg-type]
            record_id=data["record_id"],  # type: ignore[arg-type]
            datasource_id=data["datasource_id"],  # type: ignore[arg-type]
            source_id=data["source_id"],  # type: ignore[arg-type]
            groups=data["groups"],  # type: ignore[arg-type]
            split=data["split"],  # type: ignore[arg-type]
            split_group=data["split_group"],  # type: ignore[arg-type]
            split_group_value=data["split_group_value"],  # type: ignore[arg-type]
            field_windows=data["field_windows"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
        )
        if entry.fingerprint != data["fingerprint"]:
            raise InvalidIndexCandidateError(
                "DataSourceIndexEntry fingerprint mismatch.",
                field="fingerprint",
                expected=entry.fingerprint,
                actual=data["fingerprint"],
            )
        return entry

    def _stable_payload(self) -> dict[str, object]:
        return {
            "index_id": self.index_id,
            "entry_id": self.entry_id,
            "position": self.position,
            "candidate_id": self.candidate_id,
            "record_id": self.record_id,
            "datasource_id": self.datasource_id,
            "source_id": self.source_id,
            "groups": dict(self.groups),
            "split": self.split,
            "split_group": self.split_group,
            "split_group_value": self.split_group_value,
            "field_windows": dict(self.field_windows),
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
        }


DataSourceIndexEntry.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceIndex:
    """Ordered lazy datasource index with sidecar entry provenance."""

    index_id: str
    _items: tuple[IndexItem, ...]
    _entries: tuple[DataSourceIndexEntry, ...]
    metadata: Mapping[MetadataKey, FrozenPrimitive]

    def __init__(
        self,
        index_id: str,
        items: Sequence[IndexItem],
        entries: Sequence[DataSourceIndexEntry],
        *,
        metadata: Mapping[MetadataKey | str, object] | None = None,
    ) -> None:
        item_tuple = _coerce_items(items)
        entry_tuple = _coerce_entries(entries, index_id=index_id, length=len(item_tuple))
        object.__setattr__(self, "index_id", _non_empty_string(index_id))
        object.__setattr__(self, "_items", item_tuple)
        object.__setattr__(self, "_entries", entry_tuple)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, position: int) -> IndexItem:
        return self._items[position]

    def __iter__(self):
        return iter(self._items)

    @property
    def entries(self) -> tuple[DataSourceIndexEntry, ...]:
        """Entry sidecars aligned with item positions."""

        return self._entries

    def entry_at(self, position: int) -> DataSourceIndexEntry:
        """Return the sidecar entry for ``position``."""

        return self._entries[position]


DataSourceIndex.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IndexBuildReport:
    """Counts and rejection evidence from final index construction."""

    accepted_count: int
    rejected_candidate_ids: Mapping[str, str]
    warnings: tuple[str, ...]

    def __init__(
        self,
        *,
        accepted_count: int,
        rejected_candidate_ids: Mapping[str, str] | None = None,
        warnings: Sequence[str] = (),
    ) -> None:
        object.__setattr__(
            self,
            "accepted_count",
            _non_negative_int(accepted_count, field="accepted_count"),
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


IndexBuildReport.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class IndexResult:
    """Final datasource index plus build report."""

    index: DataSourceIndex
    report: IndexBuildReport

    def __init__(self, index: DataSourceIndex, report: IndexBuildReport) -> None:
        if not isinstance(index, DataSourceIndex):
            raise InvalidIndexCandidateError(
                "IndexResult index must be a DataSourceIndex.",
                field="index",
                actual=type(index).__name__,
            )
        if not isinstance(report, IndexBuildReport):
            raise InvalidIndexCandidateError(
                "IndexResult report must be an IndexBuildReport.",
                field="report",
                actual=type(report).__name__,
            )
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "report", report)


IndexResult.__hash__ = None  # type: ignore[assignment]


class IndexBuilder:
    """Finalize selected candidates into item-yielding datasource indexes."""

    def __init__(self, plan: IndexPlan) -> None:
        if not isinstance(plan, IndexPlan):
            raise InvalidIndexCandidateError(
                "IndexBuilder plan must be an IndexPlan.",
                field="plan",
                actual=type(plan).__name__,
            )
        self.plan = plan

    def build(
        self,
        candidate_view: IndexCandidateView,
        *,
        group_result: object | None = None,
        split_result: object | None = None,
    ) -> IndexResult:
        """Build an ordered ``DataSourceIndex`` from selected candidates."""

        from .splits import GroupResult, SplitResult

        if not isinstance(candidate_view, IndexCandidateView):
            raise InvalidIndexCandidateError(
                "IndexBuilder.build requires an IndexCandidateView.",
                field="candidate_view",
                actual=type(candidate_view).__name__,
            )
        if group_result is not None and not isinstance(group_result, GroupResult):
            raise InvalidIndexCandidateError(
                "group_result must be a GroupResult.",
                field="group_result",
                actual=type(group_result).__name__,
            )
        if split_result is not None and not isinstance(split_result, SplitResult):
            raise InvalidIndexCandidateError(
                "split_result must be a SplitResult.",
                field="split_result",
                actual=type(split_result).__name__,
            )
        items: list[IndexItem] = []
        entries: list[DataSourceIndexEntry] = []
        rejected: dict[str, str] = {}
        for position, candidate in enumerate(candidate_view.candidates):
            if not candidate.fields:
                rejected[candidate.candidate_id] = "missing_fields"
                continue
            groups = _groups_for(candidate, group_result, split_result)
            split_assignment = (
                split_result.assignments.get(candidate.candidate_id)
                if split_result is not None
                else None
            )
            item = IndexItem(candidate.fields, candidate.record)
            entry = DataSourceIndexEntry(
                index_id=self.plan.index_id,
                entry_id=f"{self.plan.index_id}:{position}",
                position=len(items),
                candidate_id=candidate.candidate_id,
                record_id=candidate.record.record_id,
                datasource_id=candidate.record.datasource.datasource_id,
                source_id=candidate.source_id,
                groups=groups,
                split=str(split_assignment.split) if split_assignment is not None else None,
                split_group=(
                    split_assignment.split_group
                    if split_assignment is not None
                    else None
                ),
                split_group_value=(
                    split_assignment.split_group_value
                    if split_assignment is not None
                    else None
                ),
                field_windows=_field_windows(candidate),
                metadata=candidate.metadata,
            )
            items.append(item)
            entries.append(entry)
        index = DataSourceIndex(
            self.plan.index_id,
            items,
            entries,
            metadata=self.plan.metadata,
        )
        return IndexResult(
            index,
            IndexBuildReport(
                accepted_count=len(items),
                rejected_candidate_ids=rejected,
            ),
        )


_DATASOURCE_INDEX_SCHEMA = "rphys.datasource_index.v1"


@dataclass(frozen=True, init=False, slots=True)
class DataSourceIndexManifest:
    """Durable JSON manifest for one datasource index."""

    schema_version: str
    index_id: str
    metadata: Mapping[MetadataKey, FrozenPrimitive]
    items: tuple[Mapping[str, object], ...]
    entries: tuple[Mapping[str, object], ...]
    content_fingerprint: str
    checksum: str

    def __init__(
        self,
        *,
        schema_version: str,
        index_id: str,
        metadata: Mapping[MetadataKey | str, object],
        items: Sequence[Mapping[str, object]],
        entries: Sequence[Mapping[str, object]],
        content_fingerprint: str | None = None,
        checksum: str | None = None,
    ) -> None:
        if schema_version != _DATASOURCE_INDEX_SCHEMA:
            raise InvalidIndexCandidateError(
                "Unsupported datasource index manifest schema.",
                field="schema_version",
                expected=_DATASOURCE_INDEX_SCHEMA,
                actual=schema_version,
            )
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "index_id", _non_empty_string(index_id))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(_coerce_metadata(metadata)),
        )
        object.__setattr__(self, "items", _coerce_manifest_records(items, field="items"))
        object.__setattr__(
            self,
            "entries",
            _coerce_manifest_records(entries, field="entries"),
        )
        stable = self._stable_payload()
        fingerprint = content_fingerprint or _sha256(stable)
        if fingerprint != _sha256(stable):
            raise InvalidIndexCandidateError(
                "DataSourceIndexManifest content fingerprint mismatch.",
                field="content_fingerprint",
                expected=_sha256(stable),
                actual=fingerprint,
            )
        object.__setattr__(self, "content_fingerprint", fingerprint)
        checksum_payload = {**stable, "content_fingerprint": fingerprint}
        manifest_checksum = checksum or _sha256(checksum_payload)
        if manifest_checksum != _sha256(checksum_payload):
            raise InvalidIndexCandidateError(
                "DataSourceIndexManifest checksum mismatch.",
                field="checksum",
                expected=_sha256(checksum_payload),
                actual=manifest_checksum,
            )
        object.__setattr__(self, "checksum", manifest_checksum)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete manifest envelope."""

        return {
            **self._stable_payload(),
            "content_fingerprint": self.content_fingerprint,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Validate and reconstruct a manifest from primitive data."""

        data = _require_mapping(value, field="manifest")
        _require_keys(
            data,
            {
                "schema_version",
                "index_id",
                "metadata",
                "items",
                "entries",
                "content_fingerprint",
                "checksum",
            },
            descriptor="DataSourceIndexManifest",
        )
        return cls(
            schema_version=data["schema_version"],  # type: ignore[arg-type]
            index_id=data["index_id"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            items=data["items"],  # type: ignore[arg-type]
            entries=data["entries"],  # type: ignore[arg-type]
            content_fingerprint=data["content_fingerprint"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
        )

    def _stable_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "index_id": self.index_id,
            "metadata": {
                str(key): thaw_primitive(value)
                for key, value in self.metadata.items()
            },
            "items": [dict(item) for item in self.items],
            "entries": [dict(entry) for entry in self.entries],
        }


DataSourceIndexManifest.__hash__ = None  # type: ignore[assignment]


class DataSourceIndexCodec:
    """Canonical JSON codec for datasource index manifests."""

    schema_version = _DATASOURCE_INDEX_SCHEMA

    def to_manifest(self, index: DataSourceIndex) -> DataSourceIndexManifest:
        """Create a manifest preserving exact item and entry descriptors."""

        if not isinstance(index, DataSourceIndex):
            raise InvalidIndexCandidateError(
                "DataSourceIndexCodec.to_manifest requires a DataSourceIndex.",
                field="index",
                actual=type(index).__name__,
            )
        return DataSourceIndexManifest(
            schema_version=self.schema_version,
            index_id=index.index_id,
            metadata=index.metadata,
            items=[item.to_dict() for item in index],
            entries=[entry.to_dict() for entry in index.entries],
        )

    def from_manifest(self, manifest: DataSourceIndexManifest) -> DataSourceIndex:
        """Reconstruct a datasource index from a validated manifest."""

        if not isinstance(manifest, DataSourceIndexManifest):
            raise InvalidIndexCandidateError(
                "DataSourceIndexCodec.from_manifest requires a DataSourceIndexManifest.",
                field="manifest",
                actual=type(manifest).__name__,
            )
        items = [IndexItem.from_dict(item) for item in manifest.items]
        entries = [DataSourceIndexEntry.from_dict(entry) for entry in manifest.entries]
        return DataSourceIndex(
            manifest.index_id,
            items,
            entries,
            metadata=manifest.metadata,
        )

    def dumps(self, index: DataSourceIndex) -> str:
        """Serialize an index manifest as deterministic JSON."""

        return _canonical_json(self.to_manifest(index).to_dict())

    def loads(self, payload: str) -> DataSourceIndex:
        """Load an index from deterministic JSON manifest text."""

        if not isinstance(payload, str):
            raise InvalidIndexCandidateError(
                "DataSourceIndexCodec.loads requires JSON text.",
                field="payload",
                actual=type(payload).__name__,
            )
        data = json.loads(payload)
        return self.from_manifest(DataSourceIndexManifest.from_dict(data))

    def dump(self, index: DataSourceIndex, path: str | Path) -> None:
        """Write a deterministic JSON manifest to ``path``."""

        Path(path).write_text(self.dumps(index), encoding="utf-8")

    def load(self, path: str | Path) -> DataSourceIndex:
        """Read a deterministic JSON manifest from ``path``."""

        return self.loads(Path(path).read_text(encoding="utf-8"))


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


def _groups_for(
    candidate: IndexCandidate,
    group_result: object | None,
    split_result: object | None,
) -> Mapping[str, str]:
    if split_result is not None and candidate.candidate_id in split_result.assignments:
        return split_result.assignments[candidate.candidate_id].groups
    if group_result is not None and candidate.candidate_id in group_result.assignments:
        return group_result.assignments[candidate.candidate_id].groups
    return {}


def _field_windows(candidate: IndexCandidate) -> dict[str, object]:
    windows: dict[str, object] = {}
    for locator, view in candidate.fields.items():
        windows[str(locator)] = (
            view.field_index.to_dict() if view.field_index is not None else None
        )
    return windows


def _coerce_items(items: Sequence[IndexItem]) -> tuple[IndexItem, ...]:
    if isinstance(items, (str, bytes)) or not isinstance(items, Sequence):
        raise InvalidIndexCandidateError(
            "DataSourceIndex items must be a sequence.",
            field="items",
            actual=type(items).__name__,
        )
    result = tuple(items)
    for item in result:
        if not isinstance(item, IndexItem):
            raise InvalidIndexCandidateError(
                "DataSourceIndex items must contain IndexItem values.",
                field="items",
                actual=type(item).__name__,
            )
    return result


def _coerce_entries(
    entries: Sequence[DataSourceIndexEntry],
    *,
    index_id: str,
    length: int,
) -> tuple[DataSourceIndexEntry, ...]:
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise InvalidIndexCandidateError(
            "DataSourceIndex entries must be a sequence.",
            field="entries",
            actual=type(entries).__name__,
        )
    result = tuple(entries)
    if len(result) != length:
        raise InvalidIndexCandidateError(
            "DataSourceIndex entries must align one-to-one with items.",
            field="entries",
            expected=length,
            actual=len(result),
        )
    for expected_position, entry in enumerate(result):
        if not isinstance(entry, DataSourceIndexEntry):
            raise InvalidIndexCandidateError(
                "DataSourceIndex entries must contain DataSourceIndexEntry values.",
                field="entries",
                actual=type(entry).__name__,
            )
        if entry.index_id != index_id:
            raise InvalidIndexCandidateError(
                "DataSourceIndex entry index_id must match index_id.",
                field="entries",
                expected=index_id,
                actual=entry.index_id,
            )
        if entry.position != expected_position:
            raise InvalidIndexCandidateError(
                "DataSourceIndex entry positions must be ordered and contiguous.",
                field="entries",
                expected=expected_position,
                actual=entry.position,
            )
    return result


def _coerce_field_windows(value: Mapping[str, object] | None) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidIndexCandidateError(
            "DataSourceIndexEntry field_windows must be a mapping.",
            field="field_windows",
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key): _jsonable_window(window)
        for key, window in value.items()
    }


def _jsonable_window(value: object) -> object:
    if value is None:
        return None
    json.dumps(value, sort_keys=True)
    return value


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


def _coerce_string_mapping(
    value: Mapping[str, str] | None,
    *,
    field: str,
) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidIndexCandidateError(
            "String provenance mappings must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(key): _non_empty_string(item)
        for key, item in value.items()
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


def _coerce_manifest_records(
    values: Sequence[Mapping[str, object]],
    *,
    field: str,
) -> tuple[Mapping[str, object], ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidIndexCandidateError(
            "Manifest records must be a sequence.",
            field=field,
            actual=type(values).__name__,
        )
    records: list[Mapping[str, object]] = []
    for value in values:
        record = _require_mapping(value, field=field)
        copied = dict(record)
        json.loads(_canonical_json(copied))
        records.append(MappingProxyType(copied))
    return tuple(records)


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidIndexCandidateError(
            "Manifest values must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _require_keys(
    value: Mapping[str, object],
    keys: set[str],
    *,
    descriptor: str,
) -> None:
    actual = set(value)
    if actual != keys:
        raise InvalidIndexCandidateError(
            "Manifest keys do not match the Stage 5 schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )


def _canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(payload: Mapping[str, object]) -> str:
    encoded = _canonical_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
