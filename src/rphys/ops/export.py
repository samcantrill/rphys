"""Data-only export descriptors, policies, layouts, and results.

Stage 8 export records describe intended field export behavior and in-memory
evidence. They do not select codecs, write files, create links, copy resources,
scan output directories, serialize durable reports, or assemble derived
datasources.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from urllib.parse import quote

from rphys.data.keys import DataKey
from rphys.data.schemas import SchemaName
from rphys.datasources.refs import RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io._primitives import (
    FrozenPrimitive,
    copy_string_mapping,
    thaw_primitive,
)
from rphys.io.codecs import CodecSaveResult, MetadataSavePolicy
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

__all__ = [
    "ExportMaterialization",
    "ExportPolicy",
    "ExportReport",
    "ExportResult",
    "ExportSpec",
    "ExportTarget",
    "FieldExportOutcome",
    "FieldExportResult",
    "IdempotencyPolicy",
    "OutputLayout",
    "RecordExportResult",
]


class IdempotencyPolicy(StrEnum):
    """Existing-target behavior requested before any export side effect."""

    FAIL_ON_EXISTING = "fail_on_existing"
    SKIP_EXISTING = "skip_existing"
    REPLACE_EXISTING = "replace_existing"


class ExportMaterialization(StrEnum):
    """Requested materialization strategy for a new target."""

    WRITE = "write"
    LINK = "link"
    COPY = "copy"


class FieldExportOutcome(StrEnum):
    """Per-field export outcome vocabulary used for in-memory reports."""

    WRITTEN = "written"
    SKIPPED = "skipped"
    LINKED = "linked"
    COPIED = "copied"
    REPLACED = "replaced"
    FAILED = "failed"


@dataclass(frozen=True, init=False, slots=True)
class ExportSpec:
    """Stable request for exporting declared fields.

    ``requested_fields`` preserves caller order for operation/report traversal.
    The stable fingerprint canonicalizes primitive content that affects target
    identity: requested field set, codec/schema requests, metadata-save policy,
    layout version, and output-shaping options. Target roots, existence checks,
    timestamps, runtime workflow state, and codec registry identity stay out of
    this fingerprint.
    """

    requested_fields: tuple[DataKey, ...]
    codec_requests: Mapping[DataKey, str]
    schema_requests: Mapping[DataKey, SchemaName]
    metadata_policy: MetadataSavePolicy
    output_options: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        requested_fields: Sequence[DataKey | str],
        *,
        codec_requests: Mapping[DataKey | str, str] | None = None,
        schema_requests: Mapping[DataKey | str, SchemaName | str] | None = None,
        metadata_policy: MetadataSavePolicy | str = MetadataSavePolicy.REFERENCE_ONLY,
        output_options: Mapping[str, object] | None = None,
    ) -> None:
        fields = _coerce_requested_fields(requested_fields)
        object.__setattr__(self, "requested_fields", fields)
        object.__setattr__(
            self,
            "codec_requests",
            MappingProxyType(_coerce_codec_requests(codec_requests, fields)),
        )
        object.__setattr__(
            self,
            "schema_requests",
            MappingProxyType(_coerce_schema_requests(schema_requests, fields)),
        )
        object.__setattr__(
            self,
            "metadata_policy",
            _coerce_metadata_policy(metadata_policy),
        )
        object.__setattr__(
            self,
            "output_options",
            MappingProxyType(
                copy_string_mapping(
                    output_options,
                    error_type=RemotePhysOperationError,
                    field="output_options",
                )
            ),
        )

    def fingerprint(self, layout: OutputLayout) -> str:
        """Return a schema-versioned digest over stable primitive inputs."""

        if not isinstance(layout, OutputLayout):
            raise RemotePhysOperationError(
                "ExportSpec fingerprint requires an OutputLayout.",
                field="layout",
                actual=type(layout).__name__,
            )
        payload = {
            "schema_version": "rphys.export-spec.v1",
            "requested_fields": sorted(str(field) for field in self.requested_fields),
            "codec_requests": {
                str(field): self.codec_requests[field]
                for field in sorted(self.codec_requests, key=str)
            },
            "schema_requests": {
                str(field): str(self.schema_requests[field])
                for field in sorted(self.schema_requests, key=str)
            },
            "metadata_policy": self.metadata_policy.value,
            "layout_version": layout.layout_version,
            "resource_suffix": layout.resource_suffix,
            "output_options": _thaw_for_json(self.output_options),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:32]


ExportSpec.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ExportTarget:
    """Root resource and export identity for deterministic target refs."""

    root: ResourceRef
    export_id: str

    def __init__(self, root: ResourceRef, export_id: str) -> None:
        if not isinstance(root, ResourceRef):
            raise RemotePhysOperationError(
                "ExportTarget root must be a ResourceRef.",
                field="root",
                actual=type(root).__name__,
            )
        object.__setattr__(self, "root", root)
        object.__setattr__(
            self,
            "export_id",
            _non_empty_token(export_id, field="export_id"),
        )


ExportTarget.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class OutputLayout:
    """Minimal deterministic layout for derived field targets.

    The layout is intentionally not a public URI-template language. It derives
    one target ``FieldRef`` from existing descriptor identity and a stable spec
    fingerprint without inspecting the filesystem.
    """

    layout_version: str
    resource_suffix: str

    def __init__(
        self,
        *,
        layout_version: str = "stage8.v1",
        resource_suffix: str = "field",
    ) -> None:
        object.__setattr__(
            self,
            "layout_version",
            _non_empty_token(layout_version, field="layout_version"),
        )
        object.__setattr__(
            self,
            "resource_suffix",
            _non_empty_token(resource_suffix, field="resource_suffix"),
        )

    def derive_target(
        self,
        record: RecordRef,
        field_key: DataKey | str,
        *,
        spec: ExportSpec,
        target: ExportTarget,
    ) -> FieldRef:
        """Derive a deterministic target ``FieldRef`` for one record field."""

        if not isinstance(record, RecordRef):
            raise RemotePhysOperationError(
                "OutputLayout target derivation requires a RecordRef.",
                field="record",
                actual=type(record).__name__,
            )
        if not isinstance(spec, ExportSpec):
            raise RemotePhysOperationError(
                "OutputLayout target derivation requires an ExportSpec.",
                field="spec",
                actual=type(spec).__name__,
            )
        if not isinstance(target, ExportTarget):
            raise RemotePhysOperationError(
                "OutputLayout target derivation requires an ExportTarget.",
                field="target",
                actual=type(target).__name__,
            )

        key = DataKey(field_key)
        if key not in spec.requested_fields:
            raise RemotePhysOperationError(
                "Cannot derive an export target for an unrequested field.",
                field="field_key",
                field_key=str(key),
            )
        if key not in record.fields:
            raise RemotePhysOperationError(
                "Cannot derive an export target for a field absent from the record.",
                field="field_key",
                field_key=str(key),
                record_id=record.record_id,
            )

        fingerprint = spec.fingerprint(self)
        source_field = record.fields[key]
        uri = _join_uri(
            target.root.uri,
            record.datasource.datasource_id,
            record.record_id,
            str(key),
            target.export_id,
            self.layout_version,
            f"{fingerprint}.{self.resource_suffix}",
        )
        resource = ResourceRef(
            uri,
            target.root.protocol,
            dict(target.root.storage_options),
        )
        schema = spec.schema_requests.get(key, source_field.schema)
        return FieldRef(
            key,
            (resource,),
            schema=schema,
            metadata={
                "export_id": target.export_id,
                "export_layout_version": self.layout_version,
                "export_spec_fingerprint": fingerprint,
                "source_datasource_id": record.datasource.datasource_id,
                "source_record_id": record.record_id,
                "source_field_key": str(key),
            },
        )


OutputLayout.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ExportPolicy:
    """Data-only export behavior policy.

    The default is fail-on-existing-target. Link/copy fallback and partial
    failure continuation are explicit policy choices and do not imply workflow
    retry or durable report semantics.
    """

    idempotency: IdempotencyPolicy
    materialization: ExportMaterialization
    allow_link_copy_fallback: bool
    continue_on_field_error: bool

    def __init__(
        self,
        *,
        idempotency: IdempotencyPolicy | str = IdempotencyPolicy.FAIL_ON_EXISTING,
        materialization: ExportMaterialization | str = ExportMaterialization.WRITE,
        allow_link_copy_fallback: bool = False,
        continue_on_field_error: bool = False,
    ) -> None:
        object.__setattr__(
            self,
            "idempotency",
            _coerce_idempotency_policy(idempotency),
        )
        object.__setattr__(
            self,
            "materialization",
            _coerce_materialization(materialization),
        )
        object.__setattr__(
            self,
            "allow_link_copy_fallback",
            _coerce_bool(
                allow_link_copy_fallback,
                field="allow_link_copy_fallback",
            ),
        )
        object.__setattr__(
            self,
            "continue_on_field_error",
            _coerce_bool(
                continue_on_field_error,
                field="continue_on_field_error",
            ),
        )

    def existing_target_outcome(self) -> FieldExportOutcome:
        """Return the explicit outcome for an existing target or raise."""

        if self.idempotency == IdempotencyPolicy.FAIL_ON_EXISTING:
            raise RemotePhysOperationError(
                "Export target already exists and policy is fail-on-existing.",
                idempotency_policy=self.idempotency.value,
            )
        if self.idempotency == IdempotencyPolicy.SKIP_EXISTING:
            return FieldExportOutcome.SKIPPED
        return FieldExportOutcome.REPLACED

    def new_target_outcome(self) -> FieldExportOutcome:
        """Return the success outcome for a target that does not exist."""

        if self.materialization == ExportMaterialization.LINK:
            return FieldExportOutcome.LINKED
        if self.materialization == ExportMaterialization.COPY:
            return FieldExportOutcome.COPIED
        return FieldExportOutcome.WRITTEN


ExportPolicy.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class FieldExportResult:
    """In-memory evidence for one requested field export.

    Results preserve source/target descriptors, ordered lineage resources, and
    optional codec-save evidence. They are not a durable report schema and do
    not expose public serialization helpers.
    """

    source_record: RecordRef
    source_field: FieldRef
    target: FieldRef
    outcome: FieldExportOutcome
    codec_result: CodecSaveResult | None
    source_resources: tuple[ResourceRef, ...]
    target_resources: tuple[ResourceRef, ...]
    failure: str | None
    metadata: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        *,
        source_record: RecordRef,
        source_field: FieldRef,
        target: FieldRef,
        outcome: FieldExportOutcome | str,
        codec_result: CodecSaveResult | None = None,
        source_resources: Sequence[ResourceRef] | None = None,
        target_resources: Sequence[ResourceRef] | None = None,
        failure: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(source_record, RecordRef):
            raise RemotePhysOperationError(
                "FieldExportResult source_record must be a RecordRef.",
                field="source_record",
                actual=type(source_record).__name__,
            )
        if not isinstance(source_field, FieldRef):
            raise RemotePhysOperationError(
                "FieldExportResult source_field must be a FieldRef.",
                field="source_field",
                actual=type(source_field).__name__,
            )
        if not isinstance(target, FieldRef):
            raise RemotePhysOperationError(
                "FieldExportResult target must be a FieldRef.",
                field="target",
                actual=type(target).__name__,
            )
        if codec_result is not None and not isinstance(codec_result, CodecSaveResult):
            raise RemotePhysOperationError(
                "FieldExportResult codec_result must be a CodecSaveResult or None.",
                field="codec_result",
                actual=type(codec_result).__name__,
            )
        if source_field.key not in source_record.fields:
            raise RemotePhysOperationError(
                "FieldExportResult source_field is not declared by source_record.",
                field="source_field",
                field_key=str(source_field.key),
                record_id=source_record.record_id,
            )
        if source_record.fields[source_field.key] != source_field:
            raise RemotePhysOperationError(
                "FieldExportResult source_field must match source_record.fields.",
                field="source_field",
                field_key=str(source_field.key),
                record_id=source_record.record_id,
            )

        resolved_outcome = _coerce_field_outcome(outcome)
        if resolved_outcome == FieldExportOutcome.FAILED:
            failure = _non_empty_failure(failure)
        elif failure is not None:
            failure = _non_empty_failure(failure)

        object.__setattr__(self, "source_record", source_record)
        object.__setattr__(self, "source_field", source_field)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "outcome", resolved_outcome)
        object.__setattr__(self, "codec_result", codec_result)
        object.__setattr__(
            self,
            "source_resources",
            _coerce_resources(
                source_resources if source_resources is not None else source_field.resources,
                field="source_resources",
            ),
        )
        object.__setattr__(
            self,
            "target_resources",
            _coerce_resources(
                target_resources
                if target_resources is not None
                else (
                    codec_result.resources
                    if codec_result is not None
                    else target.resources
                ),
                field="target_resources",
            ),
        )
        object.__setattr__(self, "failure", failure)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                copy_string_mapping(
                    metadata,
                    error_type=RemotePhysOperationError,
                    field="metadata",
                )
            ),
        )

    @property
    def succeeded(self) -> bool:
        """Whether this field produced successful export evidence."""

        return self.outcome != FieldExportOutcome.FAILED


FieldExportResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class RecordExportResult:
    """In-memory aggregation of field export results for one source record."""

    source_record: RecordRef
    field_results: tuple[FieldExportResult, ...]

    def __init__(
        self,
        source_record: RecordRef,
        field_results: Sequence[FieldExportResult],
    ) -> None:
        if not isinstance(source_record, RecordRef):
            raise RemotePhysOperationError(
                "RecordExportResult source_record must be a RecordRef.",
                field="source_record",
                actual=type(source_record).__name__,
            )
        results = _coerce_field_results(field_results)
        for result in results:
            if result.source_record != source_record:
                raise RemotePhysOperationError(
                    "RecordExportResult field results must match source_record.",
                    field="field_results",
                    record_id=source_record.record_id,
                )
        object.__setattr__(self, "source_record", source_record)
        object.__setattr__(self, "field_results", results)

    @property
    def total_count(self) -> int:
        """Total fields represented by this record result."""

        return len(self.field_results)

    def count(self, outcome: FieldExportOutcome | str) -> int:
        """Count fields with one outcome."""

        resolved_outcome = _coerce_field_outcome(outcome)
        return sum(1 for result in self.field_results if result.outcome == resolved_outcome)


RecordExportResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ExportResult:
    """In-memory export evidence across records.

    This object is the typed result payload for later export operations. It is
    deliberately not a manifest, cache key, report file, or JSON schema.
    """

    spec: ExportSpec
    target: ExportTarget
    layout: OutputLayout
    policy: ExportPolicy
    record_results: tuple[RecordExportResult, ...]

    def __init__(
        self,
        *,
        spec: ExportSpec,
        target: ExportTarget,
        layout: OutputLayout,
        policy: ExportPolicy | None = None,
        record_results: Sequence[RecordExportResult],
    ) -> None:
        if not isinstance(spec, ExportSpec):
            raise RemotePhysOperationError(
                "ExportResult spec must be an ExportSpec.",
                field="spec",
                actual=type(spec).__name__,
            )
        if not isinstance(target, ExportTarget):
            raise RemotePhysOperationError(
                "ExportResult target must be an ExportTarget.",
                field="target",
                actual=type(target).__name__,
            )
        if not isinstance(layout, OutputLayout):
            raise RemotePhysOperationError(
                "ExportResult layout must be an OutputLayout.",
                field="layout",
                actual=type(layout).__name__,
            )
        resolved_policy = ExportPolicy() if policy is None else policy
        if not isinstance(resolved_policy, ExportPolicy):
            raise RemotePhysOperationError(
                "ExportResult policy must be an ExportPolicy.",
                field="policy",
                actual=type(policy).__name__,
            )
        object.__setattr__(self, "spec", spec)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "layout", layout)
        object.__setattr__(self, "policy", resolved_policy)
        object.__setattr__(
            self,
            "record_results",
            _coerce_record_results(record_results),
        )

    @property
    def field_results(self) -> tuple[FieldExportResult, ...]:
        """Flatten field results in record order without serializing them."""

        return tuple(
            result
            for record_result in self.record_results
            for result in record_result.field_results
        )

    def count(self, outcome: FieldExportOutcome | str) -> int:
        """Count fields with one outcome."""

        resolved_outcome = _coerce_field_outcome(outcome)
        return sum(1 for result in self.field_results if result.outcome == resolved_outcome)


ExportResult.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ExportReport:
    """Typed in-memory summary counts for export evidence.

    Reports are intentionally process-local records in Stage 8. They do not
    define ``to_dict``, JSON, or report-file contracts.
    """

    export_result: ExportResult
    record_count: int
    field_count: int
    written_count: int
    skipped_count: int
    linked_count: int
    copied_count: int
    replaced_count: int
    failed_count: int

    def __init__(self, export_result: ExportResult) -> None:
        if not isinstance(export_result, ExportResult):
            raise RemotePhysOperationError(
                "ExportReport export_result must be an ExportResult.",
                field="export_result",
                actual=type(export_result).__name__,
            )
        object.__setattr__(self, "export_result", export_result)
        object.__setattr__(self, "record_count", len(export_result.record_results))
        object.__setattr__(self, "field_count", len(export_result.field_results))
        object.__setattr__(
            self,
            "written_count",
            export_result.count(FieldExportOutcome.WRITTEN),
        )
        object.__setattr__(
            self,
            "skipped_count",
            export_result.count(FieldExportOutcome.SKIPPED),
        )
        object.__setattr__(
            self,
            "linked_count",
            export_result.count(FieldExportOutcome.LINKED),
        )
        object.__setattr__(
            self,
            "copied_count",
            export_result.count(FieldExportOutcome.COPIED),
        )
        object.__setattr__(
            self,
            "replaced_count",
            export_result.count(FieldExportOutcome.REPLACED),
        )
        object.__setattr__(
            self,
            "failed_count",
            export_result.count(FieldExportOutcome.FAILED),
        )


ExportReport.__hash__ = None  # type: ignore[assignment]


def _coerce_requested_fields(
    fields: Sequence[DataKey | str],
) -> tuple[DataKey, ...]:
    if isinstance(fields, (str, bytes)) or not isinstance(fields, Sequence) or not fields:
        raise RemotePhysOperationError(
            "ExportSpec requested_fields must be a non-empty sequence.",
            field="requested_fields",
            actual=type(fields).__name__,
        )
    requested = tuple(DataKey(field) for field in fields)
    if len(set(requested)) != len(requested):
        raise RemotePhysOperationError(
            "ExportSpec requested_fields must not contain duplicates.",
            field="requested_fields",
            requested_fields=[str(field) for field in requested],
        )
    return requested


def _coerce_codec_requests(
    requests: Mapping[DataKey | str, str] | None,
    requested_fields: tuple[DataKey, ...],
) -> dict[DataKey, str]:
    if requests is None:
        return {}
    if not isinstance(requests, Mapping):
        raise RemotePhysOperationError(
            "ExportSpec codec_requests must be a mapping.",
            field="codec_requests",
            actual=type(requests).__name__,
        )
    requested = set(requested_fields)
    coerced: dict[DataKey, str] = {}
    for raw_key, raw_codec in requests.items():
        key = DataKey(raw_key)
        if key not in requested:
            raise RemotePhysOperationError(
                "ExportSpec codec_requests must reference requested fields.",
                field="codec_requests",
                field_key=str(key),
            )
        if not isinstance(raw_codec, str) or not raw_codec:
            raise RemotePhysOperationError(
                "ExportSpec codec request values must be non-empty strings.",
                field="codec_requests",
                field_key=str(key),
                actual=type(raw_codec).__name__,
            )
        coerced[key] = raw_codec
    return coerced


def _coerce_schema_requests(
    requests: Mapping[DataKey | str, SchemaName | str] | None,
    requested_fields: tuple[DataKey, ...],
) -> dict[DataKey, SchemaName]:
    if requests is None:
        return {}
    if not isinstance(requests, Mapping):
        raise RemotePhysOperationError(
            "ExportSpec schema_requests must be a mapping.",
            field="schema_requests",
            actual=type(requests).__name__,
        )
    requested = set(requested_fields)
    coerced: dict[DataKey, SchemaName] = {}
    for raw_key, raw_schema in requests.items():
        key = DataKey(raw_key)
        if key not in requested:
            raise RemotePhysOperationError(
                "ExportSpec schema_requests must reference requested fields.",
                field="schema_requests",
                field_key=str(key),
            )
        coerced[key] = SchemaName(raw_schema)
    return coerced


def _coerce_metadata_policy(value: MetadataSavePolicy | str) -> MetadataSavePolicy:
    try:
        return MetadataSavePolicy(value)
    except ValueError as exc:
        raise RemotePhysOperationError(
            "ExportSpec metadata_policy is not supported.",
            field="metadata_policy",
            actual=value,
        ) from exc


def _coerce_idempotency_policy(
    value: IdempotencyPolicy | str,
) -> IdempotencyPolicy:
    try:
        return IdempotencyPolicy(value)
    except ValueError as exc:
        raise RemotePhysOperationError(
            "ExportPolicy idempotency is not supported.",
            field="idempotency",
            actual=value,
        ) from exc


def _coerce_materialization(
    value: ExportMaterialization | str,
) -> ExportMaterialization:
    try:
        return ExportMaterialization(value)
    except ValueError as exc:
        raise RemotePhysOperationError(
            "ExportPolicy materialization is not supported.",
            field="materialization",
            actual=value,
        ) from exc


def _coerce_field_outcome(value: FieldExportOutcome | str) -> FieldExportOutcome:
    try:
        return FieldExportOutcome(value)
    except ValueError as exc:
        raise RemotePhysOperationError(
            "Field export outcome is not supported.",
            field="outcome",
            actual=value,
        ) from exc


def _coerce_bool(value: bool, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysOperationError(
            "ExportPolicy boolean fields must be bool values.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _coerce_resources(
    resources: Sequence[ResourceRef],
    *,
    field: str,
) -> tuple[ResourceRef, ...]:
    if (
        isinstance(resources, (str, bytes))
        or not isinstance(resources, Sequence)
        or len(resources) == 0
    ):
        raise RemotePhysOperationError(
            "Export lineage resources must be a non-empty sequence.",
            field=field,
            actual=type(resources).__name__,
        )
    coerced = tuple(resources)
    for resource in coerced:
        if not isinstance(resource, ResourceRef):
            raise RemotePhysOperationError(
                "Export lineage resources must contain ResourceRef values.",
                field=field,
                actual=type(resource).__name__,
            )
    return coerced


def _coerce_field_results(
    results: Sequence[FieldExportResult],
) -> tuple[FieldExportResult, ...]:
    if isinstance(results, (str, bytes)) or not isinstance(results, Sequence) or not results:
        raise RemotePhysOperationError(
            "RecordExportResult field_results must be a non-empty sequence.",
            field="field_results",
            actual=type(results).__name__,
        )
    coerced = tuple(results)
    for result in coerced:
        if not isinstance(result, FieldExportResult):
            raise RemotePhysOperationError(
                "RecordExportResult field_results must contain FieldExportResult values.",
                field="field_results",
                actual=type(result).__name__,
            )
    return coerced


def _coerce_record_results(
    results: Sequence[RecordExportResult],
) -> tuple[RecordExportResult, ...]:
    if isinstance(results, (str, bytes)) or not isinstance(results, Sequence) or not results:
        raise RemotePhysOperationError(
            "ExportResult record_results must be a non-empty sequence.",
            field="record_results",
            actual=type(results).__name__,
        )
    coerced = tuple(results)
    for result in coerced:
        if not isinstance(result, RecordExportResult):
            raise RemotePhysOperationError(
                "ExportResult record_results must contain RecordExportResult values.",
                field="record_results",
                actual=type(result).__name__,
            )
    return coerced


def _non_empty_token(value: object, *, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or "/" in value
        or "#" in value
    ):
        raise RemotePhysOperationError(
            "Export layout tokens must be non-empty strings without '/' or '#'.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value


def _non_empty_failure(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysOperationError(
            "Failed field export results require failure evidence.",
            field="failure",
            actual=type(value).__name__,
        )
    return value


def _join_uri(root_uri: str, *components: str) -> str:
    root = root_uri.rstrip("/")
    encoded = "/".join(quote(component, safe="._-") for component in components)
    return f"{root}/{encoded}"


def _thaw_for_json(value: FrozenPrimitive) -> object:
    if isinstance(value, Mapping):
        return {
            key: _thaw_for_json(value[key])
            for key in sorted(value)
        }
    if isinstance(value, tuple):
        return [_thaw_for_json(item) for item in value]
    return thaw_primitive(value)
