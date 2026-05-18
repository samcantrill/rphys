"""Data-only export descriptors, policies, layouts, and results.

Stage 8 export records describe intended field export behavior and in-memory
evidence. They do not select codecs, write files, create links, copy resources,
scan output directories, serialize durable reports, or assemble derived
datasources.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from urllib.parse import quote, unquote, urlparse

from rphys.data.containers import Sample
from rphys.data.fields import FieldValue
from rphys.data.keys import DataKey
from rphys.data.locators import FieldLocator
from rphys.data.schemas import SchemaName
from rphys.datasources.refs import RecordRef
from rphys.errors import RemotePhysOperationError
from rphys.io._primitives import (
    FrozenPrimitive,
    copy_string_mapping,
    thaw_primitive,
)
from rphys.io.codecs import (
    CodecRegistry,
    CodecSaveResult,
    MetadataSavePolicy,
    SaveContext,
)
from rphys.io.fields import FieldRef
from rphys.io.resources import ResourceRef

from .context import OperationContext, OperationResult
from .contracts import OperationContract, OperationMutationPolicy

__all__ = [
    "CodecSelectionOperation",
    "ExportMaterialization",
    "ExportPolicy",
    "ExportReport",
    "ExportSelection",
    "ExportResult",
    "ExportSpec",
    "ExportTarget",
    "FieldExportOutcome",
    "FieldExportResult",
    "IdempotencyPolicy",
    "OutputLayout",
    "RecordExportResult",
    "RecordExportRequest",
    "SaveOperation",
    "SelectedFieldExport",
    "build_sample_artifact_record",
    "export_record_requests",
    "sample_artifact_export_request",
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
class RecordExportRequest:
    """Runtime request for selecting or saving one datasource record.

    This record joins descriptor-only export intent with loaded field values.
    It is an operation input, not a durable manifest or report schema.
    """

    source_record: RecordRef
    field_values: Mapping[DataKey, FieldValue]
    spec: ExportSpec
    target: ExportTarget
    layout: OutputLayout
    policy: ExportPolicy

    def __init__(
        self,
        *,
        source_record: RecordRef,
        field_values: Mapping[DataKey | str, FieldValue],
        spec: ExportSpec,
        target: ExportTarget,
        layout: OutputLayout | None = None,
        policy: ExportPolicy | None = None,
    ) -> None:
        if not isinstance(source_record, RecordRef):
            raise RemotePhysOperationError(
                "RecordExportRequest source_record must be a RecordRef.",
                field="source_record",
                actual=type(source_record).__name__,
            )
        if not isinstance(spec, ExportSpec):
            raise RemotePhysOperationError(
                "RecordExportRequest spec must be an ExportSpec.",
                field="spec",
                actual=type(spec).__name__,
            )
        if not isinstance(target, ExportTarget):
            raise RemotePhysOperationError(
                "RecordExportRequest target must be an ExportTarget.",
                field="target",
                actual=type(target).__name__,
            )
        resolved_layout = OutputLayout() if layout is None else layout
        if not isinstance(resolved_layout, OutputLayout):
            raise RemotePhysOperationError(
                "RecordExportRequest layout must be an OutputLayout.",
                field="layout",
                actual=type(layout).__name__,
            )
        resolved_policy = ExportPolicy() if policy is None else policy
        if not isinstance(resolved_policy, ExportPolicy):
            raise RemotePhysOperationError(
                "RecordExportRequest policy must be an ExportPolicy.",
                field="policy",
                actual=type(policy).__name__,
            )

        object.__setattr__(self, "source_record", source_record)
        object.__setattr__(
            self,
            "field_values",
            MappingProxyType(_coerce_field_values(field_values, source_record)),
        )
        object.__setattr__(self, "spec", spec)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "layout", resolved_layout)
        object.__setattr__(self, "policy", resolved_policy)


RecordExportRequest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class SelectedFieldExport:
    """No-write selection evidence for one requested field.

    The selected codec name is diagnostic evidence for the in-memory operation
    result. It is not a durable codec registry schema.
    """

    source_record: RecordRef
    source_field: FieldRef
    field_value: FieldValue
    target: FieldRef
    metadata_policy: MetadataSavePolicy
    codec_name: str
    codec_request: str | None

    def __init__(
        self,
        *,
        source_record: RecordRef,
        source_field: FieldRef,
        field_value: FieldValue,
        target: FieldRef,
        metadata_policy: MetadataSavePolicy | str,
        codec_name: str,
        codec_request: str | None = None,
    ) -> None:
        if not isinstance(source_record, RecordRef):
            raise RemotePhysOperationError(
                "SelectedFieldExport source_record must be a RecordRef.",
                field="source_record",
                actual=type(source_record).__name__,
            )
        if not isinstance(source_field, FieldRef):
            raise RemotePhysOperationError(
                "SelectedFieldExport source_field must be a FieldRef.",
                field="source_field",
                actual=type(source_field).__name__,
            )
        if not isinstance(field_value, FieldValue):
            raise RemotePhysOperationError(
                "SelectedFieldExport field_value must be a FieldValue.",
                field="field_value",
                actual=type(field_value).__name__,
            )
        if not isinstance(target, FieldRef):
            raise RemotePhysOperationError(
                "SelectedFieldExport target must be a FieldRef.",
                field="target",
                actual=type(target).__name__,
            )
        if source_field.key not in source_record.fields:
            raise RemotePhysOperationError(
                "SelectedFieldExport source_field is not declared by source_record.",
                field="source_field",
                field_key=str(source_field.key),
                record_id=source_record.record_id,
            )
        if source_record.fields[source_field.key] != source_field:
            raise RemotePhysOperationError(
                "SelectedFieldExport source_field must match source_record.fields.",
                field="source_field",
                field_key=str(source_field.key),
                record_id=source_record.record_id,
            )
        object.__setattr__(self, "source_record", source_record)
        object.__setattr__(self, "source_field", source_field)
        object.__setattr__(self, "field_value", field_value)
        object.__setattr__(self, "target", target)
        object.__setattr__(
            self,
            "metadata_policy",
            _coerce_metadata_policy(metadata_policy),
        )
        object.__setattr__(
            self,
            "codec_name",
            _non_empty_string(codec_name, field="codec_name"),
        )
        object.__setattr__(
            self,
            "codec_request",
            None
            if codec_request is None
            else _non_empty_string(codec_request, field="codec_request"),
        )


SelectedFieldExport.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class ExportSelection:
    """Typed no-write selection output for later save operations.

    Selection evidence is returned in ``OperationResult.output``. It is not a
    durable wire schema and does not imply that targets have been written.
    """

    request: RecordExportRequest
    selected_fields: tuple[SelectedFieldExport, ...]

    def __init__(
        self,
        request: RecordExportRequest,
        selected_fields: Sequence[SelectedFieldExport],
    ) -> None:
        if not isinstance(request, RecordExportRequest):
            raise RemotePhysOperationError(
                "ExportSelection request must be a RecordExportRequest.",
                field="request",
                actual=type(request).__name__,
            )
        fields = _coerce_selected_fields(selected_fields)
        for field in fields:
            if field.source_record != request.source_record:
                raise RemotePhysOperationError(
                    "ExportSelection selected fields must match the request record.",
                    field="selected_fields",
                    record_id=request.source_record.record_id,
                )
        object.__setattr__(self, "request", request)
        object.__setattr__(self, "selected_fields", fields)


ExportSelection.__hash__ = None  # type: ignore[assignment]


class CodecSelectionOperation:
    """Pure ``OperationStep`` that validates export save intent without writes."""

    def __init__(
        self,
        codec_registry: CodecRegistry,
        *,
        name: str = "codec_selection",
    ) -> None:
        if not isinstance(codec_registry, CodecRegistry):
            raise RemotePhysOperationError(
                "CodecSelectionOperation codec_registry must be a CodecRegistry.",
                field="codec_registry",
                actual=type(codec_registry).__name__,
            )
        self._codec_registry = codec_registry
        self._name = _non_empty_string(name, field="name")
        self._contract = OperationContract(
            input_type=RecordExportRequest,
            output_type=ExportSelection,
            mutation_policy=OperationMutationPolicy.PURE,
            failure_modes=(
                "missing_field",
                "invalid_target",
                "unsupported_codec",
                "ambiguous_codec",
                "unsupported_metadata_policy",
                "schema_mismatch",
            ),
        )

    @property
    def name(self) -> str:
        """Operation step name used in pipeline diagnostics."""

        return self._name

    @property
    def contract(self) -> OperationContract:
        """Pure operation contract for no-write codec selection."""

        return self._contract

    def run(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        """Validate targets and codec support, returning selection evidence."""

        if context is not None and not isinstance(context, OperationContext):
            raise RemotePhysOperationError(
                "CodecSelectionOperation context must be an OperationContext.",
                field="context",
                actual=type(context).__name__,
            )
        if not isinstance(input_value, RecordExportRequest):
            raise RemotePhysOperationError(
                "CodecSelectionOperation input_value must be a RecordExportRequest.",
                field="input_value",
                actual=type(input_value).__name__,
            )

        selected = tuple(
            self._select_field(input_value, field_key)
            for field_key in input_value.spec.requested_fields
        )
        selection = ExportSelection(input_value, selected)
        return OperationResult(
            selection,
            operation_name=self.name,
            role=self.contract.role,
            metadata={
                "selected_field_count": len(selection.selected_fields),
                "write_count": 0,
                "link_count": 0,
                "copy_count": 0,
            },
            provenance={
                "source_datasource_id": input_value.source_record.datasource.datasource_id,
                "source_record_id": input_value.source_record.record_id,
            },
        )

    def __call__(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        """Run selection with callable operation-step semantics."""

        return self.run(input_value, context=context)

    def _select_field(
        self,
        request: RecordExportRequest,
        field_key: DataKey,
    ) -> SelectedFieldExport:
        if field_key not in request.source_record.fields:
            raise RemotePhysOperationError(
                "CodecSelectionOperation requested field is absent from the source record.",
                field="source_record.fields",
                field_key=str(field_key),
                record_id=request.source_record.record_id,
            )
        if field_key not in request.field_values:
            raise RemotePhysOperationError(
                "CodecSelectionOperation requested field value is missing.",
                field="field_values",
                field_key=str(field_key),
                record_id=request.source_record.record_id,
            )

        source_field = request.source_record.fields[field_key]
        field_value = request.field_values[field_key]
        target = request.layout.derive_target(
            request.source_record,
            field_key,
            spec=request.spec,
            target=request.target,
        )
        schema_request = request.spec.schema_requests.get(field_key)
        if (
            schema_request is not None
            and field_value.schema is not None
            and field_value.schema != schema_request
        ):
            raise RemotePhysOperationError(
                "CodecSelectionOperation field value schema does not match schema request.",
                field="schema_requests",
                field_key=str(field_key),
                expected=str(schema_request),
                actual=str(field_value.schema),
            )

        context = SaveContext(target, metadata_policy=request.spec.metadata_policy)
        codec = self._codec_registry.resolve_save(field_value, context)
        codec_name = _codec_name(codec)
        codec_request = request.spec.codec_requests.get(field_key)
        if codec_request is not None and codec_request != codec_name:
            raise RemotePhysOperationError(
                "CodecSelectionOperation selected codec does not match codec request.",
                field="codec_requests",
                field_key=str(field_key),
                expected=codec_request,
                actual=codec_name,
            )

        return SelectedFieldExport(
            source_record=request.source_record,
            source_field=source_field,
            field_value=field_value,
            target=target,
            metadata_policy=request.spec.metadata_policy,
            codec_name=codec_name,
            codec_request=codec_request,
        )


class SaveOperation:
    """Side-effecting ``OperationStep`` that saves selected fields via codecs."""

    def __init__(
        self,
        codec_registry: CodecRegistry,
        *,
        name: str = "save",
    ) -> None:
        if not isinstance(codec_registry, CodecRegistry):
            raise RemotePhysOperationError(
                "SaveOperation codec_registry must be a CodecRegistry.",
                field="codec_registry",
                actual=type(codec_registry).__name__,
            )
        self._codec_registry = codec_registry
        self._name = _non_empty_string(name, field="name")
        self._contract = OperationContract(
            input_type=ExportSelection,
            output_type=RecordExportResult,
            mutation_policy=OperationMutationPolicy.SIDE_EFFECTING,
            side_effects=("field_save",),
            failure_modes=(
                "target_conflict",
                "unsupported_materialization",
                "codec_failure",
                "partial_field_failure",
            ),
        )

    @property
    def name(self) -> str:
        """Operation step name used in pipeline diagnostics."""

        return self._name

    @property
    def contract(self) -> OperationContract:
        """Side-effecting operation contract for codec saves."""

        return self._contract

    def run(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        """Save selected fields and return typed record export evidence."""

        if context is not None and not isinstance(context, OperationContext):
            raise RemotePhysOperationError(
                "SaveOperation context must be an OperationContext.",
                field="context",
                actual=type(context).__name__,
            )
        if not isinstance(input_value, ExportSelection):
            raise RemotePhysOperationError(
                "SaveOperation input_value must be an ExportSelection.",
                field="input_value",
                actual=type(input_value).__name__,
            )
        field_results = tuple(
            self._save_field(selection, input_value.request.policy)
            for selection in input_value.selected_fields
        )
        record_result = RecordExportResult(
            input_value.request.source_record,
            field_results,
        )
        return OperationResult(
            record_result,
            operation_name=self.name,
            role=self.contract.role,
            metadata={
                "field_count": record_result.total_count,
                "written_count": record_result.count(FieldExportOutcome.WRITTEN),
                "skipped_count": record_result.count(FieldExportOutcome.SKIPPED),
                "replaced_count": record_result.count(FieldExportOutcome.REPLACED),
                "failed_count": record_result.count(FieldExportOutcome.FAILED),
            },
            provenance={
                "source_datasource_id": input_value.request.source_record.datasource.datasource_id,
                "source_record_id": input_value.request.source_record.record_id,
            },
            side_effect_evidence={
                "field_save": {
                    "attempted": record_result.count(FieldExportOutcome.WRITTEN)
                    + record_result.count(FieldExportOutcome.REPLACED)
                    + record_result.count(FieldExportOutcome.FAILED),
                    "skipped": record_result.count(FieldExportOutcome.SKIPPED),
                }
            },
        )

    def __call__(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        """Run save with callable operation-step semantics."""

        return self.run(input_value, context=context)

    def _save_field(
        self,
        selection: SelectedFieldExport,
        policy: ExportPolicy,
    ) -> FieldExportResult:
        if policy.materialization in {
            ExportMaterialization.LINK,
            ExportMaterialization.COPY,
        }:
            return _link_or_copy_field(selection, policy)

        target_exists = _target_exists(selection.target)
        if target_exists:
            outcome = policy.existing_target_outcome()
            if outcome == FieldExportOutcome.SKIPPED:
                return FieldExportResult(
                    source_record=selection.source_record,
                    source_field=selection.source_field,
                    target=selection.target,
                    outcome=FieldExportOutcome.SKIPPED,
                    source_resources=selection.source_field.resources,
                    target_resources=selection.target.resources,
                    metadata={"codec_name": selection.codec_name},
                )
        else:
            outcome = policy.new_target_outcome()

        save_context = SaveContext(
            selection.target,
            metadata_policy=selection.metadata_policy,
        )
        try:
            codec_result = self._codec_registry.save(selection.field_value, save_context)
        except Exception as exc:
            if not policy.continue_on_field_error:
                raise
            return FieldExportResult(
                source_record=selection.source_record,
                source_field=selection.source_field,
                target=selection.target,
                outcome=FieldExportOutcome.FAILED,
                source_resources=selection.source_field.resources,
                target_resources=selection.target.resources,
                failure=f"{type(exc).__name__}: {exc}",
                metadata={"codec_name": selection.codec_name},
            )

        return FieldExportResult(
            source_record=selection.source_record,
            source_field=selection.source_field,
            target=selection.target,
            outcome=outcome,
            codec_result=codec_result,
            source_resources=selection.source_field.resources,
            target_resources=codec_result.resources,
            metadata={"codec_name": selection.codec_name},
        )


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


def build_sample_artifact_record(
    *,
    sample: Sample,
    source_record: RecordRef,
    locators: Sequence[FieldLocator | str],
    field_refs: Mapping[DataKey | str, FieldRef] | None = None,
) -> RecordRef:
    """Return a descriptor-backed export record for one runtime ``Sample``.

    Existing source fields may be reused from ``source_record``. New derived
    fields, such as prediction fields, must be declared through ``field_refs``.
    The returned descriptor is suitable for ``RecordExportRequest`` and does
    not scan storage, infer target paths, or create a prediction-specific
    datasource.
    """

    if not isinstance(sample, Sample):
        raise RemotePhysOperationError(
            "build_sample_artifact_record requires a Sample.",
            field="sample",
            actual=type(sample).__name__,
        )
    if not isinstance(source_record, RecordRef):
        raise RemotePhysOperationError(
            "build_sample_artifact_record source_record must be a RecordRef.",
            field="source_record",
            actual=type(source_record).__name__,
        )
    requested = _coerce_export_locators(locators)
    provided_refs = _coerce_field_ref_mapping(field_refs)
    fields = dict(source_record.fields)
    for locator in requested:
        if not sample.has(locator):
            raise RemotePhysOperationError(
                "Sample artifact export locator is missing from the sample.",
                field="locators",
                locator=str(locator),
                record_id=source_record.record_id,
            )
        existing = fields.get(locator.key)
        provided = provided_refs.get(locator.key)
        if existing is None:
            if provided is None:
                raise RemotePhysOperationError(
                    "Sample artifact export requires a FieldRef for fields absent from source_record.",
                    field="field_refs",
                    field_key=str(locator.key),
                    locator=str(locator),
                    record_id=source_record.record_id,
                )
            fields[locator.key] = provided
        elif provided is not None and provided != existing:
            raise RemotePhysOperationError(
                "Sample artifact export FieldRef conflicts with source_record.fields.",
                field="field_refs",
                field_key=str(locator.key),
                locator=str(locator),
                record_id=source_record.record_id,
            )
    return RecordRef(
        source_record.datasource,
        source_record.record_id,
        fields,
        metadata={
            **dict(source_record.metadata),
            "sample_artifact.field_count": len(requested),
        },
    )


def sample_artifact_export_request(
    *,
    sample: Sample,
    source_record: RecordRef,
    locators: Sequence[FieldLocator | str],
    target: ExportTarget,
    spec: ExportSpec | None = None,
    field_refs: Mapping[DataKey | str, FieldRef] | None = None,
    layout: OutputLayout | None = None,
    policy: ExportPolicy | None = None,
) -> RecordExportRequest:
    """Build a ``RecordExportRequest`` for one uncollated sample artifact."""

    requested = _coerce_export_locators(locators)
    export_record = build_sample_artifact_record(
        sample=sample,
        source_record=source_record,
        locators=requested,
        field_refs=field_refs,
    )
    field_values = {locator.key: sample.field(locator) for locator in requested}
    resolved_spec = spec if spec is not None else ExportSpec(tuple(field_values))
    if not isinstance(resolved_spec, ExportSpec):
        raise RemotePhysOperationError(
            "sample_artifact_export_request spec must be an ExportSpec.",
            field="spec",
            actual=type(spec).__name__,
        )
    if set(resolved_spec.requested_fields) != set(field_values):
        raise RemotePhysOperationError(
            "sample artifact export spec must match requested sample fields.",
            field="spec",
            expected=sorted(str(field) for field in field_values),
            actual=sorted(str(field) for field in resolved_spec.requested_fields),
        )
    return RecordExportRequest(
        source_record=export_record,
        field_values=field_values,
        spec=resolved_spec,
        target=target,
        layout=layout,
        policy=policy,
    )


def export_record_requests(
    requests: Sequence[RecordExportRequest],
    codec_registry: CodecRegistry,
) -> ExportResult:
    """Run codec selection and save for already assembled record requests.

    This is a narrow multi-record iteration helper over existing export/save
    operations. All requests must share one spec, target, layout, and policy so
    the returned ``ExportResult`` remains the existing aggregate evidence type.
    """

    request_tuple = _coerce_record_export_requests(requests)
    first = request_tuple[0]
    _validate_shared_export_inputs(request_tuple)
    selector = CodecSelectionOperation(codec_registry)
    saver = SaveOperation(codec_registry)
    record_results = []
    for request in request_tuple:
        selection = selector.run(request).output
        record_result = saver.run(selection).output
        record_results.append(record_result)
    return ExportResult(
        spec=first.spec,
        target=first.target,
        layout=first.layout,
        policy=first.policy,
        record_results=record_results,
    )


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


def _coerce_field_values(
    values: Mapping[DataKey | str, FieldValue],
    source_record: RecordRef,
) -> dict[DataKey, FieldValue]:
    if not isinstance(values, Mapping) or not values:
        raise RemotePhysOperationError(
            "RecordExportRequest field_values must be a non-empty mapping.",
            field="field_values",
            actual=type(values).__name__,
        )
    coerced: dict[DataKey, FieldValue] = {}
    for raw_key, value in values.items():
        key = DataKey(raw_key)
        if key not in source_record.fields:
            raise RemotePhysOperationError(
                "RecordExportRequest field_values must reference source_record fields.",
                field="field_values",
                field_key=str(key),
                record_id=source_record.record_id,
            )
        if not isinstance(value, FieldValue):
            raise RemotePhysOperationError(
                "RecordExportRequest field_values must contain FieldValue values.",
                field="field_values",
                field_key=str(key),
                actual=type(value).__name__,
            )
        coerced[key] = value
    return coerced


def _coerce_selected_fields(
    fields: Sequence[SelectedFieldExport],
) -> tuple[SelectedFieldExport, ...]:
    if isinstance(fields, (str, bytes)) or not isinstance(fields, Sequence) or not fields:
        raise RemotePhysOperationError(
            "ExportSelection selected_fields must be a non-empty sequence.",
            field="selected_fields",
            actual=type(fields).__name__,
        )
    coerced = tuple(fields)
    for field in coerced:
        if not isinstance(field, SelectedFieldExport):
            raise RemotePhysOperationError(
                "ExportSelection selected_fields must contain SelectedFieldExport values.",
                field="selected_fields",
                actual=type(field).__name__,
            )
    return coerced


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


def _coerce_record_export_requests(
    requests: Sequence[RecordExportRequest],
) -> tuple[RecordExportRequest, ...]:
    if isinstance(requests, (str, bytes)) or not isinstance(requests, Sequence) or not requests:
        raise RemotePhysOperationError(
            "export_record_requests requires a non-empty sequence.",
            field="requests",
            actual=type(requests).__name__,
        )
    coerced = tuple(requests)
    for request in coerced:
        if not isinstance(request, RecordExportRequest):
            raise RemotePhysOperationError(
                "export_record_requests entries must be RecordExportRequest values.",
                field="requests",
                actual=type(request).__name__,
            )
    return coerced


def _validate_shared_export_inputs(requests: tuple[RecordExportRequest, ...]) -> None:
    first = requests[0]
    for index, request in enumerate(requests[1:], start=1):
        if request.spec != first.spec:
            raise RemotePhysOperationError(
                "export_record_requests requires all requests to share one ExportSpec.",
                field="requests",
                index=index,
            )
        if request.target != first.target:
            raise RemotePhysOperationError(
                "export_record_requests requires all requests to share one ExportTarget.",
                field="requests",
                index=index,
            )
        if request.layout != first.layout:
            raise RemotePhysOperationError(
                "export_record_requests requires all requests to share one OutputLayout.",
                field="requests",
                index=index,
            )
        if request.policy != first.policy:
            raise RemotePhysOperationError(
                "export_record_requests requires all requests to share one ExportPolicy.",
                field="requests",
                index=index,
            )


def _coerce_export_locators(
    locators: Sequence[FieldLocator | str],
) -> tuple[FieldLocator, ...]:
    if isinstance(locators, (str, bytes)) or not isinstance(locators, Sequence) or not locators:
        raise RemotePhysOperationError(
            "Sample artifact export locators must be a non-empty sequence.",
            field="locators",
            actual=type(locators).__name__,
        )
    resolved = tuple(
        FieldLocator.parse(locator) if isinstance(locator, str) else locator
        for locator in locators
    )
    seen_locators: set[FieldLocator] = set()
    seen_keys: set[DataKey] = set()
    for locator in resolved:
        if not isinstance(locator, FieldLocator):
            raise RemotePhysOperationError(
                "Sample artifact export locators must contain FieldLocator values.",
                field="locators",
                actual=type(locator).__name__,
            )
        if locator.metadata_key is not None:
            raise RemotePhysOperationError(
                "Sample artifact export locators must address fields, not metadata selectors.",
                field="locators",
                locator=str(locator),
            )
        if locator in seen_locators:
            raise RemotePhysOperationError(
                "Sample artifact export locators must not contain duplicates.",
                field="locators",
                locator=str(locator),
            )
        if locator.key in seen_keys:
            raise RemotePhysOperationError(
                "Sample artifact export locators must not duplicate data keys.",
                field="locators",
                field_key=str(locator.key),
            )
        seen_locators.add(locator)
        seen_keys.add(locator.key)
    return resolved


def _coerce_field_ref_mapping(
    values: Mapping[DataKey | str, FieldRef] | None,
) -> dict[DataKey, FieldRef]:
    if values is None:
        return {}
    if not isinstance(values, Mapping):
        raise RemotePhysOperationError(
            "Sample artifact field_refs must be a mapping.",
            field="field_refs",
            actual=type(values).__name__,
        )
    refs: dict[DataKey, FieldRef] = {}
    for raw_key, field_ref in values.items():
        key = DataKey(raw_key)
        if not isinstance(field_ref, FieldRef):
            raise RemotePhysOperationError(
                "Sample artifact field_refs must contain FieldRef values.",
                field="field_refs",
                field_key=str(key),
                actual=type(field_ref).__name__,
            )
        if field_ref.key != key:
            raise RemotePhysOperationError(
                "Sample artifact field_refs keys must match FieldRef.key.",
                field="field_refs",
                expected=str(key),
                actual=str(field_ref.key),
            )
        refs[key] = field_ref
    return refs


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


def _non_empty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysOperationError(
            "Export operation strings must be non-empty.",
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


def _target_exists(target: FieldRef) -> bool:
    return any(
        path.exists()
        for resource in target.resources
        if (path := _local_path(resource)) is not None
    )


def _link_or_copy_field(
    selection: SelectedFieldExport,
    policy: ExportPolicy,
) -> FieldExportResult:
    source_resources, target_resources = _resource_lineage_pairs(selection)
    target_exists = any(_require_local_path(resource).exists() for resource in target_resources)
    replaced = False
    if target_exists:
        outcome = policy.existing_target_outcome()
        if outcome == FieldExportOutcome.SKIPPED:
            return FieldExportResult(
                source_record=selection.source_record,
                source_field=selection.source_field,
                target=selection.target,
                outcome=FieldExportOutcome.SKIPPED,
                source_resources=source_resources,
                target_resources=target_resources,
                metadata={"codec_name": selection.codec_name},
            )
        replaced = True
        for resource in target_resources:
            _remove_local_target(resource)

    if policy.materialization == ExportMaterialization.COPY:
        _copy_local_resources(source_resources, target_resources)
        outcome = FieldExportOutcome.REPLACED if replaced else FieldExportOutcome.COPIED
    else:
        copied = _link_local_resources(
            source_resources,
            target_resources,
            allow_copy_fallback=policy.allow_link_copy_fallback,
        )
        if copied:
            outcome = FieldExportOutcome.COPIED
        else:
            outcome = FieldExportOutcome.REPLACED if replaced else FieldExportOutcome.LINKED

    return FieldExportResult(
        source_record=selection.source_record,
        source_field=selection.source_field,
        target=selection.target,
        outcome=outcome,
        source_resources=source_resources,
        target_resources=target_resources,
        metadata={"codec_name": selection.codec_name},
    )


def _resource_lineage_pairs(
    selection: SelectedFieldExport,
) -> tuple[tuple[ResourceRef, ...], tuple[ResourceRef, ...]]:
    source_resources = selection.source_field.resources
    target_resources = selection.target.resources
    if not source_resources:
        raise RemotePhysOperationError(
            "Link/copy export requires source ResourceRef lineage.",
            field="source_resources",
            field_key=str(selection.source_field.key),
        )
    if len(source_resources) != len(target_resources):
        raise RemotePhysOperationError(
            "Link/copy export requires ordered one-to-one source/target resources.",
            field="resources",
            field_key=str(selection.source_field.key),
            source_count=len(source_resources),
            target_count=len(target_resources),
        )
    for source, target in zip(source_resources, target_resources, strict=True):
        _validate_local_resource_pair(source, target)
    return source_resources, target_resources


def _validate_local_resource_pair(source: ResourceRef, target: ResourceRef) -> None:
    if source.protocol != target.protocol:
        raise RemotePhysOperationError(
            "Link/copy export does not support cross-protocol resources.",
            field="resources",
            source_protocol=source.protocol,
            target_protocol=target.protocol,
        )
    if source.protocol != "file":
        raise RemotePhysOperationError(
            "Link/copy export supports only local file resources in Stage 8.",
            field="resources",
            protocol=source.protocol,
        )


def _copy_local_resources(
    sources: tuple[ResourceRef, ...],
    targets: tuple[ResourceRef, ...],
) -> None:
    for source, target in zip(sources, targets, strict=True):
        source_path = _require_local_path(source)
        target_path = _require_local_path(target)
        if not source_path.exists():
            raise RemotePhysOperationError(
                "Copy export source path does not exist.",
                field="source_resources",
                source_uri=source.uri,
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)


def _link_local_resources(
    sources: tuple[ResourceRef, ...],
    targets: tuple[ResourceRef, ...],
    *,
    allow_copy_fallback: bool,
) -> bool:
    copied = False
    for source, target in zip(sources, targets, strict=True):
        source_path = _require_local_path(source)
        target_path = _require_local_path(target)
        if not source_path.exists():
            raise RemotePhysOperationError(
                "Link export source path does not exist.",
                field="source_resources",
                source_uri=source.uri,
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(source_path, target_path)
        except OSError as exc:
            if not allow_copy_fallback:
                raise RemotePhysOperationError(
                    "Link export failed and copy fallback is not enabled.",
                    field="allow_link_copy_fallback",
                    source_uri=source.uri,
                    target_uri=target.uri,
                ) from exc
            shutil.copy2(source_path, target_path)
            copied = True
    return copied


def _remove_local_target(resource: ResourceRef) -> None:
    path = _require_local_path(resource)
    if path.is_dir() and not path.is_symlink():
        raise RemotePhysOperationError(
            "Replace idempotency cannot remove directory targets.",
            field="target_resources",
            target_uri=resource.uri,
        )
    if path.exists() or path.is_symlink():
        path.unlink()


def _require_local_path(resource: ResourceRef) -> Path:
    path = _local_path(resource)
    if path is None:
        raise RemotePhysOperationError(
            "Local filesystem path is required for link/copy export.",
            field="resources",
            protocol=resource.protocol,
            uri=resource.uri,
        )
    return path


def _local_path(resource: ResourceRef) -> Path | None:
    if resource.protocol != "file":
        return None
    parsed = urlparse(resource.uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(resource.uri)


def _codec_name(codec: object) -> str:
    explicit_name = getattr(codec, "name", None)
    if isinstance(explicit_name, str) and explicit_name:
        return explicit_name
    return codec.__class__.__name__


def _thaw_for_json(value: FrozenPrimitive) -> object:
    if isinstance(value, Mapping):
        return {
            key: _thaw_for_json(value[key])
            for key in sorted(value)
        }
    if isinstance(value, tuple):
        return [_thaw_for_json(item) for item in value]
    return thaw_primitive(value)
