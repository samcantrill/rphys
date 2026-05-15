"""Framework-neutral sample source contracts for Stage 9 phase 1."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from rphys.data.containers import Sample
from rphys.data.locators import FieldLocator
from rphys.data.sample_builders import SampleBuilder
from rphys.datasources.indexes import (
    CompositeDataSourceIndex,
    DataSourceIndex,
    DataSourceIndexEntry,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive

__all__ = [
    "SampleRequest",
    "SampleRuntimeContext",
    "WorkerContextFactory",
    "SampleSource",
    "IndexSampleSource",
]

type SampleRequestLike = (
    SampleRequest | FieldLocator | str | Iterable[FieldLocator | str] | None
)


@dataclass(frozen=True, init=False, slots=True)
class SampleRequest:
    """Normalized request for one sample access call."""

    requested: tuple[FieldLocator, ...] | None
    eager: bool
    operation_fingerprint: FrozenPrimitive | None
    materialization_fingerprint: FrozenPrimitive | None
    fingerprint: str

    def __init__(
        self,
        requested: FieldLocator | str | Iterable[FieldLocator | str] | None = None,
        *,
        eager: bool = False,
        operation_fingerprint: object | None = None,
        materialization_fingerprint: object | None = None,
    ) -> None:
        object.__setattr__(self, "requested", _coerce_requested(requested))
        object.__setattr__(
            self,
            "eager",
            _coerce_bool(
                eager,
                owner="SampleRequest",
                field="eager",
            ),
        )
        object.__setattr__(
            self,
            "operation_fingerprint",
            _coerce_optional_primitive(
                operation_fingerprint,
                owner="SampleRequest",
                field="operation_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "materialization_fingerprint",
            _coerce_optional_primitive(
                materialization_fingerprint,
                owner="SampleRequest",
                field="materialization_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "fingerprint",
            _sha256(
                {
                    "requested": None
                    if self.requested is None
                    else [str(locator) for locator in self.requested],
                    "eager": self.eager,
                    "operation_fingerprint": self.operation_fingerprint,
                    "materialization_fingerprint": self.materialization_fingerprint,
                }
            ),
        )

    @classmethod
    def coerce(cls, request: SampleRequestLike) -> "SampleRequest":
        if isinstance(request, SampleRequest):
            return request
        return cls(request)


SampleRequest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SampleRuntimeContext:
    """Primitive evidence for one source sample position."""

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
    source_key: str | None
    child_index_id: str | None
    child_entry_id: str | None
    child_position: int | None
    child_index_fingerprint: str | None
    child_metadata: Mapping[str, FrozenPrimitive]
    field_windows: Mapping[str, FrozenPrimitive]
    request_fingerprint: str
    epoch: int | None
    worker_id: int | None
    worker_count: int | None
    rank: int | None
    world_size: int | None
    seed: FrozenPrimitive | None
    metadata: Mapping[str, FrozenPrimitive]
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
        source_id: str | None = None,
        groups: Mapping[str, str] | None = None,
        split: str | None = None,
        split_group: str | None = None,
        split_group_value: str | None = None,
        source_key: str | None = None,
        child_index_id: str | None = None,
        child_entry_id: str | None = None,
        child_position: int | None = None,
        child_index_fingerprint: str | None = None,
        child_metadata: Mapping[str, object] | None = None,
        field_windows: Mapping[str, object] | None = None,
        request_fingerprint: str,
        epoch: int | None = None,
        worker_id: int | None = None,
        worker_count: int | None = None,
        rank: int | None = None,
        world_size: int | None = None,
        seed: object | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "index_id",
            _coerce_non_empty_string(index_id, owner="SampleRuntimeContext", field="index_id"),
        )
        object.__setattr__(
            self,
            "entry_id",
            _coerce_non_empty_string(entry_id, owner="SampleRuntimeContext", field="entry_id"),
        )
        object.__setattr__(
            self,
            "position",
            _coerce_non_negative_int(position, owner="SampleRuntimeContext", field="position"),
        )
        object.__setattr__(
            self,
            "candidate_id",
            _coerce_non_empty_string(candidate_id, owner="SampleRuntimeContext", field="candidate_id"),
        )
        object.__setattr__(
            self,
            "record_id",
            _coerce_non_empty_string(record_id, owner="SampleRuntimeContext", field="record_id"),
        )
        object.__setattr__(
            self,
            "datasource_id",
            _coerce_non_empty_string(datasource_id, owner="SampleRuntimeContext", field="datasource_id"),
        )
        object.__setattr__(
            self,
            "source_id",
            _coerce_optional_non_empty_string(source_id, owner="SampleRuntimeContext", field="source_id"),
        )
        object.__setattr__(
            self,
            "groups",
            MappingProxyType(_coerce_string_mapping(groups, owner="SampleRuntimeContext", field="groups")),
        )
        object.__setattr__(
            self,
            "split",
            _coerce_optional_non_empty_string(split, owner="SampleRuntimeContext", field="split"),
        )
        object.__setattr__(
            self,
            "split_group",
            _coerce_optional_non_empty_string(
                split_group,
                owner="SampleRuntimeContext",
                field="split_group",
            ),
        )
        object.__setattr__(
            self,
            "split_group_value",
            _coerce_optional_non_empty_string(
                split_group_value,
                owner="SampleRuntimeContext",
                field="split_group_value",
            ),
        )
        object.__setattr__(
            self,
            "source_key",
            _coerce_optional_non_empty_string(
                source_key,
                owner="SampleRuntimeContext",
                field="source_key",
            ),
        )
        object.__setattr__(
            self,
            "child_index_id",
            _coerce_optional_non_empty_string(
                child_index_id,
                owner="SampleRuntimeContext",
                field="child_index_id",
            ),
        )
        object.__setattr__(
            self,
            "child_entry_id",
            _coerce_optional_non_empty_string(
                child_entry_id,
                owner="SampleRuntimeContext",
                field="child_entry_id",
            ),
        )
        object.__setattr__(
            self,
            "child_position",
            _coerce_optional_non_negative_int(
                child_position,
                owner="SampleRuntimeContext",
                field="child_position",
            ),
        )
        object.__setattr__(
            self,
            "child_index_fingerprint",
            _coerce_optional_non_empty_string(
                child_index_fingerprint,
                owner="SampleRuntimeContext",
                field="child_index_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "child_metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    child_metadata or {},
                    owner="SampleRuntimeContext",
                    field="child_metadata",
                )
            ),
        )
        object.__setattr__(
            self,
            "field_windows",
            MappingProxyType(
                _coerce_primitive_mapping(
                    field_windows or {},
                    owner="SampleRuntimeContext",
                    field="field_windows",
                )
            ),
        )
        object.__setattr__(
            self,
            "request_fingerprint",
            _coerce_non_empty_string(
                request_fingerprint,
                owner="SampleRuntimeContext",
                field="request_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "epoch",
            _coerce_optional_non_negative_int(epoch, owner="SampleRuntimeContext", field="epoch"),
        )
        object.__setattr__(
            self,
            "worker_id",
            _coerce_optional_non_negative_int(worker_id, owner="SampleRuntimeContext", field="worker_id"),
        )
        object.__setattr__(
            self,
            "worker_count",
            _coerce_optional_positive_int(
                worker_count,
                owner="SampleRuntimeContext",
                field="worker_count",
            ),
        )
        object.__setattr__(
            self,
            "rank",
            _coerce_optional_non_negative_int(
                rank,
                owner="SampleRuntimeContext",
                field="rank",
            ),
        )
        object.__setattr__(
            self,
            "world_size",
            _coerce_optional_positive_int(
                world_size,
                owner="SampleRuntimeContext",
                field="world_size",
            ),
        )
        object.__setattr__(
            self,
            "seed",
            _coerce_optional_primitive(seed, owner="SampleRuntimeContext", field="seed"),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_string_mapping_and_primitive(
                    metadata,
                    owner="SampleRuntimeContext",
                    field="metadata",
                )
            ),
        )
        object.__setattr__(
            self,
            "fingerprint",
            _sha256(
                {
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
                    "source_key": self.source_key,
                    "child_index_id": self.child_index_id,
                    "child_entry_id": self.child_entry_id,
                    "child_position": self.child_position,
                    "child_index_fingerprint": self.child_index_fingerprint,
                    "child_metadata": dict(self.child_metadata),
                    "field_windows": dict(self.field_windows),
                    "request_fingerprint": self.request_fingerprint,
                    "epoch": self.epoch,
                    "worker_id": self.worker_id,
                    "worker_count": self.worker_count,
                    "rank": self.rank,
                    "world_size": self.world_size,
                    "seed": self.seed,
                    "metadata": dict(self.metadata),
                }
            ),
        )


SampleRuntimeContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class WorkerContextFactory:
    """Creates deterministic evidence-only sample runtime contexts."""

    epoch: int | None
    worker_id: int | None
    worker_count: int | None
    rank: int | None
    world_size: int | None
    seed: FrozenPrimitive | None
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        *,
        epoch: int | None = None,
        worker_id: int | None = None,
        worker_count: int | None = None,
        rank: int | None = None,
        world_size: int | None = None,
        seed: object | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "epoch",
            _coerce_optional_non_negative_int(epoch, owner="WorkerContextFactory", field="epoch"),
        )
        object.__setattr__(
            self,
            "worker_id",
            _coerce_optional_non_negative_int(
                worker_id,
                owner="WorkerContextFactory",
                field="worker_id",
            ),
        )
        object.__setattr__(
            self,
            "worker_count",
            _coerce_optional_positive_int(
                worker_count,
                owner="WorkerContextFactory",
                field="worker_count",
            ),
        )
        object.__setattr__(
            self,
            "rank",
            _coerce_optional_non_negative_int(rank, owner="WorkerContextFactory", field="rank"),
        )
        object.__setattr__(
            self,
            "world_size",
            _coerce_optional_positive_int(
                world_size,
                owner="WorkerContextFactory",
                field="world_size",
            ),
        )
        object.__setattr__(
            self,
            "seed",
            _coerce_optional_primitive(seed, owner="WorkerContextFactory", field="seed"),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_string_mapping_and_primitive(
                    metadata,
                    owner="WorkerContextFactory",
                    field="metadata",
                )
            ),
        )

    def make_context(
        self,
        index_entry: DataSourceIndexEntry,
        request: SampleRequest,
    ) -> SampleRuntimeContext:
        if not isinstance(index_entry, DataSourceIndexEntry):
            raise RemotePhysDataSourceError(
                "WorkerContextFactory index_entry must be a DataSourceIndexEntry.",
                field="index_entry",
                actual=type(index_entry).__name__,
            )
        if not isinstance(request, SampleRequest):
            raise FieldTypeError(
                "WorkerContextFactory request must be a SampleRequest.",
                field="request",
                actual=type(request).__name__,
            )
        return SampleRuntimeContext(
            index_id=index_entry.index_id,
            entry_id=index_entry.entry_id,
            position=index_entry.position,
            candidate_id=index_entry.candidate_id,
            record_id=index_entry.record_id,
            datasource_id=index_entry.datasource_id,
            source_id=index_entry.source_id,
            groups=index_entry.groups,
            split=index_entry.split,
            split_group=index_entry.split_group,
            split_group_value=index_entry.split_group_value,
            source_key=index_entry.source_key,
            child_index_id=index_entry.child_index_id,
            child_entry_id=index_entry.child_entry_id,
            child_position=index_entry.child_position,
            child_index_fingerprint=index_entry.child_index_fingerprint,
            child_metadata={
                str(key): value for key, value in index_entry.child_metadata.items()
            },
            field_windows=index_entry.field_windows,
            request_fingerprint=request.fingerprint,
            epoch=self.epoch,
            worker_id=self.worker_id,
            worker_count=self.worker_count,
            rank=self.rank,
            world_size=self.world_size,
            seed=self.seed,
            metadata=self.metadata,
        )


class SampleSource:
    """Framework-neutral sample source contract."""

    def __len__(self) -> int:
        raise NotImplementedError

    def sample_at(
        self,
        position: int,
        request: SampleRequestLike = None,
        context: SampleRuntimeContext | None = None,
    ) -> Sample:
        raise NotImplementedError

    def __getitem__(self, position: int) -> Sample:
        return self.sample_at(position)


class IndexSampleSource(SampleSource):
    """Sample source over ``DataSourceIndex`` and ``CompositeDataSourceIndex``."""

    __slots__ = ("_index", "_builder", "_context_factory")

    def __init__(
        self,
        index: DataSourceIndex | CompositeDataSourceIndex,
        builder: SampleBuilder,
        *,
        context_factory: WorkerContextFactory | None = None,
    ) -> None:
        if not isinstance(index, (DataSourceIndex, CompositeDataSourceIndex)):
            raise RemotePhysDataSourceError(
                "IndexSampleSource index must be a DataSourceIndex or CompositeDataSourceIndex.",
                field="index",
                actual=type(index).__name__,
            )
        if not isinstance(builder, SampleBuilder):
            raise RemotePhysDataSourceError(
                "IndexSampleSource builder must be a SampleBuilder.",
                field="builder",
                actual=type(builder).__name__,
            )
        if context_factory is None:
            context_factory = WorkerContextFactory()
        if not isinstance(context_factory, WorkerContextFactory):
            raise RemotePhysDataSourceError(
                "IndexSampleSource context_factory must be a WorkerContextFactory.",
                field="context_factory",
                actual=type(context_factory).__name__,
            )
        self._index = index
        self._builder = builder
        self._context_factory = context_factory

    def __len__(self) -> int:
        return len(self._index)

    def sample_at(
        self,
        position: int,
        request: SampleRequestLike = None,
        context: SampleRuntimeContext | None = None,
    ) -> Sample:
        source_position = _coerce_position(position, owner="IndexSampleSource", field="position")
        if source_position >= len(self._index):
            raise RemotePhysDataSourceError(
                "Sample position is out of range.",
                field="position",
                expected=f"0 <= position < {len(self._index)}",
                actual=source_position,
            )

        if context is not None and not isinstance(context, SampleRuntimeContext):
            raise FieldTypeError(
                "IndexSampleSource context must be a SampleRuntimeContext when provided.",
                field="context",
                actual=type(context).__name__,
            )

        request_object = SampleRequest.coerce(request)
        index_item = self._index[source_position]
        index_entry = self._index.entry_at(source_position)
        _ = (
            context
            if context is not None
            else self._context_factory.make_context(
                index_entry=index_entry,
                request=request_object,
            )
        )

        return self._builder.build(
            index_item,
            requested=request_object.requested,
            eager=request_object.eager,
        )


def _coerce_requested(
    value: FieldLocator | str | Iterable[FieldLocator | str] | None,
) -> tuple[FieldLocator, ...] | None:
    if value is None:
        return None

    if isinstance(value, (FieldLocator, str)):
        values = (value,)
    else:
        try:
            values = tuple(value)
        except TypeError as exc:
            raise FieldTypeError(
                "Requested fields must be a FieldLocator, a locator string, or an iterable of locators.",
                field="requested",
                actual=type(value).__name__,
            ) from exc
        if not values:
            raise FieldTypeError(
                "Requested fields must not be empty.",
                field="requested",
            )

    locators = tuple(_coerce_locator(value_) for value_ in values)
    duplicates = sorted(
        str(locator)
        for index, locator in enumerate(locators)
        if locator in locators[:index]
    )
    if duplicates:
        raise FieldTypeError(
            "Requested locators must be unique.",
            field="requested",
            duplicates=duplicates,
        )

    return locators


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    return FieldLocator.parse(value)


def _coerce_bool(value: object, *, owner: str, field: str) -> bool:
    if type(value) is not bool:
        raise FieldTypeError(
            f"{owner} {field} must be a bool.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_non_empty_string(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldTypeError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return value


def _coerce_optional_non_empty_string(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> str | None:
    if value is None:
        return None
    return _coerce_non_empty_string(value, owner=owner, field=field)


def _coerce_optional_primitive(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> FrozenPrimitive | None:
    if value is None:
        return None
    return freeze_primitive(value, error_type=FieldTypeError, field=field)


def _coerce_non_negative_int(value: object, *, owner: str, field: str) -> int:
    if type(value) is not int:
        raise FieldTypeError(
            f"{owner} {field} must be a non-boolean integer.",
            owner=owner,
            field=field,
            expected="non-negative int",
            actual=type(value).__name__,
        )
    if value < 0:
        raise FieldTypeError(
            f"{owner} {field} must be non-negative.",
            owner=owner,
            field=field,
            actual=value,
        )
    return value


def _coerce_position(value: object, *, owner: str, field: str) -> int:
    return _coerce_non_negative_int(value, owner=owner, field=field)


def _coerce_optional_non_negative_int(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    if value is None:
        return None
    return _coerce_non_negative_int(value, owner=owner, field=field)


def _coerce_optional_positive_int(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    coerced = _coerce_optional_non_negative_int(
        value,
        owner=owner,
        field=field,
    )
    if coerced is not None and coerced == 0:
        raise FieldTypeError(
            f"{owner} {field} must be positive.",
            owner=owner,
            field=field,
            actual=coerced,
        )
    return coerced


def _coerce_string_mapping(value: Mapping[str, str] | None, *, owner: str, field: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, str]",
            actual=type(value).__name__,
        )
    output: dict[str, str] = {}
    for key, item in value.items():
        output[_coerce_non_empty_string(key, owner=owner, field=f"{field} key")] = (
            _coerce_non_empty_string(item, owner=owner, field=f"{field} value")
        )
    return output


def _coerce_string_mapping_and_primitive(
    value: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> dict[str, FrozenPrimitive]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, primitive]",
            actual=type(value).__name__,
        )
    return {
        _coerce_non_empty_string(key, owner=owner, field=f"{field} key"): (
            freeze_primitive(value_, error_type=FieldTypeError, field=f"{field}[{key}]")
        )
        for key, value_ in value.items()
    }


def _coerce_primitive_mapping(
    value: Mapping[object, object],
    *,
    owner: str,
    field: str,
) -> dict[str, FrozenPrimitive]:
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, primitive]",
            actual=type(value).__name__,
        )
    output: dict[str, FrozenPrimitive] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise FieldTypeError(
                f"{owner} {field} keys must be non-empty strings.",
                owner=owner,
                field=field,
                key=key,
                actual=type(key).__name__,
            )
        output[key] = freeze_primitive(item, error_type=FieldTypeError, field=f"{field}[{key}]")
    return output


def _canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _to_jsonable(value: object) -> object:
    if isinstance(value, MappingProxyType):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _sha256(value: Mapping[str, object]) -> str:
    encoded = _canonical_json(_to_jsonable(value)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
