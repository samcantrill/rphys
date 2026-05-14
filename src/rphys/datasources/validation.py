"""Descriptor-only datasource validation reports and IO policy.

Validation consumes ``DataSourceScanResult`` descriptor output and emits
primitive, inspectable issue records. IO is opt-in by policy: descriptor-only
checks run under ``no_io``; probe and full validation IO requests must be
declared explicitly and are rejected otherwise.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Self

from rphys.data.keys import DataKey
from rphys.data.metadata import MetadataKey
from rphys.errors import InvalidDataSourceValidationError
from rphys.io._primitives import (
    FrozenPrimitive,
    freeze_primitive,
    thaw_primitive,
)

from .adapters import DataSourceScanResult, DataSourceSpec
from .refs import DataSourceRef

__all__ = [
    "DataSourceValidationReport",
    "ValidationIOPolicy",
    "ValidationIssue",
    "validate_scan_result",
]

_Severity = Literal["warning", "error"]
_Scope = Literal["datasource", "record", "field", "resource", "schema", "metadata", "io"]


@dataclass(frozen=True, init=False, slots=True)
class ValidationIOPolicy:
    """Explicit validation IO mode.

    ``no_io`` allows only descriptor checks. ``probe_only`` allows lightweight
    resource probes but not full payload validation. ``explicit_validation_io``
    is the only mode that can authorize full validation IO; Stage 5 still does
    not implement hidden payload loading.
    """

    mode: str

    def __init__(self, mode: str) -> None:
        if mode not in {"no_io", "probe_only", "explicit_validation_io"}:
            raise InvalidDataSourceValidationError(
                "Unsupported datasource validation IO policy.",
                field="mode",
                actual=mode,
                supported=["no_io", "probe_only", "explicit_validation_io"],
            )
        object.__setattr__(self, "mode", mode)

    @classmethod
    def no_io(cls) -> Self:
        """Create a descriptor-only validation policy."""

        return cls("no_io")

    @classmethod
    def probe_only(cls) -> Self:
        """Create a policy allowing explicit lightweight probes."""

        return cls("probe_only")

    @classmethod
    def explicit_validation_io(cls) -> Self:
        """Create a policy allowing explicitly requested validation IO."""

        return cls("explicit_validation_io")

    @property
    def allows_probe(self) -> bool:
        """Whether explicit resource probes are allowed."""

        return self.mode in {"probe_only", "explicit_validation_io"}

    @property
    def allows_validation_io(self) -> bool:
        """Whether explicit full validation IO is allowed."""

        return self.mode == "explicit_validation_io"

    def require_allowed(self, *, probe: bool = False, validation_io: bool = False) -> None:
        """Raise when requested IO exceeds this policy."""

        if validation_io and not self.allows_validation_io:
            raise InvalidDataSourceValidationError(
                "Datasource validation IO must be explicitly enabled.",
                field="policy",
                policy=self.mode,
                requested="validation_io",
            )
        if probe and not self.allows_probe:
            raise InvalidDataSourceValidationError(
                "Datasource validation probes must be explicitly enabled.",
                field="policy",
                policy=self.mode,
                requested="probe",
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the policy mode."""

        return {"mode": self.mode}

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a policy from primitive values."""

        if not isinstance(value, Mapping) or set(value) != {"mode"}:
            raise InvalidDataSourceValidationError(
                "Serialized ValidationIOPolicy must contain only mode.",
                field="policy",
                actual=type(value).__name__,
            )
        return cls(value["mode"])  # type: ignore[arg-type]


@dataclass(frozen=True, init=False, slots=True)
class ValidationIssue:
    """Primitive diagnostic produced by datasource validation.

    ``code`` values are provisional diagnostic strings. ``scope`` identifies
    the descriptor layer where evidence was found; optional IDs keep datasource,
    record, and field context inspectable without loading payloads.
    """

    code: str
    message: str
    severity: _Severity
    scope: _Scope
    datasource_id: str | None
    record_id: str | None
    field_key: DataKey | None
    context: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        code: str,
        message: str,
        *,
        severity: _Severity,
        scope: _Scope,
        datasource_id: str | None = None,
        record_id: str | None = None,
        field_key: DataKey | str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "code", _non_empty_string(code, field="code"))
        object.__setattr__(self, "message", _non_empty_string(message, field="message"))
        if severity not in {"warning", "error"}:
            raise InvalidDataSourceValidationError(
                "ValidationIssue severity must be warning or error.",
                field="severity",
                actual=severity,
            )
        object.__setattr__(self, "severity", severity)
        if scope not in {
            "datasource",
            "record",
            "field",
            "resource",
            "schema",
            "metadata",
            "io",
        }:
            raise InvalidDataSourceValidationError(
                "ValidationIssue scope is unsupported.",
                field="scope",
                actual=scope,
            )
        object.__setattr__(self, "scope", scope)
        object.__setattr__(
            self,
            "datasource_id",
            _optional_string(datasource_id, field="datasource_id"),
        )
        object.__setattr__(
            self,
            "record_id",
            _optional_string(record_id, field="record_id"),
        )
        object.__setattr__(
            self,
            "field_key",
            DataKey(field_key) if field_key is not None else None,
        )
        object.__setattr__(
            self,
            "context",
            MappingProxyType(_coerce_context(context)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the issue as primitive validation evidence."""

        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "scope": self.scope,
            "datasource_id": self.datasource_id,
            "record_id": self.record_id,
            "field_key": str(self.field_key) if self.field_key is not None else None,
            "context": {
                key: thaw_primitive(value)
                for key, value in self.context.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct an issue from primitive values."""

        if not isinstance(value, Mapping):
            raise InvalidDataSourceValidationError(
                "Serialized ValidationIssue must be a mapping.",
                field="issue",
                actual=type(value).__name__,
            )
        _require_keys(
            value,
            {
                "code",
                "message",
                "severity",
                "scope",
                "datasource_id",
                "record_id",
                "field_key",
                "context",
            },
            descriptor="ValidationIssue",
        )
        return cls(
            value["code"],  # type: ignore[arg-type]
            value["message"],  # type: ignore[arg-type]
            severity=value["severity"],  # type: ignore[arg-type]
            scope=value["scope"],  # type: ignore[arg-type]
            datasource_id=value["datasource_id"],  # type: ignore[arg-type]
            record_id=value["record_id"],  # type: ignore[arg-type]
            field_key=value["field_key"],  # type: ignore[arg-type]
            context=value["context"],  # type: ignore[arg-type]
        )


ValidationIssue.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class DataSourceValidationReport:
    """Validation summary for one descriptor-only scan result."""

    datasource: DataSourceRef
    policy: ValidationIOPolicy
    issues: tuple[ValidationIssue, ...]
    record_count: int
    field_count: int
    rejected_record_ids: Mapping[str, str]
    validation_evidence: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        datasource: DataSourceRef,
        *,
        policy: ValidationIOPolicy,
        issues: Sequence[ValidationIssue] = (),
        record_count: int = 0,
        field_count: int = 0,
        rejected_record_ids: Mapping[str, str] | None = None,
        validation_evidence: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(datasource, DataSourceRef):
            raise InvalidDataSourceValidationError(
                "DataSourceValidationReport datasource must be a DataSourceRef.",
                field="datasource",
                actual=type(datasource).__name__,
            )
        if not isinstance(policy, ValidationIOPolicy):
            raise InvalidDataSourceValidationError(
                "DataSourceValidationReport policy must be a ValidationIOPolicy.",
                field="policy",
                actual=type(policy).__name__,
            )
        object.__setattr__(self, "datasource", datasource)
        object.__setattr__(self, "policy", policy)
        object.__setattr__(self, "issues", _coerce_issues(issues))
        object.__setattr__(
            self,
            "record_count",
            _non_negative_int(record_count, field="record_count"),
        )
        object.__setattr__(
            self,
            "field_count",
            _non_negative_int(field_count, field="field_count"),
        )
        object.__setattr__(
            self,
            "rejected_record_ids",
            MappingProxyType(_coerce_rejections(rejected_record_ids)),
        )
        object.__setattr__(
            self,
            "validation_evidence",
            MappingProxyType(_coerce_context(validation_evidence)),
        )

    @property
    def passed(self) -> bool:
        """Whether the report contains no error-severity issues."""

        return not self.errors

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        """Error-severity validation issues."""

        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        """Warning-severity validation issues."""

        return tuple(issue for issue in self.issues if issue.severity == "warning")

    def to_dict(self) -> dict[str, object]:
        """Serialize report evidence without payloads or stable code enums."""

        return {
            "datasource": self.datasource.to_dict(),
            "policy": self.policy.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "record_count": self.record_count,
            "field_count": self.field_count,
            "rejected_record_ids": dict(self.rejected_record_ids),
            "validation_evidence": {
                key: thaw_primitive(value)
                for key, value in self.validation_evidence.items()
            },
        }


DataSourceValidationReport.__hash__ = None  # type: ignore[assignment]


def validate_scan_result(
    scan_result: DataSourceScanResult,
    *,
    spec: DataSourceSpec | None = None,
    policy: ValidationIOPolicy | None = None,
    required_fields: Sequence[DataKey | str] | None = None,
    required_metadata: Sequence[MetadataKey | str] = (),
    require_probe: bool = False,
    require_validation_io: bool = False,
) -> DataSourceValidationReport:
    """Validate descriptor-only scan evidence.

    The function checks scan structure, missing declared fields, missing
    requested metadata, scan warnings, and rejected IDs. It never probes or
    loads resources itself; ``require_probe`` and ``require_validation_io`` are
    explicit guardrails used to reject hidden IO under restrictive policies.
    """

    if not isinstance(scan_result, DataSourceScanResult):
        raise InvalidDataSourceValidationError(
            "validate_scan_result requires a DataSourceScanResult.",
            field="scan_result",
            actual=type(scan_result).__name__,
        )
    if spec is not None and not isinstance(spec, DataSourceSpec):
        raise InvalidDataSourceValidationError(
            "validate_scan_result spec must be a DataSourceSpec.",
            field="spec",
            actual=type(spec).__name__,
        )
    if spec is not None and spec.datasource.datasource_id != scan_result.datasource.datasource_id:
        raise InvalidDataSourceValidationError(
            "Validation spec datasource_id must match scan datasource_id.",
            field="spec",
            expected=scan_result.datasource.datasource_id,
            actual=spec.datasource.datasource_id,
        )

    selected_policy = policy or ValidationIOPolicy.no_io()
    if not isinstance(selected_policy, ValidationIOPolicy):
        raise InvalidDataSourceValidationError(
            "validate_scan_result policy must be a ValidationIOPolicy.",
            field="policy",
            actual=type(selected_policy).__name__,
        )
    selected_policy.require_allowed(
        probe=require_probe,
        validation_io=require_validation_io,
    )

    requested_fields = _required_fields(
        required_fields=required_fields,
        spec=spec,
        datasource=scan_result.datasource,
    )
    requested_metadata = _metadata_keys(required_metadata)
    issues: list[ValidationIssue] = []

    if not scan_result.records:
        issues.append(
            _issue(
                "records.empty",
                "Datasource scan produced no accepted records.",
                severity="error",
                scope="record",
                datasource=scan_result.datasource,
            )
        )

    if scan_result.datasource.source is None:
        issues.append(
            _issue(
                "datasource.source_missing",
                "Datasource descriptor does not declare a source resource.",
                severity="warning",
                scope="resource",
                datasource=scan_result.datasource,
            )
        )
    if scan_result.datasource.schema is None:
        issues.append(
            _issue(
                "schema.missing",
                "Datasource descriptor does not declare a schema.",
                severity="warning",
                scope="schema",
                datasource=scan_result.datasource,
            )
        )

    for warning in scan_result.warnings:
        issues.append(
            _issue(
                "scan.warning",
                warning,
                severity="warning",
                scope="datasource",
                datasource=scan_result.datasource,
            )
        )

    for record_id, reason in scan_result.rejected_record_ids.items():
        issues.append(
            _issue(
                "record.rejected",
                reason,
                severity="error",
                scope="record",
                datasource=scan_result.datasource,
                record_id=record_id,
            )
        )

    for record in scan_result.records:
        for field_key in requested_fields:
            if field_key not in record.fields:
                issues.append(
                    _issue(
                        "field.missing",
                        "Record is missing a required field.",
                        severity="error",
                        scope="field",
                        datasource=scan_result.datasource,
                        record_id=record.record_id,
                        field_key=field_key,
                    )
                )
        for metadata_key in requested_metadata:
            if metadata_key not in record.metadata:
                issues.append(
                    _issue(
                        "metadata.missing",
                        "Record is missing required metadata.",
                        severity="error",
                        scope="metadata",
                        datasource=scan_result.datasource,
                        record_id=record.record_id,
                        context={"metadata_key": str(metadata_key)},
                    )
                )

    return DataSourceValidationReport(
        scan_result.datasource,
        policy=selected_policy,
        issues=tuple(issues),
        record_count=len(scan_result.records),
        field_count=sum(len(record.fields) for record in scan_result.records),
        rejected_record_ids=scan_result.rejected_record_ids,
        validation_evidence=scan_result.validation_evidence,
    )


def _required_fields(
    *,
    required_fields: Sequence[DataKey | str] | None,
    spec: DataSourceSpec | None,
    datasource: DataSourceRef,
) -> tuple[DataKey, ...]:
    if required_fields is not None:
        return _data_keys(required_fields)
    if spec is not None and spec.required_fields:
        return spec.required_fields
    if datasource.schema is not None:
        return tuple(datasource.schema.fields)
    return ()


def _data_keys(values: Sequence[DataKey | str]) -> tuple[DataKey, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidDataSourceValidationError(
            "required_fields must be a sequence.",
            field="required_fields",
            actual=type(values).__name__,
        )
    return tuple(DataKey(value) for value in values)


def _metadata_keys(values: Sequence[MetadataKey | str]) -> tuple[MetadataKey, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidDataSourceValidationError(
            "required_metadata must be a sequence.",
            field="required_metadata",
            actual=type(values).__name__,
        )
    return tuple(MetadataKey(value) for value in values)


def _issue(
    code: str,
    message: str,
    *,
    severity: _Severity,
    scope: _Scope,
    datasource: DataSourceRef,
    record_id: str | None = None,
    field_key: DataKey | str | None = None,
    context: Mapping[str, object] | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        code,
        message,
        severity=severity,
        scope=scope,
        datasource_id=datasource.datasource_id,
        record_id=record_id,
        field_key=field_key,
        context=context,
    )


def _coerce_issues(values: Sequence[ValidationIssue]) -> tuple[ValidationIssue, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidDataSourceValidationError(
            "Validation report issues must be a sequence.",
            field="issues",
            actual=type(values).__name__,
        )
    issues = tuple(values)
    for issue in issues:
        if not isinstance(issue, ValidationIssue):
            raise InvalidDataSourceValidationError(
                "Validation report issues must contain ValidationIssue values.",
                field="issues",
                actual=type(issue).__name__,
            )
    return issues


def _coerce_context(value: Mapping[str, object] | None) -> dict[str, FrozenPrimitive]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidDataSourceValidationError(
            "Validation context must be a mapping.",
            field="context",
            actual=type(value).__name__,
        )
    context: dict[str, FrozenPrimitive] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise InvalidDataSourceValidationError(
                "Validation context keys must be non-empty strings.",
                field="context",
                key=key,
            )
        context[key] = freeze_primitive(
            item,
            error_type=InvalidDataSourceValidationError,
            field="context",
        )
    return context


def _coerce_rejections(value: Mapping[str, str] | None) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise InvalidDataSourceValidationError(
            "Validation report rejected_record_ids must be a mapping.",
            field="rejected_record_ids",
            actual=type(value).__name__,
        )
    return {
        _non_empty_string(record_id, field="record_id"): _non_empty_string(
            reason,
            field="reason",
        )
        for record_id, reason in value.items()
    }


def _non_empty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidDataSourceValidationError(
            "Validation descriptor fields must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value


def _optional_string(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    return _non_empty_string(value, field=field)


def _non_negative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InvalidDataSourceValidationError(
            "Validation report counts must be non-negative integers.",
            field=field,
            actual=type(value).__name__,
            value=value,
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
        raise InvalidDataSourceValidationError(
            "Serialized validation keys do not match the Stage 5 schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )
