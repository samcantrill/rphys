"""Build runtime samples with lazy fields from one index item.

``SampleBuilder`` bridges descriptor-only ``IndexItem`` objects to runtime
``Sample`` containers. It uses explicit ``CodecRegistry`` instances and keeps
datasource record provenance on builder-side provenance records, not on codec
contexts.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from rphys.datasources.index_items import IndexItem
from rphys.datasources.refs import RecordRef
from rphys.errors import FieldTypeError, MissingFieldError
from rphys.io._primitives import FrozenPrimitive, copy_string_mapping
from rphys.io.codecs import (
    CodecLoadResult,
    CodecProbeResult,
    CodecRegistry,
    LoadContext,
)
from rphys.io.fields import FieldView

from .containers import Sample
from .locators import FieldLocator
from .metadata import MetadataKey
from .sample_fields import SampleField

__all__ = [
    "SampleBuildContext",
    "SampleBuilder",
    "SampleFieldProvenance",
    "SampleProbeResult",
]


@dataclass(frozen=True, init=False, slots=True)
class SampleBuildContext:
    """Explicit context for one-item lazy sample construction."""

    registry: CodecRegistry
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        registry: CodecRegistry,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(registry, CodecRegistry):
            raise FieldTypeError(
                "SampleBuildContext registry must be a CodecRegistry.",
                field="registry",
                actual=type(registry).__name__,
            )
        object.__setattr__(self, "registry", registry)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                copy_string_mapping(
                    metadata,
                    error_type=FieldTypeError,
                    field="metadata",
                )
            ),
        )


SampleBuildContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SampleFieldProvenance:
    """Builder-side provenance for one lazy field handle."""

    locator: FieldLocator
    field_view: FieldView
    record: RecordRef
    item_metadata: Mapping[MetadataKey, FrozenPrimitive]
    builder_metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        *,
        locator: FieldLocator,
        field_view: FieldView,
        record: RecordRef,
        item_metadata: Mapping[MetadataKey, FrozenPrimitive],
        builder_metadata: Mapping[str, FrozenPrimitive],
    ) -> None:
        if not isinstance(locator, FieldLocator):
            raise FieldTypeError(
                "SampleFieldProvenance locator must be a FieldLocator.",
                field="locator",
                actual=type(locator).__name__,
            )
        if not isinstance(field_view, FieldView):
            raise FieldTypeError(
                "SampleFieldProvenance field_view must be a FieldView.",
                field="field_view",
                actual=type(field_view).__name__,
            )
        if not isinstance(record, RecordRef):
            raise FieldTypeError(
                "SampleFieldProvenance record must be a RecordRef.",
                field="record",
                actual=type(record).__name__,
            )
        object.__setattr__(self, "locator", locator)
        object.__setattr__(self, "field_view", field_view)
        object.__setattr__(self, "record", record)
        object.__setattr__(self, "item_metadata", MappingProxyType(dict(item_metadata)))
        object.__setattr__(
            self,
            "builder_metadata",
            MappingProxyType(dict(builder_metadata)),
        )


SampleFieldProvenance.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class SampleProbeResult:
    """Probe evidence for one requested lazy sample field."""

    locator: FieldLocator
    field_view: FieldView
    probe_result: CodecProbeResult
    provenance: SampleFieldProvenance


SampleProbeResult.__hash__ = None  # type: ignore[assignment]


class _BuiltSampleField(SampleField):
    """SampleField carrying builder-owned provenance."""

    __slots__ = ("_provenance",)

    def __init__(
        self,
        load_context: LoadContext,
        loader: Callable[[LoadContext], CodecLoadResult],
        *,
        provenance: SampleFieldProvenance,
        collate_policy: object | None = None,
    ) -> None:
        super().__init__(load_context, loader, collate_policy=collate_policy)
        self._provenance = provenance

    @property
    def provenance(self) -> SampleFieldProvenance:
        """Builder-side descriptor provenance for this lazy field."""

        return self._provenance

    def __copy__(self) -> "_BuiltSampleField":
        clone = type(self)(
            self._load_context,
            self._loader,
            provenance=self._provenance,
            collate_policy=self.collate_policy,
        )
        clone.schema = self.schema
        clone.metadata = dict(self.metadata)
        clone._state = self._state
        clone._load_result = self._load_result
        clone._load_error = self._load_error
        return clone

    def __deepcopy__(self, memo: dict[int, object]) -> "_BuiltSampleField":
        clone = type(self)(
            self._load_context,
            self._loader,
            provenance=self._provenance,
            collate_policy=copy.deepcopy(self.collate_policy, memo),
        )
        clone.schema = copy.deepcopy(self.schema, memo)
        clone.metadata = copy.deepcopy(self.metadata, memo)
        clone._state = self._state
        clone._load_result = (
            CodecLoadResult(
                copy.deepcopy(self._load_result.field_value, memo),
                metadata=dict(self._load_result.metadata),
            )
            if self._load_result is not None
            else None
        )
        clone._load_error = self._load_error
        return clone


class SampleBuilder:
    """Build lazy ``Sample`` containers from exactly one ``IndexItem``."""

    __slots__ = ("context",)

    def __init__(
        self,
        context: SampleBuildContext | None = None,
        *,
        registry: CodecRegistry | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if context is not None and registry is not None:
            raise FieldTypeError(
                "SampleBuilder accepts either context or registry, not both.",
                field="context",
            )
        if context is None:
            if registry is None:
                raise FieldTypeError(
                    "SampleBuilder requires a SampleBuildContext or CodecRegistry.",
                    field="context",
                )
            context = SampleBuildContext(registry, metadata=metadata)
        elif metadata is not None:
            raise FieldTypeError(
                "SampleBuilder metadata is accepted only with registry construction.",
                field="metadata",
            )
        if not isinstance(context, SampleBuildContext):
            raise FieldTypeError(
                "SampleBuilder context must be a SampleBuildContext.",
                field="context",
                actual=type(context).__name__,
            )
        self.context = context

    def build(
        self,
        index_item: IndexItem,
        requested: FieldLocator | str | Iterable[FieldLocator | str] | None = None,
        *,
        eager: bool = False,
    ) -> Sample:
        """Build all or requested lazy fields from one ``IndexItem``."""

        item = _require_index_item(index_item)
        locators = _select_locators(item, requested)
        sample = Sample()
        for locator in locators:
            sample.set_field(locator, self._make_field(item, locator))
        if eager:
            for locator in locators:
                sample.field(locator).eager_load()  # type: ignore[attr-defined]
        return sample

    def build_one(
        self,
        index_item: IndexItem,
        locator: FieldLocator | str,
        *,
        eager: bool = False,
    ) -> SampleField:
        """Build one lazy field handle from ``index_item``."""

        item = _require_index_item(index_item)
        selected = _select_locators(item, locator)
        field = self._make_field(item, selected[0])
        if eager:
            field.eager_load()
        return field

    def probe(
        self,
        index_item: IndexItem,
        requested: FieldLocator | str | Iterable[FieldLocator | str] | None = None,
    ) -> tuple[SampleProbeResult, ...]:
        """Probe all or requested fields without constructing payloads."""

        item = _require_index_item(index_item)
        locators = _select_locators(item, requested)
        results: list[SampleProbeResult] = []
        for locator in locators:
            field_view = item.fields[locator]
            load_context = LoadContext(field_view, metadata=self.context.metadata)
            provenance = _provenance(
                item,
                locator,
                field_view,
                builder_metadata=self.context.metadata,
            )
            results.append(
                SampleProbeResult(
                    locator=locator,
                    field_view=field_view,
                    probe_result=self.context.registry.probe(load_context),
                    provenance=provenance,
                )
            )
        return tuple(results)

    def _make_field(self, item: IndexItem, locator: FieldLocator) -> SampleField:
        field_view = item.fields[locator]
        load_context = LoadContext(field_view, metadata=self.context.metadata)
        provenance = _provenance(
            item,
            locator,
            field_view,
            builder_metadata=self.context.metadata,
        )
        return _BuiltSampleField(
            load_context,
            self.context.registry.load,
            provenance=provenance,
        )


def _require_index_item(index_item: IndexItem) -> IndexItem:
    if not isinstance(index_item, IndexItem):
        raise FieldTypeError(
            "SampleBuilder requires an IndexItem.",
            field="index_item",
            actual=type(index_item).__name__,
        )
    return index_item


def _select_locators(
    index_item: IndexItem,
    requested: FieldLocator | str | Iterable[FieldLocator | str] | None,
) -> tuple[FieldLocator, ...]:
    if requested is None:
        return tuple(index_item.fields)
    if isinstance(requested, (FieldLocator, str)):
        values: tuple[FieldLocator | str, ...] = (requested,)
    else:
        try:
            values = tuple(requested)
        except TypeError as exc:
            raise FieldTypeError(
                "Requested locators must be a locator or iterable of locators.",
                field="requested",
                actual=type(requested).__name__,
            ) from exc
        if not values:
            raise FieldTypeError("Requested locators must not be empty.")

    locators = tuple(_coerce_locator(value) for value in values)
    duplicates = sorted(
        str(locator)
        for index, locator in enumerate(locators)
        if locator in locators[:index]
    )
    if duplicates:
        raise FieldTypeError(
            "Requested locators must be unique.",
            duplicates=duplicates,
        )

    missing = tuple(locator for locator in locators if locator not in index_item.fields)
    if missing:
        raise MissingFieldError(
            "Requested field is missing from IndexItem.",
            requested=[str(locator) for locator in locators],
            missing=[str(locator) for locator in missing],
            available=[str(locator) for locator in index_item.fields],
        )
    return locators


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    return FieldLocator.parse(value)


def _provenance(
    index_item: IndexItem,
    locator: FieldLocator,
    field_view: FieldView,
    *,
    builder_metadata: Mapping[str, FrozenPrimitive],
) -> SampleFieldProvenance:
    return SampleFieldProvenance(
        locator=locator,
        field_view=field_view,
        record=index_item.record,
        item_metadata=index_item.metadata,
        builder_metadata=builder_metadata,
    )
