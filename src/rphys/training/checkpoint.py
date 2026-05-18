"""Dependency-light checkpoint contracts for policy, ref, and selector evidence."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from rphys.errors import RemotePhysTrainingError

from ._validation import (
    PrimitiveMapping,
    coerce_non_negative_int,
    coerce_optional_positive_int,
    freeze_primitive_mapping,
)

__all__ = [
    "CheckpointCatalog",
    "CheckpointPruneEvidence",
    "CheckpointPrunePolicy",
    "CheckpointRef",
    "CheckpointRefStatus",
    "CheckpointRetentionReason",
    "CheckpointRestoreMode",
    "CheckpointRestorePolicy",
    "CheckpointRestoreResult",
    "CheckpointResultStatus",
    "CheckpointSavePolicy",
    "CheckpointSaveResult",
    "CheckpointSelection",
    "CheckpointSelectionMode",
    "CheckpointSelectionResult",
    "CheckpointPruneResult",
]


class CheckpointRefStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    UNKNOWN = "unknown"

    @classmethod
    def coerce(cls, value: "CheckpointRefStatus | str") -> "CheckpointRefStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint reference status.",
                    owner="CheckpointRefStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointRefStatus must be a CheckpointRefStatus or string.",
            owner="CheckpointRefStatus",
            field="status",
            expected="CheckpointRefStatus | str",
            actual=type(value).__name__,
        )


class CheckpointMetricDirection(StrEnum):
    MIN = "min"
    MAX = "max"

    @classmethod
    def coerce(cls, value: "CheckpointMetricDirection | str | None") -> "CheckpointMetricDirection | None":
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint metric direction.",
                    owner="CheckpointMetricDirection",
                    field="direction",
                    expected=tuple(direction.value for direction in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointMetricDirection must be a CheckpointMetricDirection, string, or None.",
            owner="CheckpointMetricDirection",
            field="direction",
            expected="CheckpointMetricDirection | str | None",
            actual=type(value).__name__,
        )


class CheckpointSelectionMode(StrEnum):
    LATEST_COMPLETED = "latest_completed"
    BEST_BY_METRIC = "best_by_metric"
    N_EPOCHS_BACK = "n_epochs_back"
    N_STEPS_BACK = "n_steps_back"
    BEFORE_TIMESTAMP = "before_timestamp"
    AFTER_TIMESTAMP = "after_timestamp"
    FAILURE = "failure"
    FINAL = "final"
    EXPLICIT = "explicit"

    @classmethod
    def coerce(cls, value: "CheckpointSelectionMode | str") -> "CheckpointSelectionMode":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint selection mode.",
                    owner="CheckpointSelectionMode",
                    field="mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointSelectionMode must be a CheckpointSelectionMode or string.",
            owner="CheckpointSelectionMode",
            field="mode",
            expected="CheckpointSelectionMode | str",
            actual=type(value).__name__,
        )


class CheckpointResultStatus(StrEnum):
    ATTEMPTED = "attempted"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"
    UNAVAILABLE = "unavailable"

    @classmethod
    def coerce(cls, value: "CheckpointResultStatus | str") -> "CheckpointResultStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint result status.",
                    owner="CheckpointResultStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointResultStatus must be a CheckpointResultStatus or string.",
            owner="CheckpointResultStatus",
            field="status",
            expected="CheckpointResultStatus | str",
            actual=type(value).__name__,
        )


class CheckpointRetentionReason(StrEnum):
    RETAIN_RECENT = "retain_recent"
    RETAIN_BEST = "retain_best"
    RETAIN_FINAL = "retain_final"
    RETAIN_FAILURE = "retain_failure"
    DROP_AGE = "drop_age"
    DROP_DUPLICATE = "drop_duplicate"
    DROP_EXPLICIT = "drop_explicit"
    NONE = "none"

    @classmethod
    def coerce(cls, value: "CheckpointRetentionReason | str") -> "CheckpointRetentionReason":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint retention reason.",
                    owner="CheckpointRetentionReason",
                    field="reason",
                    expected=tuple(reason.value for reason in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointRetentionReason must be a CheckpointRetentionReason or string.",
            owner="CheckpointRetentionReason",
            field="reason",
            expected="CheckpointRetentionReason | str",
            actual=type(value).__name__,
        )


class CheckpointRestoreMode(StrEnum):
    EXPRESSION = "expression"
    CATALOG = "catalog"
    EXPLICIT = "explicit"

    @classmethod
    def coerce(cls, value: "CheckpointRestoreMode | str") -> "CheckpointRestoreMode":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported checkpoint restore mode.",
                    owner="CheckpointRestoreMode",
                    field="mode",
                    expected=tuple(mode.value for mode in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "CheckpointRestoreMode must be a CheckpointRestoreMode or string.",
            owner="CheckpointRestoreMode",
            field="mode",
            expected="CheckpointRestoreMode | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class CheckpointRef:
    """Checkpoint evidence pointer independent of any store or runtime backend."""

    ref_id: str
    stream_id: str | None
    run_id: str | None
    timeline_id: str | None
    path: str | None
    uri: str | None
    epoch: int | None
    step: int | None
    timestamp: float | None
    sequence_id: int | None
    is_final: bool
    is_failure: bool
    status: CheckpointRefStatus
    metric_name: str | None
    metric_direction: CheckpointMetricDirection | None
    metric_value: float | None
    metadata: PrimitiveMapping

    def __init__(
        self,
        ref_id: str,
        *,
        stream_id: str | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        path: str | None = None,
        uri: str | None = None,
        epoch: int | None = None,
        step: int | None = None,
        timestamp: float | None = None,
        sequence_id: int | None = None,
        is_final: bool = False,
        is_failure: bool = False,
        status: CheckpointRefStatus | str = CheckpointRefStatus.PENDING,
        metric_name: str | None = None,
        metric_direction: CheckpointMetricDirection | str | None = None,
        metric_value: float | None = None,
        metadata: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "ref_id",
            _coerce_name(ref_id, owner="CheckpointRef", field="ref_id"),
        )
        object.__setattr__(
            self,
            "stream_id",
            _coerce_optional_name(stream_id, owner="CheckpointRef", field="stream_id"),
        )
        object.__setattr__(
            self,
            "run_id",
            _coerce_optional_name(run_id, owner="CheckpointRef", field="run_id"),
        )
        object.__setattr__(
            self,
            "timeline_id",
            _coerce_optional_name(timeline_id, owner="CheckpointRef", field="timeline_id"),
        )
        object.__setattr__(
            self,
            "path",
            _coerce_optional_name(path, owner="CheckpointRef", field="path"),
        )
        object.__setattr__(
            self,
            "uri",
            _coerce_optional_name(uri, owner="CheckpointRef", field="uri"),
        )
        object.__setattr__(
            self,
            "epoch",
            coerce_non_negative_int(epoch, owner="CheckpointRef", field="epoch") if epoch is not None else None,
        )
        object.__setattr__(
            self,
            "step",
            coerce_non_negative_int(step, owner="CheckpointRef", field="step") if step is not None else None,
        )
        if sequence_id is not None:
            sequence_id = coerce_non_negative_int(sequence_id, owner="CheckpointRef", field="sequence_id")
        object.__setattr__(self, "sequence_id", sequence_id)
        object.__setattr__(self, "status", CheckpointRefStatus.coerce(status))
        object.__setattr__(self, "is_final", _coerce_bool(is_final, owner="CheckpointRef", field="is_final"))
        object.__setattr__(self, "is_failure", _coerce_bool(is_failure, owner="CheckpointRef", field="is_failure"))
        object.__setattr__(
            self,
            "metric_name",
            _coerce_optional_name(metric_name, owner="CheckpointRef", field="metric_name"),
        )
        metric_direction = CheckpointMetricDirection.coerce(metric_direction)
        object.__setattr__(
            self,
            "metric_direction",
            metric_direction,
        )
        if metric_value is not None:
            metric_value = _coerce_finite_float(metric_value, owner="CheckpointRef", field="metric_value")
            if metric_name is None:
                raise RemotePhysTrainingError(
                    "CheckpointRef metric_value requires metric_name.",
                    owner="CheckpointRef",
                    field="metric_value",
                    metric_name=metric_name,
                )
            if metric_direction is None:
                raise RemotePhysTrainingError(
                    "CheckpointRef metric_value requires metric_direction.",
                    owner="CheckpointRef",
                    field="metric_value",
                    metric_direction=metric_direction,
                )
        object.__setattr__(self, "metric_value", metric_value)
        if metric_name is None and metric_direction is not None:
            raise RemotePhysTrainingError(
                "CheckpointRef metric_direction requires metric_name.",
                owner="CheckpointRef",
                field="metric_direction",
                metric_name=metric_name,
            )
        if timestamp is not None:
            timestamp = _coerce_finite_float(timestamp, owner="CheckpointRef", field="timestamp")
            if timestamp < 0:
                raise RemotePhysTrainingError(
                    "CheckpointRef timestamp must be non-negative.",
                    owner="CheckpointRef",
                    field="timestamp",
                    actual=timestamp,
                )
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "metadata", freeze_primitive_mapping(metadata, owner="CheckpointRef", field="metadata"))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointSavePolicy:
    """Checkpoint persistence cadence and intent."""

    enabled: bool
    by_step: int | None
    by_epoch: int | None
    by_elapsed_seconds: float | None
    on_metric: bool
    metric_name: str | None
    metric_direction: CheckpointMetricDirection | None
    metric_threshold: float | None
    on_failure: bool
    on_final: bool

    def __init__(
        self,
        *,
        enabled: bool = True,
        by_step: int | None = None,
        by_epoch: int | None = None,
        by_elapsed_seconds: float | None = None,
        on_metric: bool = False,
        metric_name: str | None = None,
        metric_direction: CheckpointMetricDirection | str | None = None,
        metric_threshold: float | None = None,
        on_failure: bool = False,
        on_final: bool = True,
    ) -> None:
        object.__setattr__(self, "enabled", _coerce_bool(enabled, owner="CheckpointSavePolicy", field="enabled"))
        object.__setattr__(
            self,
            "by_step",
            coerce_optional_positive_int(by_step, owner="CheckpointSavePolicy", field="by_step"),
        )
        object.__setattr__(
            self,
            "by_epoch",
            coerce_optional_positive_int(by_epoch, owner="CheckpointSavePolicy", field="by_epoch"),
        )
        if by_elapsed_seconds is not None:
            by_elapsed_seconds = _coerce_positive_float(
                by_elapsed_seconds,
                owner="CheckpointSavePolicy",
                field="by_elapsed_seconds",
            )
        object.__setattr__(self, "by_elapsed_seconds", by_elapsed_seconds)
        object.__setattr__(self, "on_metric", _coerce_bool(on_metric, owner="CheckpointSavePolicy", field="on_metric"))
        object.__setattr__(
            self,
            "metric_name",
            _coerce_optional_name(metric_name, owner="CheckpointSavePolicy", field="metric_name"),
        )
        metric_direction = CheckpointMetricDirection.coerce(metric_direction)
        object.__setattr__(self, "metric_direction", metric_direction)
        if metric_threshold is not None:
            metric_threshold = _coerce_finite_float(metric_threshold, owner="CheckpointSavePolicy", field="metric_threshold")
        object.__setattr__(self, "metric_threshold", metric_threshold)
        if on_metric and self.metric_name is None:
            raise RemotePhysTrainingError(
                "CheckpointSavePolicy requires metric_name when on_metric is true.",
                owner="CheckpointSavePolicy",
                field="metric_name",
            )
        if on_metric and metric_direction is None:
            raise RemotePhysTrainingError(
                "CheckpointSavePolicy requires metric_direction when on_metric is true.",
                owner="CheckpointSavePolicy",
                field="metric_direction",
            )
        if not enabled and any(
            value is not None for value in (by_step, by_epoch, by_elapsed_seconds, on_metric, on_failure)
        ):
            raise RemotePhysTrainingError(
                "CheckpointSavePolicy cannot configure triggers when disabled.",
                owner="CheckpointSavePolicy",
                field="enabled",
                value=enabled,
            )
        if not enabled and not on_final:
            raise RemotePhysTrainingError(
                "CheckpointSavePolicy disabled checkpoints should keep final behavior explicit.",
                owner="CheckpointSavePolicy",
                field="on_final",
                value=on_final,
            )
        if not any((by_step, by_epoch, by_elapsed_seconds, on_metric, on_failure, on_final)):
            raise RemotePhysTrainingError(
                "CheckpointSavePolicy must specify at least one save trigger.",
                owner="CheckpointSavePolicy",
                field="triggers",
            )
        object.__setattr__(self, "on_failure", _coerce_bool(on_failure, owner="CheckpointSavePolicy", field="on_failure"))
        object.__setattr__(self, "on_final", _coerce_bool(on_final, owner="CheckpointSavePolicy", field="on_final"))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointPrunePolicy:
    """Retention intent consumed by restart/result contracts."""

    enabled: bool
    keep_recent: int | None
    keep_best: int | None
    best_metric_name: str | None
    best_metric_direction: CheckpointMetricDirection | None
    keep_final: bool
    keep_failure: bool

    def __init__(
        self,
        *,
        enabled: bool = True,
        keep_recent: int | None = None,
        keep_best: int | None = None,
        best_metric_name: str | None = None,
        best_metric_direction: CheckpointMetricDirection | str | None = None,
        keep_final: bool = True,
        keep_failure: bool = True,
    ) -> None:
        object.__setattr__(self, "enabled", _coerce_bool(enabled, owner="CheckpointPrunePolicy", field="enabled"))
        object.__setattr__(
            self,
            "keep_recent",
            coerce_optional_positive_int(keep_recent, owner="CheckpointPrunePolicy", field="keep_recent"),
        )
        object.__setattr__(
            self,
            "keep_best",
            coerce_optional_positive_int(keep_best, owner="CheckpointPrunePolicy", field="keep_best"),
        )
        if keep_best is not None and best_metric_name is None:
            raise RemotePhysTrainingError(
                "CheckpointPrunePolicy keep_best requires best_metric_name.",
                owner="CheckpointPrunePolicy",
                field="best_metric_name",
            )
        object.__setattr__(
            self,
            "best_metric_name",
            _coerce_optional_name(best_metric_name, owner="CheckpointPrunePolicy", field="best_metric_name"),
        )
        object.__setattr__(
            self,
            "best_metric_direction",
            CheckpointMetricDirection.coerce(best_metric_direction),
        )
        if best_metric_direction is not None and best_metric_name is None:
            raise RemotePhysTrainingError(
                "CheckpointPrunePolicy best_metric_direction requires best_metric_name.",
                owner="CheckpointPrunePolicy",
                field="best_metric_direction",
                best_metric_name=best_metric_name,
            )
        if not enabled:
            if any(v is not None for v in (keep_recent, keep_best, best_metric_name, best_metric_direction)):
                raise RemotePhysTrainingError(
                    "CheckpointPrunePolicy cannot configure keeps when disabled.",
                    owner="CheckpointPrunePolicy",
                    field="enabled",
                    value=enabled,
                )
        if not any((keep_recent, keep_best)) and not (keep_final or keep_failure):
            raise RemotePhysTrainingError(
                "CheckpointPrunePolicy must retain something when enabled.",
                owner="CheckpointPrunePolicy",
                field="policy",
            )
        object.__setattr__(self, "keep_final", _coerce_bool(keep_final, owner="CheckpointPrunePolicy", field="keep_final"))
        object.__setattr__(self, "keep_failure", _coerce_bool(keep_failure, owner="CheckpointPrunePolicy", field="keep_failure"))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointRestorePolicy:
    """Restore intent independent of runtime callback details."""

    mode: CheckpointRestoreMode
    selector: CheckpointSelectionMode
    preferred_stream_id: str | None

    def __init__(
        self,
        *,
        mode: CheckpointRestoreMode = CheckpointRestoreMode.CATALOG,
        selector: CheckpointSelectionMode = CheckpointSelectionMode.LATEST_COMPLETED,
        preferred_stream_id: str | None = None,
    ) -> None:
        object.__setattr__(self, "mode", CheckpointRestoreMode.coerce(mode))
        object.__setattr__(self, "selector", CheckpointSelectionMode.coerce(selector))
        object.__setattr__(
            self,
            "preferred_stream_id",
            _coerce_optional_name(preferred_stream_id, owner="CheckpointRestorePolicy", field="preferred_stream_id"),
        )


@dataclass(frozen=True, init=False, slots=True)
class CheckpointSelection:
    """Checkpoint restart selector configuration."""

    mode: CheckpointSelectionMode
    stream_id: str | None
    metric_name: str | None
    metric_direction: CheckpointMetricDirection | None
    metric_count: int | None
    step_back: int | None
    epoch_back: int | None
    timestamp: float | None
    inclusive_timestamp: bool
    explicit_ref_id: str | None

    def __init__(
        self,
        mode: CheckpointSelectionMode,
        *,
        stream_id: str | None = None,
        metric_name: str | None = None,
        metric_direction: CheckpointMetricDirection | str | None = None,
        metric_count: int | None = None,
        step_back: int | None = None,
        epoch_back: int | None = None,
        timestamp: float | None = None,
        inclusive_timestamp: bool = True,
        explicit_ref_id: str | None = None,
    ) -> None:
        mode = CheckpointSelectionMode.coerce(mode)
        object.__setattr__(
            self,
            "stream_id",
            _coerce_optional_name(stream_id, owner="CheckpointSelection", field="stream_id"),
        )
        object.__setattr__(
            self,
            "metric_name",
            _coerce_optional_name(metric_name, owner="CheckpointSelection", field="metric_name"),
        )
        metric_direction = CheckpointMetricDirection.coerce(metric_direction)
        object.__setattr__(self, "metric_direction", metric_direction)
        object.__setattr__(self, "mode", mode)
        if mode is CheckpointSelectionMode.BEST_BY_METRIC and metric_name is None:
            raise RemotePhysTrainingError(
                "BEST_BY_METRIC selection requires metric_name.",
                owner="CheckpointSelection",
                field="metric_name",
                mode=mode.value,
            )
        if mode is CheckpointSelectionMode.BEST_BY_METRIC and metric_direction is None:
            raise RemotePhysTrainingError(
                "BEST_BY_METRIC selection requires metric_direction.",
                owner="CheckpointSelection",
                field="metric_direction",
                mode=mode.value,
            )
        if mode is CheckpointSelectionMode.N_STEPS_BACK:
            object.__setattr__(
                self,
                "step_back",
                coerce_optional_positive_int(step_back, owner="CheckpointSelection", field="step_back"),
            )
            if step_back is None:
                raise RemotePhysTrainingError(
                    "N_STEPS_BACK selection requires step_back.",
                    owner="CheckpointSelection",
                    field="step_back",
                    mode=mode.value,
                )
        else:
            object.__setattr__(self, "step_back", None)
        if mode is CheckpointSelectionMode.N_EPOCHS_BACK:
            object.__setattr__(
                self,
                "epoch_back",
                coerce_optional_positive_int(epoch_back, owner="CheckpointSelection", field="epoch_back"),
            )
            if epoch_back is None:
                raise RemotePhysTrainingError(
                    "N_EPOCHS_BACK selection requires epoch_back.",
                    owner="CheckpointSelection",
                    field="epoch_back",
                    mode=mode.value,
                )
        else:
            object.__setattr__(self, "epoch_back", None)
        if mode in {CheckpointSelectionMode.BEFORE_TIMESTAMP, CheckpointSelectionMode.AFTER_TIMESTAMP}:
            if timestamp is None:
                raise RemotePhysTrainingError(
                    "Timestamp-based selection requires timestamp.",
                    owner="CheckpointSelection",
                    field="timestamp",
                    mode=mode.value,
                )
            object.__setattr__(self, "timestamp", _coerce_finite_float(timestamp, owner="CheckpointSelection", field="timestamp"))
        else:
            if timestamp is not None:
                raise RemotePhysTrainingError(
                    "Timestamp is only supported by before/after timestamp selectors.",
                    owner="CheckpointSelection",
                    field="timestamp",
                    mode=mode.value,
                )
            object.__setattr__(self, "timestamp", None)
        object.__setattr__(
            self,
            "inclusive_timestamp",
            _coerce_bool(inclusive_timestamp, owner="CheckpointSelection", field="inclusive_timestamp"),
        )
        object.__setattr__(
            self,
            "metric_count",
            coerce_optional_positive_int(metric_count, owner="CheckpointSelection", field="metric_count"),
        )
        object.__setattr__(
            self,
            "explicit_ref_id",
            _coerce_optional_name(explicit_ref_id, owner="CheckpointSelection", field="explicit_ref_id"),
        )
        if mode is CheckpointSelectionMode.EXPLICIT and explicit_ref_id is None:
            raise RemotePhysTrainingError(
                "EXPLICIT selection requires explicit_ref_id.",
                owner="CheckpointSelection",
                field="explicit_ref_id",
                mode=mode.value,
            )
        if mode is not CheckpointSelectionMode.EXPLICIT and explicit_ref_id is not None:
            raise RemotePhysTrainingError(
                "explicit_ref_id is only supported for EXPLICIT selection.",
                owner="CheckpointSelection",
                field="explicit_ref_id",
                mode=mode.value,
            )


@dataclass(frozen=True, init=False, slots=True)
class CheckpointSelectionResult:
    """Deterministic checkpoint selection result evidence."""

    selection: CheckpointSelection
    status: CheckpointResultStatus
    ref: CheckpointRef | None
    reason: str | None

    def __init__(
        self,
        *,
        selection: CheckpointSelection,
        status: CheckpointResultStatus,
        ref: CheckpointRef | None = None,
        reason: str | None = None,
    ) -> None:
        status = CheckpointResultStatus.coerce(status)
        if not isinstance(selection, CheckpointSelection):
            raise RemotePhysTrainingError(
                "CheckpointSelectionResult selection must be a CheckpointSelection.",
                owner="CheckpointSelectionResult",
                field="selection",
                expected="CheckpointSelection",
                actual=type(selection).__name__,
            )
        if ref is not None and not isinstance(ref, CheckpointRef):
            raise RemotePhysTrainingError(
                "CheckpointSelectionResult ref must be a CheckpointRef when provided.",
                owner="CheckpointSelectionResult",
                field="ref",
                expected="CheckpointRef | None",
                actual=type(ref).__name__,
            )
        if status in {CheckpointResultStatus.COMPLETED, CheckpointResultStatus.ATTEMPTED} and ref is None:
            raise RemotePhysTrainingError(
                "Completed checkpoint selections require a selected ref.",
                owner="CheckpointSelectionResult",
                field="status",
                value=status.value,
            )
        if status in {CheckpointResultStatus.SKIPPED, CheckpointResultStatus.UNSUPPORTED} and ref is not None:
            raise RemotePhysTrainingError(
                "Skipped or unsupported checkpoint selections must not include a ref.",
                owner="CheckpointSelectionResult",
                field="ref",
                value=type(ref).__name__,
            )
        object.__setattr__(self, "selection", selection)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "ref", ref)
        object.__setattr__(
            self,
            "reason",
            _coerce_optional_name(reason, owner="CheckpointSelectionResult", field="reason"),
        )


@dataclass(frozen=True, init=False, slots=True)
class CheckpointCatalog:
    """Index of checkpoint references used for deterministic restart selection."""

    refs: tuple[CheckpointRef, ...]

    def __init__(self, refs: Iterable[CheckpointRef] = ()) -> None:
        object.__setattr__(self, "refs", _coerce_records(refs, owner="CheckpointCatalog", field="refs", expected="CheckpointRef"))

    def select(self, selector: CheckpointSelection) -> CheckpointSelectionResult:
        if not isinstance(selector, CheckpointSelection):
            raise RemotePhysTrainingError(
                "CheckpointCatalog.select expects a CheckpointSelection.",
                owner="CheckpointCatalog",
                field="selector",
                expected="CheckpointSelection",
                actual=type(selector).__name__,
            )
        selected = self._select_by_mode(selector)
        if selected is None:
            return CheckpointSelectionResult(
                selection=selector,
                status=CheckpointResultStatus.UNAVAILABLE,
                reason="No matching checkpoint reference.",
            )
        return CheckpointSelectionResult(
            selection=selector,
            status=CheckpointResultStatus.COMPLETED,
            ref=selected,
        )

    def _select_by_mode(self, selector: CheckpointSelection) -> CheckpointRef | None:
        scoped = [ref for ref in self.refs if selector.stream_id is None or ref.stream_id == selector.stream_id]
        if selector.mode is CheckpointSelectionMode.LATEST_COMPLETED:
            candidates = [ref for ref in scoped if ref.status is CheckpointRefStatus.COMPLETED]
            return _choose_latest(candidates)

        if selector.mode is CheckpointSelectionMode.BEST_BY_METRIC:
            candidates = [
                ref
                for ref in scoped
                if ref.metric_name == selector.metric_name
                and ref.metric_direction == selector.metric_direction
                and ref.metric_value is not None
            ]
            candidates = [ref for ref in candidates if ref.status is CheckpointRefStatus.COMPLETED]
            return _choose_best(candidates, selector.metric_direction or CheckpointMetricDirection.MAX)

        if selector.mode is CheckpointSelectionMode.N_STEPS_BACK:
            completed = [ref for ref in scoped if ref.status is CheckpointRefStatus.COMPLETED and ref.step is not None]
            if not completed:
                return None
            anchor = max(ref.step for ref in completed)
            target = max(0, anchor - (selector.step_back or 0))
            ordered = sorted(completed, key=_selection_key, reverse=True)
            ordered = [ref for ref in ordered if (ref.step or 0) <= target]
            return ordered[min(selector.metric_count or 1, len(ordered)) - 1] if ordered else None

        if selector.mode is CheckpointSelectionMode.N_EPOCHS_BACK:
            completed = [ref for ref in scoped if ref.status is CheckpointRefStatus.COMPLETED and ref.epoch is not None]
            if not completed:
                return None
            anchor = max(ref.epoch for ref in completed)
            target = max(0, anchor - (selector.epoch_back or 0))
            ordered = sorted(completed, key=_selection_key, reverse=True)
            ordered = [ref for ref in ordered if (ref.epoch or 0) <= target]
            return ordered[min(selector.metric_count or 1, len(ordered)) - 1] if ordered else None

        if selector.mode is CheckpointSelectionMode.BEFORE_TIMESTAMP:
            completed = [
                ref
                for ref in scoped
                if ref.status is CheckpointRefStatus.COMPLETED and ref.timestamp is not None
            ]
            candidates = [
                ref
                for ref in completed
                if ref.timestamp is not None
                and (
                    ref.timestamp <= selector.timestamp
                    if selector.timestamp is not None and selector.inclusive_timestamp
                    else ref.timestamp < (selector.timestamp or 0)
                )
            ]
            return _choose_latest(candidates)

        if selector.mode is CheckpointSelectionMode.AFTER_TIMESTAMP:
            completed = [
                ref
                for ref in scoped
                if ref.status is CheckpointRefStatus.COMPLETED and ref.timestamp is not None
            ]
            candidates = [
                ref
                for ref in completed
                if ref.timestamp is not None
                and (
                    ref.timestamp >= selector.timestamp
                    if selector.timestamp is not None and selector.inclusive_timestamp
                    else ref.timestamp > (selector.timestamp or 0)
                )
            ]
            return _choose_earliest(candidates)

        if selector.mode is CheckpointSelectionMode.FINAL:
            candidates = [ref for ref in scoped if ref.is_final]
            if not candidates:
                return None
            return _choose_latest(candidates)

        if selector.mode is CheckpointSelectionMode.FAILURE:
            candidates = [ref for ref in scoped if ref.is_failure]
            if not candidates:
                return None
            return _choose_latest(candidates)

        if selector.mode is CheckpointSelectionMode.EXPLICIT:
            for ref in scoped:
                if ref.ref_id == selector.explicit_ref_id:
                    return ref
            return None

        raise RemotePhysTrainingError(
            "Unsupported checkpoint selection mode.",
            owner="CheckpointCatalog",
            field="selector.mode",
            value=selector.mode,
        )


@dataclass(frozen=True, init=False, slots=True)
class CheckpointSaveResult:
    """Save attempt outcome evidence for checkpoint integrations."""

    status: CheckpointResultStatus
    ref_id: str | None
    retention_policy_applied: str | None
    reason: str | None

    def __init__(
        self,
        *,
        status: CheckpointResultStatus,
        ref_id: str | None = None,
        retention_policy_applied: str | None = None,
        reason: str | None = None,
    ) -> None:
        object.__setattr__(self, "status", CheckpointResultStatus.coerce(status))
        object.__setattr__(self, "ref_id", _coerce_optional_name(ref_id, owner="CheckpointSaveResult", field="ref_id"))
        object.__setattr__(self, "retention_policy_applied", _coerce_optional_name(retention_policy_applied, owner="CheckpointSaveResult", field="retention_policy_applied"))
        object.__setattr__(self, "reason", _coerce_optional_name(reason, owner="CheckpointSaveResult", field="reason"))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointRestoreResult:
    """Restore outcome evidence for restart behavior."""

    status: CheckpointResultStatus
    ref_id: str | None
    mode: CheckpointRestoreMode
    reason: str | None

    def __init__(
        self,
        *,
        status: CheckpointResultStatus,
        mode: CheckpointRestoreMode,
        ref_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        object.__setattr__(self, "status", CheckpointResultStatus.coerce(status))
        object.__setattr__(self, "mode", CheckpointRestoreMode.coerce(mode))
        object.__setattr__(self, "ref_id", _coerce_optional_name(ref_id, owner="CheckpointRestoreResult", field="ref_id"))
        object.__setattr__(self, "reason", _coerce_optional_name(reason, owner="CheckpointRestoreResult", field="reason"))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointPruneEvidence:
    """Per-checkpoint prune action evidence."""

    ref: CheckpointRef
    reason: CheckpointRetentionReason

    def __init__(self, ref: CheckpointRef, reason: CheckpointRetentionReason | str) -> None:
        if not isinstance(ref, CheckpointRef):
            raise RemotePhysTrainingError(
                "CheckpointPruneEvidence ref must be a CheckpointRef.",
                owner="CheckpointPruneEvidence",
                field="ref",
                expected="CheckpointRef",
                actual=type(ref).__name__,
            )
        object.__setattr__(self, "ref", ref)
        object.__setattr__(self, "reason", CheckpointRetentionReason.coerce(reason))


@dataclass(frozen=True, init=False, slots=True)
class CheckpointPruneResult:
    """Retention/ejection outcome for a checkpoint catalog."""

    status: CheckpointResultStatus
    kept: tuple[CheckpointRef, ...]
    dropped: tuple[CheckpointPruneEvidence, ...]
    keep_count: int | None

    def __init__(
        self,
        *,
        status: CheckpointResultStatus,
        kept: Iterable[CheckpointRef] = (),
        dropped: Iterable[CheckpointPruneEvidence] = (),
        keep_count: int | None = None,
    ) -> None:
        object.__setattr__(self, "status", CheckpointResultStatus.coerce(status))
        object.__setattr__(
            self,
            "kept",
            _coerce_records(kept, owner="CheckpointPruneResult", field="kept", expected="CheckpointRef"),
        )
        object.__setattr__(
            self,
            "dropped",
            _coerce_records(dropped, owner="CheckpointPruneResult", field="dropped", expected="CheckpointPruneEvidence"),
        )
        if keep_count is not None:
            keep_count = coerce_non_negative_int(keep_count, owner="CheckpointPruneResult", field="keep_count")
        object.__setattr__(self, "keep_count", keep_count)


# ---------------------------------------------------------------------------
# Helpers


def _selection_key(ref: CheckpointRef) -> tuple[float, int, int, int, int, int, str, str]:
    metric_value = float(ref.metric_value) if ref.metric_value is not None else float("-inf")
    status_rank = 0 if ref.status is CheckpointRefStatus.COMPLETED else 1
    return (
        status_rank,
        ref.timestamp if ref.timestamp is not None else -1.0,
        ref.epoch if ref.epoch is not None else -1,
        ref.step if ref.step is not None else -1,
        ref.sequence_id if ref.sequence_id is not None else -1,
        0 if ref.stream_id is None else 1,
        ref.stream_id or "",
        ref.ref_id,
    )


def _choose_latest(refs: list[CheckpointRef]) -> CheckpointRef | None:
    return _sort_refs(refs)


def _choose_earliest(refs: list[CheckpointRef]) -> CheckpointRef | None:
    if not refs:
        return None
    sorted_refs = sorted(refs, key=_selection_key)
    return sorted_refs[0]


def _sort_refs(refs: list[CheckpointRef]) -> CheckpointRef | None:
    if not refs:
        return None
    sorted_refs = sorted(refs, key=_selection_key, reverse=True)
    return sorted_refs[0]


def _choose_best(
    refs: list[CheckpointRef],
    direction: CheckpointMetricDirection,
) -> CheckpointRef | None:
    if not refs:
        return None
    def best_key(ref: CheckpointRef) -> tuple[int, float, float, int, int, int, int, str, str]:
        metric = ref.metric_value if ref.metric_value is not None else float("-inf")
        if direction is CheckpointMetricDirection.MIN:
            metric = -metric
        return (
            0 if ref.status is CheckpointRefStatus.COMPLETED else 1,
            metric,
            ref.timestamp if ref.timestamp is not None else -1.0,
            ref.epoch if ref.epoch is not None else -1,
            ref.step if ref.step is not None else -1,
            ref.sequence_id if ref.sequence_id is not None else -1,
            0 if ref.stream_id is None else 1,
            ref.stream_id or "",
            ref.ref_id,
        )
    return sorted(refs, key=best_key, reverse=True)[0]


def _coerce_name(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return value


def _coerce_optional_name(value: str | None, *, owner: str, field: str) -> str | None:
    if value is None:
        return None
    return _coerce_name(value, owner=owner, field=field)


def _coerce_bool(value: object, *, owner: str, field: str) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a boolean.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_records(
    values: Iterable[object],
    *,
    owner: str,
    field: str,
    expected: str,
) -> tuple[object, ...]:
    try:
        values = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected=f"Iterable[{expected}]",
            actual=type(values).__name__,
        ) from exc
    expected_type = {
        "CheckpointRef": CheckpointRef,
        "CheckpointPruneEvidence": CheckpointPruneEvidence,
    }[expected]
    for index, value in enumerate(values):
        if not isinstance(value, expected_type):
            raise RemotePhysTrainingError(
                f"{owner} {field} contains invalid entries.",
                owner=owner,
                field=field,
                expected=expected,
                index=index,
                actual=type(value).__name__,
            )
    return values


def _coerce_positive_float(value: object, *, owner: str, field: str) -> float:
    value = _coerce_finite_float(value, owner=owner, field=field)
    if value <= 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be positive.",
            owner=owner,
            field=field,
            expected="positive number",
            actual=value,
        )
    return value


def _coerce_finite_float(value: object, *, owner: str, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a finite number.",
            owner=owner,
            field=field,
            expected="finite number",
            actual=type(value).__name__,
        )
    return float(value)


CheckpointRef.__hash__ = None  # type: ignore[assignment]
CheckpointSelection.__hash__ = None  # type: ignore[assignment]
CheckpointSelectionResult.__hash__ = None  # type: ignore[assignment]
CheckpointCatalog.__hash__ = None  # type: ignore[assignment]
CheckpointSavePolicy.__hash__ = None  # type: ignore[assignment]
CheckpointPrunePolicy.__hash__ = None  # type: ignore[assignment]
CheckpointRestorePolicy.__hash__ = None  # type: ignore[assignment]
CheckpointSaveResult.__hash__ = None  # type: ignore[assignment]
CheckpointRestoreResult.__hash__ = None  # type: ignore[assignment]
CheckpointPruneEvidence.__hash__ = None  # type: ignore[assignment]
CheckpointPruneResult.__hash__ = None  # type: ignore[assignment]
