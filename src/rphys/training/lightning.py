"""Optional Lightning adapter for shared rphys training results.

This module is importable without Lightning, torch, CUDA, NVML, or profiler
packages installed. It inspects package metadata before importing Lightning so
known unsafe package versions are rejected before import-time code can run.
"""

from __future__ import annotations

import importlib
import importlib.metadata as metadata
from collections.abc import Callable, Generator, Iterable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from rphys.data import Batch
from rphys.errors import RemotePhysDependencyError, RemotePhysTrainingError
from rphys.learning import Learner, LoopContext, LoopMode

from ._validation import PrimitiveValue, coerce_optional_non_empty_string
from .checkpoint import (
    CheckpointCatalog,
    CheckpointMetricDirection,
    CheckpointPrunePolicy,
    CheckpointPruneResult,
    CheckpointRestoreMode,
    CheckpointRestorePolicy,
    CheckpointRestoreResult,
    CheckpointResultStatus,
    CheckpointSavePolicy,
    CheckpointSaveResult,
    CheckpointSelection,
    CheckpointSelectionMode,
    CheckpointSelectionResult,
)
from .events import TrainingEvent, TrainingEventPhase
from .plan import TrainingPlan
from .policies import CompilePolicy, KernelPolicy, PolicyStatus, PrecisionPolicy
from .probes import (
    ProbeFailurePolicy,
    ProbeHookPoint,
    ProbeSelector,
    ProbeSelectorMode,
    TrainingProbe,
    UnavailableProbeEvidence,
)
from .profiling import (
    AsyncTrainingProfileWriter,
    ProfileSpanSummary,
    ProfileWriterFlushScope,
    ResourceMonitor,
    TrainingProfile,
    TrainingProfileRecorder,
    UnavailableProfileProbe,
)
from .results import TrainingEventSummary, TrainingMetricSummary, TrainingResult, TrainingStatus

__all__ = [
    "LIGHTNING_SECURITY_ADVISORY_URL",
    "LIGHTNING_TRAINER_KWARG_NAMES",
    "LightningBridgeCallback",
    "LightningBridgeConfig",
    "LightningCheckpointMapping",
    "LightningDependencyPreflight",
    "LightningDependencyStatus",
    "LightningPolicyMapping",
    "LightningProfilerBridge",
    "LightningTrainerConfig",
    "LightningTrainingEngine",
    "fit_lightning_module",
    "map_lightning_checkpoint_policies",
    "map_lightning_policies",
    "predict_lightning_module",
    "preflight_lightning_dependency",
    "test_lightning_module",
    "validate_lightning_module",
]

LIGHTNING_SECURITY_ADVISORY_URL = (
    "https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3"
)
LIGHTNING_SAFE_MAX_VERSION = (2, 6, 1)
LIGHTNING_DISTRIBUTIONS = ("lightning", "pytorch-lightning")
LIGHTNING_MODULE_NAME = "lightning.pytorch"
LIGHTNING_TRAINER_KWARG_NAMES = frozenset(
    {
        "accelerator",
        "accumulate_grad_batches",
        "barebones",
        "benchmark",
        "callbacks",
        "check_val_every_n_epoch",
        "default_root_dir",
        "detect_anomaly",
        "deterministic",
        "devices",
        "enable_autolog_hparams",
        "enable_checkpointing",
        "enable_model_summary",
        "enable_progress_bar",
        "fast_dev_run",
        "gradient_clip_algorithm",
        "gradient_clip_val",
        "inference_mode",
        "limit_predict_batches",
        "limit_test_batches",
        "limit_train_batches",
        "limit_val_batches",
        "log_every_n_steps",
        "logger",
        "max_epochs",
        "max_steps",
        "min_epochs",
        "min_steps",
        "model_registry",
        "num_sanity_val_steps",
        "plugins",
        "precision",
        "profiler",
        "reload_dataloaders_every_n_epochs",
        "strategy",
        "sync_batchnorm",
        "val_check_interval",
    }
)

_LIGHTNING_PRECISION_VALUES = {
    "16-mixed",
    "bf16-mixed",
    "32-true",
    "64-true",
    "transformer-engine",
    "transformer-engine-float16",
}
_LIGHTNING_PRECISION_ALIASES = {
    "16": "16-mixed",
    "16-mixed": "16-mixed",
    "fp16": "16-mixed",
    "float16": "16-mixed",
    "bf16": "bf16-mixed",
    "bfloat16": "bf16-mixed",
    "bf16-mixed": "bf16-mixed",
    "32": "32-true",
    "32-true": "32-true",
    "fp32": "32-true",
    "float32": "32-true",
    "64": "64-true",
    "64-true": "64-true",
    "fp64": "64-true",
    "float64": "64-true",
    "transformer-engine": "transformer-engine",
    "transformer-engine-float16": "transformer-engine-float16",
}


class LightningDependencyStatus(StrEnum):
    """Dependency preflight status before importing Lightning."""

    AVAILABLE = "available"
    ABSENT = "absent"
    UNSAFE = "unsafe"
    INVALID = "invalid"

    @classmethod
    def coerce(cls, value: "LightningDependencyStatus | str") -> "LightningDependencyStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise RemotePhysTrainingError(
                    "Unsupported Lightning dependency status.",
                    owner="LightningDependencyStatus",
                    field="status",
                    expected=tuple(status.value for status in cls),
                    actual=value,
                ) from exc
        raise RemotePhysTrainingError(
            "Lightning dependency status must be a LightningDependencyStatus or string.",
            owner="LightningDependencyStatus",
            field="status",
            expected="LightningDependencyStatus | str",
            actual=type(value).__name__,
        )


@dataclass(frozen=True, init=False, slots=True)
class LightningDependencyPreflight:
    """Result of checking Lightning package metadata before import.

    The security advisory current on 2026-05-18 marks PyTorch Lightning
    versions ``>=2.6.2`` as affected and recommends version ``2.6.1``. rphys
    treats later versions as unsafe until the advisory is explicitly refreshed.
    """

    status: LightningDependencyStatus
    package_name: str | None
    version: str | None
    module_name: str
    reason: str | None
    advisory_url: str | None

    def __init__(
        self,
        *,
        status: LightningDependencyStatus | str,
        package_name: str | None = None,
        version: str | None = None,
        module_name: str = LIGHTNING_MODULE_NAME,
        reason: str | None = None,
        advisory_url: str | None = None,
    ) -> None:
        resolved_status = LightningDependencyStatus.coerce(status)
        object.__setattr__(self, "status", resolved_status)
        object.__setattr__(
            self,
            "package_name",
            coerce_optional_non_empty_string(
                package_name,
                owner="LightningDependencyPreflight",
                field="package_name",
            ),
        )
        object.__setattr__(
            self,
            "version",
            coerce_optional_non_empty_string(
                version,
                owner="LightningDependencyPreflight",
                field="version",
            ),
        )
        object.__setattr__(
            self,
            "module_name",
            _coerce_non_empty_string(
                module_name,
                owner="LightningDependencyPreflight",
                field="module_name",
            ),
        )
        object.__setattr__(
            self,
            "reason",
            coerce_optional_non_empty_string(
                reason,
                owner="LightningDependencyPreflight",
                field="reason",
            ),
        )
        object.__setattr__(
            self,
            "advisory_url",
            coerce_optional_non_empty_string(
                advisory_url,
                owner="LightningDependencyPreflight",
                field="advisory_url",
            ),
        )
        if resolved_status is LightningDependencyStatus.AVAILABLE:
            if package_name is None or version is None:
                raise RemotePhysTrainingError(
                    "Available Lightning preflight requires package_name and version.",
                    owner="LightningDependencyPreflight",
                    field="status",
                    status=resolved_status.value,
                )
        if resolved_status in {
            LightningDependencyStatus.ABSENT,
            LightningDependencyStatus.UNSAFE,
            LightningDependencyStatus.INVALID,
        } and reason is None:
            raise RemotePhysTrainingError(
                "Unavailable Lightning preflight requires a reason.",
                owner="LightningDependencyPreflight",
                field="reason",
                status=resolved_status.value,
            )

    @property
    def available(self) -> bool:
        """Return whether Lightning can be imported by the adapter."""

        return self.status is LightningDependencyStatus.AVAILABLE


@dataclass(frozen=True, init=False, slots=True)
class LightningTrainerConfig:
    """Bounded public ``lightning.pytorch.Trainer`` keyword arguments."""

    trainer_kwargs: Mapping[str, object]

    def __init__(self, trainer_kwargs: Mapping[str, object] | None = None) -> None:
        object.__setattr__(self, "trainer_kwargs", _freeze_trainer_kwargs(trainer_kwargs))

    def to_kwargs(self) -> dict[str, object]:
        """Return a mutable copy suitable for ``Trainer(**kwargs)``."""

        return dict(self.trainer_kwargs)


@dataclass(frozen=True, init=False, slots=True)
class LightningPolicyMapping:
    """Policy mapping evidence and resulting Lightning ``Trainer`` kwargs."""

    trainer_kwargs: Mapping[str, object]
    precision_policy: PrecisionPolicy | None
    compile_policy: CompilePolicy | None
    kernel_policy: KernelPolicy | None
    diagnostics: tuple[str, ...]

    def __init__(
        self,
        *,
        trainer_kwargs: Mapping[str, object] | None = None,
        precision_policy: PrecisionPolicy | None = None,
        compile_policy: CompilePolicy | None = None,
        kernel_policy: KernelPolicy | None = None,
        diagnostics: Iterable[str] = (),
    ) -> None:
        object.__setattr__(self, "trainer_kwargs", _freeze_trainer_kwargs(trainer_kwargs))
        object.__setattr__(
            self,
            "precision_policy",
            _coerce_optional_policy(
                precision_policy,
                PrecisionPolicy,
                field="precision_policy",
            ),
        )
        object.__setattr__(
            self,
            "compile_policy",
            _coerce_optional_policy(
                compile_policy,
                CompilePolicy,
                field="compile_policy",
            ),
        )
        object.__setattr__(
            self,
            "kernel_policy",
            _coerce_optional_policy(
                kernel_policy,
                KernelPolicy,
                field="kernel_policy",
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            _coerce_string_tuple(
                diagnostics,
                owner="LightningPolicyMapping",
                field="diagnostics",
            ),
        )

    def to_kwargs(self) -> dict[str, object]:
        """Return the Lightning trainer kwargs after policy mapping."""

        return dict(self.trainer_kwargs)


@dataclass(frozen=True, init=False, slots=True)
class LightningCheckpointMapping:
    """Public Lightning ``ModelCheckpoint`` kwargs and rphys retention evidence."""

    callback_kwargs: Mapping[str, object]
    save_policy: CheckpointSavePolicy | None
    prune_policy: CheckpointPrunePolicy | None
    requires_recency_pruner: bool
    diagnostics: tuple[str, ...]

    def __init__(
        self,
        *,
        callback_kwargs: Mapping[str, object] | None = None,
        save_policy: CheckpointSavePolicy | None = None,
        prune_policy: CheckpointPrunePolicy | None = None,
        requires_recency_pruner: bool = False,
        diagnostics: Iterable[str] = (),
    ) -> None:
        object.__setattr__(self, "callback_kwargs", MappingProxyType(dict(callback_kwargs or {})))
        object.__setattr__(
            self,
            "save_policy",
            _coerce_optional_checkpoint_policy(
                save_policy,
                CheckpointSavePolicy,
                field="save_policy",
            ),
        )
        object.__setattr__(
            self,
            "prune_policy",
            _coerce_optional_checkpoint_policy(
                prune_policy,
                CheckpointPrunePolicy,
                field="prune_policy",
            ),
        )
        object.__setattr__(
            self,
            "requires_recency_pruner",
            _coerce_bool(
                requires_recency_pruner,
                owner="LightningCheckpointMapping",
                field="requires_recency_pruner",
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            _coerce_string_tuple(
                diagnostics,
                owner="LightningCheckpointMapping",
                field="diagnostics",
            ),
        )

    def to_kwargs(self) -> dict[str, object]:
        """Return kwargs suitable for ``lightning.pytorch.callbacks.ModelCheckpoint``."""

        return dict(self.callback_kwargs)


@dataclass(frozen=True, init=False, slots=True)
class LightningBridgeConfig:
    """Runtime bridge components that normalize Lightning evidence into rphys records."""

    resource_monitors: tuple[ResourceMonitor, ...]
    profile_writers: tuple[AsyncTrainingProfileWriter, ...]
    training_probes: tuple[TrainingProbe, ...]
    checkpoint_catalog: CheckpointCatalog
    checkpoint_restore_policy: CheckpointRestorePolicy | None
    checkpoint_restore_selection: CheckpointSelection | None
    checkpoint_save_policy: CheckpointSavePolicy | None
    checkpoint_prune_policy: CheckpointPrunePolicy | None
    run_id: str | None
    timeline_id: str | None
    process_id: int | None
    node_id: str | None
    local_rank: int | None
    global_rank: int | None
    device_id: str | None

    def __init__(
        self,
        *,
        resource_monitors: Iterable[ResourceMonitor] = (),
        profile_writers: Iterable[AsyncTrainingProfileWriter] = (),
        training_probes: Iterable[TrainingProbe] = (),
        checkpoint_catalog: CheckpointCatalog | None = None,
        checkpoint_restore_policy: CheckpointRestorePolicy | None = None,
        checkpoint_restore_selection: CheckpointSelection | None = None,
        checkpoint_save_policy: CheckpointSavePolicy | None = None,
        checkpoint_prune_policy: CheckpointPrunePolicy | None = None,
        run_id: str | None = None,
        timeline_id: str | None = None,
        process_id: int | None = None,
        node_id: str | None = None,
        local_rank: int | None = None,
        global_rank: int | None = None,
        device_id: str | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "resource_monitors",
            _coerce_records(
                resource_monitors,
                ResourceMonitor,
                owner="LightningBridgeConfig",
                field="resource_monitors",
            ),
        )
        object.__setattr__(
            self,
            "profile_writers",
            _coerce_records(
                profile_writers,
                AsyncTrainingProfileWriter,
                owner="LightningBridgeConfig",
                field="profile_writers",
            ),
        )
        object.__setattr__(
            self,
            "training_probes",
            _coerce_training_probes(training_probes),
        )
        object.__setattr__(
            self,
            "checkpoint_catalog",
            checkpoint_catalog if checkpoint_catalog is not None else CheckpointCatalog(),
        )
        if not isinstance(self.checkpoint_catalog, CheckpointCatalog):
            raise RemotePhysTrainingError(
                "LightningBridgeConfig checkpoint_catalog must be a CheckpointCatalog.",
                owner="LightningBridgeConfig",
                field="checkpoint_catalog",
                expected="CheckpointCatalog | None",
                actual=type(checkpoint_catalog).__name__,
            )
        object.__setattr__(
            self,
            "checkpoint_restore_policy",
            _coerce_optional_checkpoint_policy(
                checkpoint_restore_policy,
                CheckpointRestorePolicy,
                field="checkpoint_restore_policy",
            ),
        )
        object.__setattr__(
            self,
            "checkpoint_restore_selection",
            _coerce_optional_checkpoint_policy(
                checkpoint_restore_selection,
                CheckpointSelection,
                field="checkpoint_restore_selection",
            ),
        )
        object.__setattr__(
            self,
            "checkpoint_save_policy",
            _coerce_optional_checkpoint_policy(
                checkpoint_save_policy,
                CheckpointSavePolicy,
                field="checkpoint_save_policy",
            ),
        )
        object.__setattr__(
            self,
            "checkpoint_prune_policy",
            _coerce_optional_checkpoint_policy(
                checkpoint_prune_policy,
                CheckpointPrunePolicy,
                field="checkpoint_prune_policy",
            ),
        )
        _set_bridge_context(
            self,
            owner="LightningBridgeConfig",
            run_id=run_id,
            timeline_id=timeline_id,
            process_id=process_id,
            node_id=node_id,
            local_rank=local_rank,
            global_rank=global_rank,
            device_id=device_id,
        )

    @classmethod
    def from_plan(cls, plan: TrainingPlan) -> "LightningBridgeConfig":
        """Build bridge configuration from a shared rphys ``TrainingPlan``."""

        return cls(
            resource_monitors=plan.resource_monitors,
            profile_writers=plan.profile_writers,
            training_probes=plan.training_probes,
            checkpoint_catalog=plan.checkpoint_catalog,
            checkpoint_restore_policy=plan.checkpoint_restore_policy,
            checkpoint_restore_selection=plan.checkpoint_restore_selection,
            checkpoint_save_policy=plan.checkpoint_save_policy,
            checkpoint_prune_policy=plan.checkpoint_prune_policy,
            run_id=plan.run_id,
            timeline_id=plan.timeline_id,
            process_id=plan.process_id,
            node_id=plan.node_id,
            local_rank=plan.local_rank,
            global_rank=plan.global_rank,
            device_id=plan.device_id,
        )

    @property
    def enabled(self) -> bool:
        """Return whether any bridge component has work to do."""

        return any(
            (
                self.resource_monitors,
                self.profile_writers,
                self.training_probes,
                self.checkpoint_restore_policy is not None,
                self.checkpoint_restore_selection is not None,
                self.checkpoint_save_policy is not None,
                self.checkpoint_prune_policy is not None,
            )
        )


type LightningModuleFactory = Callable[[object, TrainingPlan, Learner, LoopMode], object]


class LightningTrainingEngine:
    """Optional Lightning-backed engine returning shared ``TrainingResult`` records."""

    __slots__ = (
        "allow_unsafe_versions",
        "bridge_config",
        "ckpt_path",
        "compile_policy",
        "kernel_policy",
        "module_factory",
        "precision_policy",
        "trainer_config",
    )

    def __init__(
        self,
        *,
        trainer_config: LightningTrainerConfig | None = None,
        trainer_kwargs: Mapping[str, object] | None = None,
        precision_policy: PrecisionPolicy | None = None,
        compile_policy: CompilePolicy | None = None,
        kernel_policy: KernelPolicy | None = None,
        module_factory: LightningModuleFactory | None = None,
        bridge_config: LightningBridgeConfig | None = None,
        ckpt_path: str | None = None,
        allow_unsafe_versions: bool = False,
    ) -> None:
        if trainer_config is not None and trainer_kwargs is not None:
            raise RemotePhysTrainingError(
                "LightningTrainingEngine accepts trainer_config or trainer_kwargs, not both.",
                owner="LightningTrainingEngine",
                field="trainer_kwargs",
            )
        if trainer_config is not None and not isinstance(trainer_config, LightningTrainerConfig):
            raise RemotePhysTrainingError(
                "LightningTrainingEngine trainer_config must be a LightningTrainerConfig.",
                owner="LightningTrainingEngine",
                field="trainer_config",
                expected="LightningTrainerConfig | None",
                actual=type(trainer_config).__name__,
            )
        if module_factory is not None and not callable(module_factory):
            raise RemotePhysTrainingError(
                "LightningTrainingEngine module_factory must be callable.",
                owner="LightningTrainingEngine",
                field="module_factory",
                expected="callable | None",
                actual=type(module_factory).__name__,
            )
        if bridge_config is not None and not isinstance(bridge_config, LightningBridgeConfig):
            raise RemotePhysTrainingError(
                "LightningTrainingEngine bridge_config must be a LightningBridgeConfig.",
                owner="LightningTrainingEngine",
                field="bridge_config",
                expected="LightningBridgeConfig | None",
                actual=type(bridge_config).__name__,
            )
        object.__setattr__(
            self,
            "trainer_config",
            trainer_config if trainer_config is not None else LightningTrainerConfig(trainer_kwargs),
        )
        object.__setattr__(
            self,
            "precision_policy",
            _coerce_optional_policy(
                precision_policy,
                PrecisionPolicy,
                field="precision_policy",
            ),
        )
        object.__setattr__(
            self,
            "compile_policy",
            _coerce_optional_policy(
                compile_policy,
                CompilePolicy,
                field="compile_policy",
            ),
        )
        object.__setattr__(
            self,
            "kernel_policy",
            _coerce_optional_policy(
                kernel_policy,
                KernelPolicy,
                field="kernel_policy",
            ),
        )
        object.__setattr__(self, "module_factory", module_factory)
        object.__setattr__(self, "bridge_config", bridge_config)
        object.__setattr__(
            self,
            "ckpt_path",
            coerce_optional_non_empty_string(
                ckpt_path,
                owner="LightningTrainingEngine",
                field="ckpt_path",
            ),
        )
        object.__setattr__(self, "allow_unsafe_versions", _coerce_bool(allow_unsafe_versions))

    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run ``Trainer.fit`` through the shared rphys engine protocol."""

        return self._run("fit", LoopMode.TRAIN, _require_plan(plan), learner)

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run ``Trainer.validate`` through the shared rphys engine protocol."""

        return self._run("validate", LoopMode.VALIDATE, _require_plan(plan), learner)

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run ``Trainer.test`` through the shared rphys engine protocol."""

        return self._run("test", LoopMode.TEST, _require_plan(plan), learner)

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        """Run ``Trainer.predict`` through the shared rphys engine protocol."""

        return self._run("predict", LoopMode.PREDICT, _require_plan(plan), learner)

    def _run(self, method_name: str, mode: LoopMode, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        mapping = map_lightning_policies(
            trainer_config=self.trainer_config,
            precision_policy=self.precision_policy,
            compile_policy=self.compile_policy,
            kernel_policy=self.kernel_policy,
        )
        preflight = preflight_lightning_dependency(allow_unsafe_versions=self.allow_unsafe_versions)
        if not preflight.available:
            return _preflight_failed_result(mode, preflight, mapping)
        try:
            lightning_api = _load_lightning(preflight=preflight)
            bridge_config = (
                self.bridge_config
                if self.bridge_config is not None
                else LightningBridgeConfig.from_plan(plan)
            )
            module = _build_engine_module(
                lightning_api,
                plan,
                learner,
                mode,
                module_factory=self.module_factory,
            )
            return _run_lightning_trainer(
                lightning_api,
                method_name=method_name,
                mode=mode,
                model=module,
                trainer_kwargs=mapping.to_kwargs(),
                train_dataloaders=plan.train_batches,
                val_dataloaders=plan.validation_batches,
                dataloaders=plan.batches_for(mode),
                ckpt_path=self.ckpt_path,
                policy_mapping=mapping,
                preflight=preflight,
                bridge_config=bridge_config,
            )
        except Exception as exc:  # pragma: no cover - exercised with fake failures in tests.
            return _failed_result(mode, exc, mapping, preflight=preflight)


def preflight_lightning_dependency(
    *,
    allow_unsafe_versions: bool = False,
    distribution_names: Iterable[str] = LIGHTNING_DISTRIBUTIONS,
    module_name: str = LIGHTNING_MODULE_NAME,
) -> LightningDependencyPreflight:
    """Inspect Lightning package metadata before importing Lightning.

    ``allow_unsafe_versions`` exists for controlled incident-response testing.
    The default blocks the advisory range before any ``lightning`` import is
    attempted.
    """

    if not isinstance(allow_unsafe_versions, bool):
        raise RemotePhysTrainingError(
            "Lightning preflight allow_unsafe_versions must be boolean.",
            owner="preflight_lightning_dependency",
            field="allow_unsafe_versions",
            expected="bool",
            actual=type(allow_unsafe_versions).__name__,
        )
    found: list[tuple[str, str, tuple[int, ...] | None]] = []
    checked: list[str] = []
    for package_name in distribution_names:
        if not isinstance(package_name, str) or not package_name:
            raise RemotePhysTrainingError(
                "Lightning distribution names must be non-empty strings.",
                owner="preflight_lightning_dependency",
                field="distribution_names",
                actual=type(package_name).__name__,
            )
        checked.append(package_name)
        try:
            version = metadata.version(package_name)
            found.append((package_name, version, _parse_version_prefix(version)))
        except metadata.PackageNotFoundError:
            continue
    if not found:
        return LightningDependencyPreflight(
            status=LightningDependencyStatus.ABSENT,
            module_name=module_name,
            reason="No Lightning package metadata found for: " + ", ".join(checked),
        )

    invalid = next((item for item in found if item[2] is None), None)
    if invalid is not None:
        package_name, version, _ = invalid
        return LightningDependencyPreflight(
            status=LightningDependencyStatus.INVALID,
            package_name=package_name,
            version=version,
            module_name=module_name,
            reason=f"Could not parse Lightning package version {version!r}.",
        )

    unsafe = next((item for item in found if item[2] is not None and item[2] > LIGHTNING_SAFE_MAX_VERSION), None)
    if unsafe is not None and not allow_unsafe_versions:
        package_name, version, _ = unsafe
        return LightningDependencyPreflight(
            status=LightningDependencyStatus.UNSAFE,
            package_name=package_name,
            version=version,
            module_name=module_name,
            reason=(
                "Lightning package version is in the GHSA-w37p-236h-pfx3 advisory range; "
                "pin to 2.6.1 or refresh the advisory before importing."
            ),
            advisory_url=LIGHTNING_SECURITY_ADVISORY_URL,
        )
    package_name, version, _ = found[0]
    return LightningDependencyPreflight(
        status=LightningDependencyStatus.AVAILABLE,
        package_name=package_name,
        version=version,
        module_name=module_name,
    )


def map_lightning_policies(
    *,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
) -> LightningPolicyMapping:
    """Map rphys optimization policies onto public Lightning Trainer kwargs."""

    if trainer_config is not None and trainer_kwargs is not None:
        raise RemotePhysTrainingError(
            "Lightning policy mapping accepts trainer_config or trainer_kwargs, not both.",
            owner="map_lightning_policies",
            field="trainer_kwargs",
        )
    config = trainer_config if trainer_config is not None else LightningTrainerConfig(trainer_kwargs)
    kwargs = config.to_kwargs()
    diagnostics: list[str] = []

    mapped_precision = _map_precision_policy(precision_policy, kwargs, diagnostics)
    mapped_compile = _map_compile_policy(compile_policy, diagnostics)
    mapped_kernel = _map_kernel_policy(kernel_policy, diagnostics)
    return LightningPolicyMapping(
        trainer_kwargs=kwargs,
        precision_policy=mapped_precision,
        compile_policy=mapped_compile,
        kernel_policy=mapped_kernel,
        diagnostics=diagnostics,
    )


def map_lightning_checkpoint_policies(
    *,
    save_policy: CheckpointSavePolicy | None = None,
    prune_policy: CheckpointPrunePolicy | None = None,
) -> LightningCheckpointMapping:
    """Map rphys checkpoint policies onto public Lightning ``ModelCheckpoint`` kwargs."""

    save_policy = _coerce_optional_checkpoint_policy(
        save_policy,
        CheckpointSavePolicy,
        field="save_policy",
    )
    prune_policy = _coerce_optional_checkpoint_policy(
        prune_policy,
        CheckpointPrunePolicy,
        field="prune_policy",
    )
    diagnostics: list[str] = []
    callback_kwargs: dict[str, object] = {}
    requires_recency_pruner = False

    if save_policy is not None:
        if not save_policy.enabled:
            diagnostics.append("checkpoint.save.disabled")
        else:
            if save_policy.by_step is not None:
                callback_kwargs["every_n_train_steps"] = save_policy.by_step
                diagnostics.append(f"checkpoint.every_n_train_steps:{save_policy.by_step}")
            if save_policy.by_epoch is not None:
                callback_kwargs["every_n_epochs"] = save_policy.by_epoch
                diagnostics.append(f"checkpoint.every_n_epochs:{save_policy.by_epoch}")
            if save_policy.by_elapsed_seconds is not None:
                callback_kwargs["train_time_interval"] = timedelta(seconds=save_policy.by_elapsed_seconds)
                diagnostics.append("checkpoint.train_time_interval")
            if save_policy.on_metric:
                callback_kwargs["monitor"] = save_policy.metric_name
                callback_kwargs["mode"] = (save_policy.metric_direction or CheckpointMetricDirection.MIN).value
                diagnostics.append(f"checkpoint.monitor:{save_policy.metric_name}")
            if save_policy.on_failure:
                callback_kwargs["save_on_exception"] = True
                diagnostics.append("checkpoint.save_on_exception")
            if save_policy.on_final:
                callback_kwargs["save_last"] = True
                diagnostics.append("checkpoint.save_last")

    if prune_policy is not None:
        if not prune_policy.enabled:
            diagnostics.append("checkpoint.prune.disabled")
        else:
            if prune_policy.keep_best is not None:
                callback_kwargs["save_top_k"] = prune_policy.keep_best
                callback_kwargs["monitor"] = prune_policy.best_metric_name
                callback_kwargs["mode"] = (
                    prune_policy.best_metric_direction or CheckpointMetricDirection.MIN
                ).value
                diagnostics.append(f"checkpoint.save_top_k:{prune_policy.keep_best}")
            if prune_policy.keep_recent is not None:
                requires_recency_pruner = True
                callback_kwargs.setdefault("save_last", True)
                if "save_top_k" not in callback_kwargs:
                    callback_kwargs["save_top_k"] = -1
                diagnostics.append(f"checkpoint.recency_pruner:{prune_policy.keep_recent}")
            if prune_policy.keep_final:
                callback_kwargs.setdefault("save_last", True)
                diagnostics.append("checkpoint.keep_final")
            if prune_policy.keep_failure:
                callback_kwargs.setdefault("save_on_exception", True)
                diagnostics.append("checkpoint.keep_failure")

    return LightningCheckpointMapping(
        callback_kwargs=callback_kwargs,
        save_policy=save_policy,
        prune_policy=prune_policy,
        requires_recency_pruner=requires_recency_pruner,
        diagnostics=diagnostics,
    )


def fit_lightning_module(
    model: object,
    *,
    train_dataloaders: object = None,
    val_dataloaders: object = None,
    datamodule: object = None,
    ckpt_path: str | None = None,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
    bridge_config: LightningBridgeConfig | None = None,
    allow_unsafe_versions: bool = False,
) -> TrainingResult:
    """Run a user-provided LightningModule/DataModule through shared results."""

    _validate_fit_data_boundary(train_dataloaders, val_dataloaders, datamodule)
    return _run_lightning_module(
        "fit",
        LoopMode.TRAIN,
        model,
        train_dataloaders=train_dataloaders,
        val_dataloaders=val_dataloaders,
        datamodule=datamodule,
        ckpt_path=ckpt_path,
        trainer_config=trainer_config,
        trainer_kwargs=trainer_kwargs,
        precision_policy=precision_policy,
        compile_policy=compile_policy,
        kernel_policy=kernel_policy,
        bridge_config=bridge_config,
        allow_unsafe_versions=allow_unsafe_versions,
    )


def validate_lightning_module(
    model: object | None = None,
    *,
    dataloaders: object = None,
    datamodule: object = None,
    ckpt_path: str | None = None,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
    bridge_config: LightningBridgeConfig | None = None,
    allow_unsafe_versions: bool = False,
) -> TrainingResult:
    """Run ``Trainer.validate`` and normalize Lightning metric output."""

    _validate_eval_data_boundary(dataloaders, datamodule, owner="validate_lightning_module")
    return _run_lightning_module(
        "validate",
        LoopMode.VALIDATE,
        model,
        dataloaders=dataloaders,
        datamodule=datamodule,
        ckpt_path=ckpt_path,
        trainer_config=trainer_config,
        trainer_kwargs=trainer_kwargs,
        precision_policy=precision_policy,
        compile_policy=compile_policy,
        kernel_policy=kernel_policy,
        bridge_config=bridge_config,
        allow_unsafe_versions=allow_unsafe_versions,
    )


def test_lightning_module(
    model: object | None = None,
    *,
    dataloaders: object = None,
    datamodule: object = None,
    ckpt_path: str | None = None,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
    bridge_config: LightningBridgeConfig | None = None,
    allow_unsafe_versions: bool = False,
) -> TrainingResult:
    """Run ``Trainer.test`` and normalize Lightning metric output."""

    _validate_eval_data_boundary(dataloaders, datamodule, owner="test_lightning_module")
    return _run_lightning_module(
        "test",
        LoopMode.TEST,
        model,
        dataloaders=dataloaders,
        datamodule=datamodule,
        ckpt_path=ckpt_path,
        trainer_config=trainer_config,
        trainer_kwargs=trainer_kwargs,
        precision_policy=precision_policy,
        compile_policy=compile_policy,
        kernel_policy=kernel_policy,
        bridge_config=bridge_config,
        allow_unsafe_versions=allow_unsafe_versions,
    )


def predict_lightning_module(
    model: object | None = None,
    *,
    dataloaders: object = None,
    datamodule: object = None,
    return_predictions: bool | None = None,
    ckpt_path: str | None = None,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
    bridge_config: LightningBridgeConfig | None = None,
    allow_unsafe_versions: bool = False,
) -> TrainingResult:
    """Run ``Trainer.predict`` and normalize shared result evidence."""

    _validate_eval_data_boundary(dataloaders, datamodule, owner="predict_lightning_module")
    return _run_lightning_module(
        "predict",
        LoopMode.PREDICT,
        model,
        dataloaders=dataloaders,
        datamodule=datamodule,
        return_predictions=return_predictions,
        ckpt_path=ckpt_path,
        trainer_config=trainer_config,
        trainer_kwargs=trainer_kwargs,
        precision_policy=precision_policy,
        compile_policy=compile_policy,
        kernel_policy=kernel_policy,
        bridge_config=bridge_config,
        allow_unsafe_versions=allow_unsafe_versions,
    )


class LightningBridgeCallback:
    """Lightning callback bridge that records shared rphys profile evidence."""

    __slots__ = (
        "_checkpoint_mapping",
        "_config",
        "_finalized",
        "_last_monitor_lifecycle_counts",
        "_mode",
        "_monitors_running",
        "_recorder",
        "_run_writers_flushed",
    )

    def __init__(
        self,
        *,
        config: LightningBridgeConfig,
        mode: LoopMode,
        checkpoint_mapping: LightningCheckpointMapping,
    ) -> None:
        if not isinstance(config, LightningBridgeConfig):
            raise RemotePhysTrainingError(
                "LightningBridgeCallback config must be a LightningBridgeConfig.",
                owner="LightningBridgeCallback",
                field="config",
                expected="LightningBridgeConfig",
                actual=type(config).__name__,
            )
        if not isinstance(checkpoint_mapping, LightningCheckpointMapping):
            raise RemotePhysTrainingError(
                "LightningBridgeCallback checkpoint_mapping must be a LightningCheckpointMapping.",
                owner="LightningBridgeCallback",
                field="checkpoint_mapping",
                expected="LightningCheckpointMapping",
                actual=type(checkpoint_mapping).__name__,
            )
        self._config = config
        self._mode = LoopMode.coerce(mode)
        self._checkpoint_mapping = checkpoint_mapping
        self._recorder = TrainingProfileRecorder()
        self._last_monitor_lifecycle_counts: dict[int, int] = {}
        self._monitors_running = False
        self._run_writers_flushed = False
        self._finalized = False
        for decision in checkpoint_mapping.diagnostics:
            self._recorder.record_decision(decision)

    @property
    def profile(self) -> TrainingProfile:
        """Return current bridge profile evidence."""

        return self._recorder.profile

    def setup(self, trainer: object, pl_module: object, stage: str | None = None) -> None:
        self._record_event(TrainingEventPhase.SETUP, status="started", trainer=trainer, metadata={"stage": stage})
        self._start_resource_monitors()
        self._collect_probes(ProbeHookPoint.SETUP, trainer=trainer, pl_module=pl_module, metadata={"stage": stage})

    def teardown(self, trainer: object, pl_module: object, stage: str | None = None) -> None:
        self._collect_probes(ProbeHookPoint.TEARDOWN, trainer=trainer, pl_module=pl_module, metadata={"stage": stage})
        self._stop_resource_monitors()
        self._flush_writers(ProfileWriterFlushScope.RUN)
        self._record_event(TrainingEventPhase.TEARDOWN, status="completed", trainer=trainer, metadata={"stage": stage})

    def on_exception(self, trainer: object, pl_module: object, exception: BaseException) -> None:
        self._record_event(
            TrainingEventPhase.LOOP_FAILED,
            status="failed",
            trainer=trainer,
            metadata={"exception": type(exception).__name__},
        )
        self._collect_probes(
            ProbeHookPoint.FAILURE,
            trainer=trainer,
            pl_module=pl_module,
            metadata={"exception": type(exception).__name__},
        )
        self._stop_resource_monitors()
        self._flush_writers(ProfileWriterFlushScope.RUN)

    def on_fit_start(self, trainer: object, pl_module: object) -> None:
        self._record_event(TrainingEventPhase.LOOP_STARTED, status="started", trainer=trainer)

    def on_fit_end(self, trainer: object, pl_module: object) -> None:
        self._record_event(TrainingEventPhase.LOOP_COMPLETED, status="completed", trainer=trainer)

    def on_train_batch_start(self, trainer: object, pl_module: object, batch: object, batch_idx: int) -> None:
        self._record_event(
            TrainingEventPhase.STEP_STARTED,
            status="started",
            trainer=trainer,
            batch_index=batch_idx,
            step_index=_trainer_global_step(trainer),
        )
        self._collect_resource_samples()
        self._collect_probes(
            ProbeHookPoint.BATCH_FETCH,
            trainer=trainer,
            pl_module=pl_module,
            batch=batch,
            batch_index=batch_idx,
        )
        self._collect_probes(
            ProbeHookPoint.PRE_DEVICE_TRANSFER,
            trainer=trainer,
            pl_module=pl_module,
            batch=batch,
            batch_index=batch_idx,
        )

    def on_train_batch_end(
        self,
        trainer: object,
        pl_module: object,
        outputs: object,
        batch: object,
        batch_idx: int,
    ) -> None:
        self._collect_probes(
            ProbeHookPoint.POST_DEVICE_TRANSFER,
            trainer=trainer,
            pl_module=pl_module,
            batch=batch,
            outputs=outputs,
            batch_index=batch_idx,
        )
        self._collect_probes(
            ProbeHookPoint.STEP_COMPLETED,
            trainer=trainer,
            pl_module=pl_module,
            batch=batch,
            outputs=outputs,
            batch_index=batch_idx,
        )
        self._collect_resource_samples()
        self._record_event(
            TrainingEventPhase.STEP_COMPLETED,
            status="completed",
            trainer=trainer,
            batch_index=batch_idx,
            step_index=_trainer_global_step(trainer),
        )
        self._flush_writers(ProfileWriterFlushScope.STEP)

    def on_validation_batch_start(self, trainer: object, pl_module: object, batch: object, batch_idx: int) -> None:
        self._record_event(
            TrainingEventPhase.VALIDATION,
            status="batch_started",
            trainer=trainer,
            batch_index=batch_idx,
        )
        self._collect_probes(
            ProbeHookPoint.VALIDATION,
            trainer=trainer,
            pl_module=pl_module,
            batch=batch,
            batch_index=batch_idx,
        )

    def on_before_backward(self, trainer: object, pl_module: object, loss: object) -> None:
        self._collect_probes(ProbeHookPoint.BACKWARD, trainer=trainer, pl_module=pl_module, loss=loss)

    def on_after_backward(self, trainer: object, pl_module: object) -> None:
        self._record_span("lightning.backward", trainer=trainer)

    def on_before_optimizer_step(self, trainer: object, pl_module: object, optimizer: object) -> None:
        self._collect_probes(ProbeHookPoint.OPTIMIZER_STEP, trainer=trainer, pl_module=pl_module, optimizer=optimizer)
        self._record_span("lightning.optimizer_step", trainer=trainer)

    def on_save_checkpoint(self, trainer: object, pl_module: object, checkpoint: dict[str, object]) -> None:
        self._record_event(
            TrainingEventPhase.CHECKPOINT,
            status="save_attempted",
            trainer=trainer,
            metadata={"checkpoint_keys": ",".join(sorted(str(key) for key in checkpoint.keys()))},
        )
        self._recorder.record_checkpoint_result(
            CheckpointSaveResult(
                status=CheckpointResultStatus.ATTEMPTED,
                reason="lightning_on_save_checkpoint",
                **self._result_context(trainer),
            )
        )

    def on_load_checkpoint(self, trainer: object, pl_module: object, checkpoint: dict[str, object]) -> None:
        self._record_event(
            TrainingEventPhase.CHECKPOINT,
            status="load_attempted",
            trainer=trainer,
            metadata={"checkpoint_keys": ",".join(sorted(str(key) for key in checkpoint.keys()))},
        )
        self._recorder.record_checkpoint_result(
            CheckpointRestoreResult(
                status=CheckpointResultStatus.ATTEMPTED,
                mode=CheckpointRestoreMode.EXPLICIT,
                reason="lightning_on_load_checkpoint",
                **self._result_context(trainer),
            )
        )

    def finalize(self, trainer: object, checkpoint_callback: object | None = None) -> None:
        """Collect end-of-run checkpoint, monitor, and writer evidence."""

        if self._finalized:
            return
        self._collect_checkpoint_callback_evidence(trainer, checkpoint_callback)
        self._stop_resource_monitors()
        self._flush_writers(ProfileWriterFlushScope.RUN)
        self._finalized = True

    def _record_event(
        self,
        phase: TrainingEventPhase,
        *,
        status: str,
        trainer: object,
        batch_index: int | None = None,
        step_index: int | None = None,
        metadata: Mapping[object, object] | None = None,
    ) -> None:
        event = TrainingEvent(
            phase,
            self._mode,
            status=status,
            epoch_index=_trainer_current_epoch(trainer),
            step_index=step_index,
            batch_index=batch_index,
            metadata=_merge_metadata(metadata, self._rank_metadata(trainer)),
            provenance={"engine": "LightningTrainingEngine", "bridge": "callback"},
            **self._event_context(trainer),
        )
        self._recorder.record_event(event)
        self._append_writer_record(event)

    def _record_span(self, stage_name: str, *, trainer: object) -> None:
        span = ProfileSpanSummary(
            stage_name,
            mode=self._mode,
            status="available",
            duration_seconds=0.0,
            metadata=self._rank_metadata(trainer),
            provenance={"engine": "LightningTrainingEngine", "bridge": "callback"},
            **self._event_context(trainer),
        )
        self._recorder.record_scalar_span(span)
        self._append_writer_record(span)

    def _collect_probes(
        self,
        hook_point: ProbeHookPoint,
        *,
        trainer: object,
        pl_module: object,
        batch: object | None = None,
        outputs: object | None = None,
        loss: object | None = None,
        optimizer: object | None = None,
        batch_index: int | None = None,
        metadata: Mapping[object, object] | None = None,
    ) -> None:
        if not self._config.training_probes:
            return
        context = {
            "hook_point": hook_point,
            "trainer": trainer,
            "pl_module": pl_module,
            "batch": batch,
            "outputs": outputs,
            "loss": loss,
            "optimizer": optimizer,
            "mode": self._mode,
            "batch_index": batch_index,
            "metadata": _merge_metadata(metadata, self._rank_metadata(trainer)),
            **self._result_context(trainer),
        }
        for probe in self._config.training_probes:
            try:
                results = probe.collect(context)
            except Exception as exc:
                self._recorder.record_probe_result(
                    UnavailableProbeEvidence(
                        _probe_id(probe),
                        reason=f"{type(exc).__name__}: {exc}",
                        hook_point=hook_point,
                        selector=ProbeSelector(ProbeSelectorMode.ALL),
                        failure_policy=ProbeFailurePolicy.RECORD_AND_CONTINUE,
                        metadata={"bridge": "lightning"},
                        provenance={"engine": "LightningTrainingEngine"},
                        **self._result_context(trainer),
                    )
                )
                continue
            for result in results:
                self._recorder.record_probe_result(result)
                self._append_writer_record(result)

    def _start_resource_monitors(self) -> None:
        if self._monitors_running:
            return
        for monitor in self._config.resource_monitors:
            monitor.configure()
            monitor.start()
            self._record_new_monitor_lifecycle(monitor)
        self._monitors_running = bool(self._config.resource_monitors)

    def _collect_resource_samples(self) -> None:
        for monitor in self._config.resource_monitors:
            sample = monitor.collect_sample()
            if sample is not None:
                self._recorder.record_resource_sample(sample)
                self._append_writer_record(sample)
            self._record_new_monitor_lifecycle(monitor)

    def _stop_resource_monitors(self) -> None:
        if not self._monitors_running:
            return
        for monitor in self._config.resource_monitors:
            monitor.request_flush()
            monitor.stop()
            self._record_new_monitor_lifecycle(monitor)
        self._monitors_running = False

    def _record_new_monitor_lifecycle(self, monitor: ResourceMonitor) -> None:
        key = id(monitor)
        last_count = self._last_monitor_lifecycle_counts.get(key, 0)
        events = monitor.lifecycle_events
        for record in events[last_count:]:
            self._recorder.record_monitor_lifecycle_record(record)
            self._append_writer_record(record)
        self._last_monitor_lifecycle_counts[key] = len(events)

    def _append_writer_record(self, record: object) -> None:
        for writer in self._config.profile_writers:
            append_result = writer.append(record)
            self._recorder.record_writer_result(append_result)

    def _flush_writers(self, scope: ProfileWriterFlushScope) -> None:
        if scope is ProfileWriterFlushScope.RUN and self._run_writers_flushed:
            return
        for writer in self._config.profile_writers:
            self._recorder.record_writer_result(writer.flush(scope))
        if scope is ProfileWriterFlushScope.RUN:
            self._run_writers_flushed = True

    def _collect_checkpoint_callback_evidence(self, trainer: object, checkpoint_callback: object | None) -> None:
        if checkpoint_callback is None:
            return
        ref_id = _checkpoint_ref_id(checkpoint_callback)
        if ref_id is not None:
            self._recorder.record_checkpoint_result(
                CheckpointSaveResult(
                    status=CheckpointResultStatus.COMPLETED,
                    ref_id=ref_id,
                    retention_policy_applied="lightning_model_checkpoint",
                    reason="lightning_callback_reported_checkpoint",
                    metadata={"best_model_path": _safe_str(getattr(checkpoint_callback, "best_model_path", None))},
                    provenance={"engine": "LightningTrainingEngine"},
                    **self._result_context(trainer),
                )
            )
        if self._checkpoint_mapping.requires_recency_pruner:
            self._recorder.record_checkpoint_result(
                CheckpointPruneResult(
                    status=CheckpointResultStatus.ATTEMPTED,
                    keep_count=(
                        self._checkpoint_mapping.prune_policy.keep_recent
                        if self._checkpoint_mapping.prune_policy
                        else None
                    ),
                    metadata={"bridge": "lightning_recency_pruner"},
                    provenance={"engine": "LightningTrainingEngine"},
                    **self._result_context(trainer),
                )
            )

    def _event_context(self, trainer: object) -> dict[str, object]:
        context = self._result_context(trainer)
        return {
            "run_id": context["run_id"],
            "timeline_id": context["timeline_id"],
            "process_id": context["process_id"],
            "node_id": context["node_id"],
            "local_rank": context["local_rank"],
            "global_rank": context["global_rank"],
            "device_id": context["device_id"],
        }

    def _result_context(self, trainer: object) -> dict[str, object]:
        return {
            "run_id": self._config.run_id,
            "timeline_id": self._config.timeline_id or "lightning",
            "process_id": self._config.process_id,
            "node_id": self._config.node_id,
            "local_rank": (
                self._config.local_rank
                if self._config.local_rank is not None
                else _optional_int_attr(trainer, "local_rank")
            ),
            "global_rank": (
                self._config.global_rank
                if self._config.global_rank is not None
                else _optional_int_attr(trainer, "global_rank")
            ),
            "device_id": self._config.device_id,
        }

    def _rank_metadata(self, trainer: object) -> dict[str, PrimitiveValue]:
        context = self._result_context(trainer)
        return {
            key: value
            for key, value in {
                "local_rank": context["local_rank"],
                "global_rank": context["global_rank"],
                "device_id": context["device_id"],
            }.items()
            if value is not None
        }


class LightningProfilerBridge:
    """Minimal Lightning profiler bridge that records public start/stop actions."""

    __slots__ = ("_active", "_mode", "_recorder")

    def __init__(self, *, mode: LoopMode) -> None:
        self._mode = LoopMode.coerce(mode)
        self._recorder = TrainingProfileRecorder()
        self._active: dict[str, float] = {}

    @property
    def training_profile(self) -> TrainingProfile:
        """Return profiler span evidence."""

        return self._recorder.profile

    def setup(self, stage: str, local_rank: int | None = None, log_dir: str | None = None) -> None:
        self._recorder.record_decision(f"lightning_profiler_setup:{stage}")
        if local_rank is not None:
            self._recorder.record_decision(f"lightning_profiler_local_rank:{local_rank}")
        if log_dir:
            self._recorder.record_decision("lightning_profiler_log_dir:configured")

    def start(self, action_name: str) -> None:
        self._active[action_name] = float(len(self._active))

    def stop(self, action_name: str) -> None:
        start = self._active.pop(action_name, 0.0)
        self._recorder.record_scalar_span(
            ProfileSpanSummary(
                f"lightning.profiler.{action_name}",
                mode=self._mode,
                status="available",
                duration_seconds=max(0.0, float(len(self._active)) - start),
                provenance={"engine": "LightningTrainingEngine", "bridge": "profiler"},
            )
        )

    def teardown(self, stage: str) -> None:
        self._recorder.record_decision(f"lightning_profiler_teardown:{stage}")

    def describe(self) -> None:
        self._recorder.record_decision("lightning_profiler_describe")

    @contextmanager
    def profile(self, action_name: str) -> Generator[str, None, None]:
        """Profile a public Lightning action scope."""

        self.start(action_name)
        try:
            yield action_name
        finally:
            self.stop(action_name)

    def summary(self) -> str:
        """Return an intentionally empty Lightning-compatible text summary."""

        return ""


def _run_lightning_module(
    method_name: str,
    mode: LoopMode,
    model: object | None,
    *,
    train_dataloaders: object = None,
    val_dataloaders: object = None,
    dataloaders: object = None,
    datamodule: object = None,
    return_predictions: bool | None = None,
    ckpt_path: str | None = None,
    trainer_config: LightningTrainerConfig | None = None,
    trainer_kwargs: Mapping[str, object] | None = None,
    precision_policy: PrecisionPolicy | None = None,
    compile_policy: CompilePolicy | None = None,
    kernel_policy: KernelPolicy | None = None,
    bridge_config: LightningBridgeConfig | None = None,
    allow_unsafe_versions: bool = False,
) -> TrainingResult:
    mapping = map_lightning_policies(
        trainer_config=trainer_config,
        trainer_kwargs=trainer_kwargs,
        precision_policy=precision_policy,
        compile_policy=compile_policy,
        kernel_policy=kernel_policy,
    )
    preflight = preflight_lightning_dependency(allow_unsafe_versions=allow_unsafe_versions)
    if not preflight.available:
        return _preflight_failed_result(mode, preflight, mapping)
    try:
        lightning_api = _load_lightning(preflight=preflight)
        return _run_lightning_trainer(
            lightning_api,
            method_name=method_name,
            mode=mode,
            model=model,
            trainer_kwargs=mapping.to_kwargs(),
            train_dataloaders=train_dataloaders,
            val_dataloaders=val_dataloaders,
            dataloaders=dataloaders,
            datamodule=datamodule,
            return_predictions=return_predictions,
            ckpt_path=ckpt_path,
            policy_mapping=mapping,
            preflight=preflight,
            bridge_config=bridge_config,
        )
    except Exception as exc:  # pragma: no cover - exercised with fake failures in tests.
        return _failed_result(mode, exc, mapping, preflight=preflight)


def _run_lightning_trainer(
    lightning_api: object,
    *,
    method_name: str,
    mode: LoopMode,
    model: object | None,
    trainer_kwargs: Mapping[str, object],
    policy_mapping: LightningPolicyMapping,
    preflight: LightningDependencyPreflight,
    train_dataloaders: object = None,
    val_dataloaders: object = None,
    dataloaders: object = None,
    datamodule: object = None,
    return_predictions: bool | None = None,
    ckpt_path: str | None = None,
    bridge_config: LightningBridgeConfig | None = None,
) -> TrainingResult:
    bridge_config = _coerce_optional_bridge_config(bridge_config)
    checkpoint_mapping = map_lightning_checkpoint_policies(
        save_policy=bridge_config.checkpoint_save_policy if bridge_config is not None else None,
        prune_policy=bridge_config.checkpoint_prune_policy if bridge_config is not None else None,
    )
    bridge_callback = (
        LightningBridgeCallback(
            config=bridge_config,
            mode=mode,
            checkpoint_mapping=checkpoint_mapping,
        )
        if bridge_config is not None and bridge_config.enabled
        else None
    )
    profiler_bridge = LightningProfilerBridge(mode=mode) if bridge_callback is not None else None
    checkpoint_callback = _build_checkpoint_callback(lightning_api, checkpoint_mapping)
    if (
        bridge_callback is not None
        and checkpoint_mapping.callback_kwargs
        and checkpoint_callback is None
    ):
        bridge_callback._recorder.record_decision("checkpoint.model_checkpoint_unavailable")
    selected_ckpt_path, selection_result, restore_result = _resolve_lightning_ckpt_path(
        bridge_config,
        explicit_ckpt_path=ckpt_path,
    )
    if bridge_callback is not None:
        if selection_result is not None:
            bridge_callback._recorder.record_checkpoint_result(selection_result)
        if restore_result is not None:
            bridge_callback._recorder.record_checkpoint_result(restore_result)
    resolved_trainer_kwargs = _with_bridge_trainer_kwargs(
        trainer_kwargs,
        bridge_callback=bridge_callback,
        profiler_bridge=profiler_bridge,
        checkpoint_callback=checkpoint_callback,
    )
    try:
        trainer_type = getattr(lightning_api, "Trainer", None)
        if not callable(trainer_type):
            raise RemotePhysDependencyError(
                "lightning.pytorch.Trainer is unavailable or invalid.",
                dependency="lightning",
                module=LIGHTNING_MODULE_NAME,
                attribute="Trainer",
                actual=type(trainer_type).__name__,
            )
        trainer = trainer_type(**resolved_trainer_kwargs)
        method = getattr(trainer, method_name)
    except Exception as exc:
        return _failed_result(
            mode,
            exc,
            policy_mapping,
            preflight=preflight,
            bridge_profile=_bridge_profile(bridge_callback, profiler_bridge),
        )
    kwargs: dict[str, object] = {}
    if method_name == "fit":
        kwargs = {
            "train_dataloaders": train_dataloaders,
            "val_dataloaders": val_dataloaders,
            "datamodule": datamodule,
            "ckpt_path": selected_ckpt_path,
        }
    elif method_name in {"validate", "test"}:
        kwargs = {
            "dataloaders": dataloaders,
            "datamodule": datamodule,
            "ckpt_path": selected_ckpt_path,
        }
    elif method_name == "predict":
        kwargs = {
            "dataloaders": dataloaders,
            "datamodule": datamodule,
            "return_predictions": return_predictions,
            "ckpt_path": selected_ckpt_path,
        }
    try:
        output = method(model, **{key: value for key, value in kwargs.items() if value is not None})
    except Exception as exc:
        if bridge_callback is not None:
            bridge_callback.on_exception(trainer, model, exc)
            bridge_callback.finalize(trainer, checkpoint_callback)
        return _failed_result(
            mode,
            exc,
            policy_mapping,
            preflight=preflight,
            bridge_profile=_bridge_profile(bridge_callback, profiler_bridge),
        )
    if bridge_callback is not None:
        bridge_callback.finalize(trainer, checkpoint_callback)
    return _completed_result(
        mode,
        output,
        trainer=trainer,
        mapping=policy_mapping,
        preflight=preflight,
        bridge_profile=_bridge_profile(bridge_callback, profiler_bridge),
    )


def _build_engine_module(
    lightning_api: object,
    plan: TrainingPlan,
    learner: Learner,
    mode: LoopMode,
    *,
    module_factory: LightningModuleFactory | None,
) -> object:
    if module_factory is not None:
        return module_factory(lightning_api, plan, learner, mode)
    base = getattr(lightning_api, "LightningModule", object)
    if not isinstance(base, type):
        base = object

    class RPhysLightningModule(base):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            try:
                super().__init__()  # type: ignore[misc]
            except TypeError:
                pass
            self._rphys_plan = plan
            self._rphys_learner = learner

        def training_step(self, batch: object, batch_idx: int) -> object:
            return self._rphys_step(batch, LoopMode.TRAIN, batch_idx)

        def validation_step(self, batch: object, batch_idx: int) -> object:
            return self._rphys_step(batch, LoopMode.VALIDATE, batch_idx)

        def test_step(self, batch: object, batch_idx: int) -> object:
            return self._rphys_step(batch, LoopMode.TEST, batch_idx)

        def predict_step(self, batch: object, batch_idx: int, dataloader_idx: int = 0) -> object:
            return self._rphys_step(batch, LoopMode.PREDICT, batch_idx)

        def configure_optimizers(self) -> object:
            optimizer = self._rphys_plan.optimizer
            scheduler = self._rphys_plan.scheduler
            if optimizer is None:
                return None
            if scheduler is None:
                return optimizer
            return [optimizer], [scheduler]

        def _rphys_step(self, batch: object, step_mode: LoopMode, batch_idx: int) -> object:
            if not isinstance(batch, Batch):
                raise RemotePhysTrainingError(
                    "LightningTrainingEngine learner wrapper requires Batch inputs.",
                    owner="LightningTrainingEngine",
                    field="batch",
                    expected="Batch",
                    actual=type(batch).__name__,
                )
            output = self._rphys_learner.step(
                batch,
                LoopContext(
                    step_mode,
                    batch_index=batch_idx,
                    step_index=batch_idx,
                    metadata={"engine": "LightningTrainingEngine"},
                ),
            )
            if not isinstance(output, Batch):
                raise RemotePhysTrainingError(
                    "LightningTrainingEngine learner wrapper requires Batch outputs.",
                    owner="LightningTrainingEngine",
                    field="learner",
                    expected="Batch",
                    actual=type(output).__name__,
                )
            validated = self._rphys_plan.output_spec.validate_batch(output, step_mode)
            objective = self._rphys_plan.output_spec.objective_value(validated, step_mode)
            if objective is not None:
                return objective
            metrics = self._rphys_plan.output_spec.metric_values(validated)
            return {name: _primitive_metric_value(value) for name, value in metrics.items()}

    return RPhysLightningModule()


def _load_lightning(*, preflight: LightningDependencyPreflight) -> object:
    if not preflight.available:
        raise RemotePhysDependencyError(
            "Lightning dependency is unavailable or unsafe.",
            dependency="lightning",
            module=preflight.module_name,
            status=preflight.status.value,
            reason=preflight.reason,
        )
    try:
        return importlib.import_module(preflight.module_name)
    except ImportError as exc:
        raise RemotePhysDependencyError(
            "Lightning package metadata exists but lightning.pytorch could not be imported.",
            dependency=preflight.package_name,
            module=preflight.module_name,
            version=preflight.version,
        ) from exc


def _map_precision_policy(
    policy: PrecisionPolicy | None,
    trainer_kwargs: dict[str, object],
    diagnostics: list[str],
) -> PrecisionPolicy | None:
    if policy is None:
        return None
    _coerce_optional_policy(policy, PrecisionPolicy, field="precision_policy")
    if policy.status is PolicyStatus.DISABLED:
        diagnostics.append("precision.disabled")
        return policy
    if policy.status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE}:
        diagnostics.append(f"precision.{policy.status.value}")
        return policy
    requested = policy.requested_precision
    if requested is None:
        return PrecisionPolicy(
            status=PolicyStatus.UNSUPPORTED,
            backend="lightning",
            supported_backends=("lightning",),
            unsupported_reason="Lightning precision mapping requires requested_precision.",
            provenance={"engine": "LightningTrainingEngine"},
        )
    mapped = _LIGHTNING_PRECISION_ALIASES.get(requested.lower())
    if mapped is None or mapped not in _LIGHTNING_PRECISION_VALUES:
        diagnostics.append(f"precision.unsupported:{requested}")
        return PrecisionPolicy(
            requested,
            status=PolicyStatus.UNSUPPORTED,
            backend="lightning",
            supported_backends=("lightning",),
            unsupported_reason=f"Lightning Trainer does not expose precision={requested!r}.",
            metadata={"requested_precision": requested},
            provenance={"engine": "LightningTrainingEngine"},
        )
    existing = trainer_kwargs.get("precision")
    if existing is not None and existing != mapped:
        raise RemotePhysTrainingError(
            "Lightning trainer precision conflicts with PrecisionPolicy.",
            owner="map_lightning_policies",
            field="precision",
            requested_precision=requested,
            mapped_precision=mapped,
            trainer_precision=existing,
        )
    trainer_kwargs["precision"] = mapped
    diagnostics.append(f"precision.applied:{mapped}")
    return PrecisionPolicy(
        requested,
        applied_precision=mapped,
        status=PolicyStatus.APPLIED,
        backend="lightning",
        supported_backends=("lightning",),
        numerical_equivalence=policy.numerical_equivalence,
        metadata=dict(policy.metadata),
        provenance={"engine": "LightningTrainingEngine", "source_policy_status": policy.status.value},
    )


def _map_compile_policy(policy: CompilePolicy | None, diagnostics: list[str]) -> CompilePolicy | None:
    if policy is None:
        return None
    _coerce_optional_policy(policy, CompilePolicy, field="compile_policy")
    if policy.status is PolicyStatus.DISABLED:
        diagnostics.append("compile.disabled")
        return policy
    if policy.status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE}:
        diagnostics.append(f"compile.{policy.status.value}")
        return policy
    requested = policy.requested_mode
    diagnostics.append("compile.unsupported:trainer_kwarg_absent")
    return CompilePolicy(
        requested,
        status=PolicyStatus.UNSUPPORTED,
        backend="lightning",
        supported_backends=("lightning",),
        backend_equivalence_note=policy.backend_equivalence_note,
        unsupported_reason=(
            "Phase 6 maps only public Lightning Trainer settings; torch.compile is a model boundary."
        ),
        metadata=dict(policy.metadata),
        provenance={"engine": "LightningTrainingEngine", "source_policy_status": policy.status.value},
    )


def _map_kernel_policy(policy: KernelPolicy | None, diagnostics: list[str]) -> KernelPolicy | None:
    if policy is None:
        return None
    _coerce_optional_policy(policy, KernelPolicy, field="kernel_policy")
    if policy.status is PolicyStatus.DISABLED:
        diagnostics.append("kernel.disabled")
        return policy
    if policy.status in {PolicyStatus.UNSUPPORTED, PolicyStatus.UNAVAILABLE}:
        diagnostics.append(f"kernel.{policy.status.value}")
        return policy
    requested = policy.requested_kernel
    diagnostics.append("kernel.unsupported:trainer_kwarg_absent")
    return KernelPolicy(
        requested,
        status=PolicyStatus.UNSUPPORTED,
        backend="lightning",
        supported_backends=("lightning",),
        backend_scope=policy.backend_scope,
        unsupported_reason="Lightning Trainer does not expose a public kernel-selection setting.",
        metadata=dict(policy.metadata),
        provenance={"engine": "LightningTrainingEngine", "source_policy_status": policy.status.value},
    )


def _coerce_optional_bridge_config(value: LightningBridgeConfig | None) -> LightningBridgeConfig | None:
    if value is None or isinstance(value, LightningBridgeConfig):
        return value
    raise RemotePhysTrainingError(
        "Lightning bridge_config must be a LightningBridgeConfig when provided.",
        owner="LightningTrainingEngine",
        field="bridge_config",
        expected="LightningBridgeConfig | None",
        actual=type(value).__name__,
    )


def _with_bridge_trainer_kwargs(
    trainer_kwargs: Mapping[str, object],
    *,
    bridge_callback: LightningBridgeCallback | None,
    profiler_bridge: LightningProfilerBridge | None,
    checkpoint_callback: object | None,
) -> dict[str, object]:
    kwargs = dict(trainer_kwargs)
    callbacks: list[object] = []
    existing_callbacks = kwargs.get("callbacks")
    if existing_callbacks is None:
        callbacks = []
    elif isinstance(existing_callbacks, (list, tuple)):
        callbacks = list(existing_callbacks)
    else:
        callbacks = [existing_callbacks]
    if checkpoint_callback is not None:
        callbacks.append(checkpoint_callback)
    if bridge_callback is not None:
        callbacks.append(bridge_callback)
    if callbacks:
        kwargs["callbacks"] = callbacks

    if profiler_bridge is not None:
        if kwargs.get("profiler") is None:
            kwargs["profiler"] = profiler_bridge
        elif bridge_callback is not None:
            bridge_callback._recorder.record_decision(
                "lightning_profiler_bridge:trainer_profiler_already_configured"
            )
    return kwargs


def _build_checkpoint_callback(
    lightning_api: object,
    checkpoint_mapping: LightningCheckpointMapping,
) -> object | None:
    if not checkpoint_mapping.callback_kwargs:
        return None
    callbacks_module = getattr(lightning_api, "callbacks", None)
    checkpoint_type = getattr(callbacks_module, "ModelCheckpoint", None)
    if checkpoint_type is None:
        checkpoint_type = getattr(lightning_api, "ModelCheckpoint", None)
    if not callable(checkpoint_type):
        return None
    return checkpoint_type(**checkpoint_mapping.to_kwargs())


def _resolve_lightning_ckpt_path(
    bridge_config: LightningBridgeConfig | None,
    *,
    explicit_ckpt_path: str | None,
) -> tuple[str | None, CheckpointSelectionResult | None, CheckpointRestoreResult | None]:
    explicit_ckpt_path = coerce_optional_non_empty_string(
        explicit_ckpt_path,
        owner="LightningTrainingEngine",
        field="ckpt_path",
    )
    if bridge_config is None:
        return explicit_ckpt_path, None, None

    context = _bridge_result_context(bridge_config)
    if explicit_ckpt_path is not None:
        return (
            explicit_ckpt_path,
            None,
            CheckpointRestoreResult(
                status=CheckpointResultStatus.ATTEMPTED,
                mode=CheckpointRestoreMode.EXPLICIT,
                reason="explicit_ckpt_path",
                metadata={"ckpt_path": explicit_ckpt_path},
                provenance={"engine": "LightningTrainingEngine"},
                **context,
            ),
        )

    selection = bridge_config.checkpoint_restore_selection
    restore_policy = bridge_config.checkpoint_restore_policy
    if selection is None and restore_policy is not None:
        selection = _selection_from_restore_policy(restore_policy)
    if selection is None:
        return None, None, None

    selection_result = bridge_config.checkpoint_catalog.select(selection)
    restore_mode = restore_policy.mode if restore_policy is not None else CheckpointRestoreMode.CATALOG
    selected_ref = selection_result.ref
    if selected_ref is None:
        return (
            None,
            selection_result,
            CheckpointRestoreResult(
                status=CheckpointResultStatus.UNAVAILABLE,
                mode=restore_mode,
                reason=selection_result.reason or "checkpoint_selection_unavailable",
                provenance={"engine": "LightningTrainingEngine"},
                **context,
            ),
        )

    selected_path = selected_ref.path or selected_ref.uri
    if selected_path is None:
        return (
            None,
            selection_result,
            CheckpointRestoreResult(
                status=CheckpointResultStatus.UNAVAILABLE,
                mode=restore_mode,
                ref_id=selected_ref.ref_id,
                reason="selected_checkpoint_has_no_path_or_uri",
                provenance={"engine": "LightningTrainingEngine"},
                **context,
            ),
        )

    return (
        selected_path,
        selection_result,
        CheckpointRestoreResult(
            status=CheckpointResultStatus.COMPLETED,
            mode=restore_mode,
            ref_id=selected_ref.ref_id,
            reason="lightning_ckpt_path_selected",
            metadata={"ckpt_path": selected_path},
            provenance={"engine": "LightningTrainingEngine"},
            **context,
        ),
    )


def _selection_from_restore_policy(policy: CheckpointRestorePolicy) -> CheckpointSelection | None:
    if policy.selector in {
        CheckpointSelectionMode.LATEST_COMPLETED,
        CheckpointSelectionMode.FINAL,
        CheckpointSelectionMode.FAILURE,
    }:
        return CheckpointSelection(policy.selector, stream_id=policy.preferred_stream_id)
    return None


def _bridge_profile(
    bridge_callback: LightningBridgeCallback | None,
    profiler_bridge: LightningProfilerBridge | None,
) -> TrainingProfile | None:
    profiles = []
    if bridge_callback is not None:
        profiles.append(bridge_callback.profile)
    if profiler_bridge is not None:
        profiles.append(profiler_bridge.training_profile)
    if not profiles:
        return None
    merged = profiles[0]
    for profile in profiles[1:]:
        merged = _merge_profiles(merged, profile)
    return merged


def _merge_profiles(left: TrainingProfile, right: TrainingProfile) -> TrainingProfile:
    return TrainingProfile(
        event_logs=left.event_logs + right.event_logs,
        scalar_spans=left.scalar_spans + right.scalar_spans,
        unavailable_spans=left.unavailable_spans + right.unavailable_spans,
        resource_traces=left.resource_traces + right.resource_traces,
        monitor_lifecycle_records=left.monitor_lifecycle_records + right.monitor_lifecycle_records,
        writer_results=left.writer_results + right.writer_results,
        probe_results=left.probe_results + right.probe_results,
        checkpoint_results=left.checkpoint_results + right.checkpoint_results,
        decisions=left.decisions + right.decisions,
    )


def _bridge_result_context(config: LightningBridgeConfig) -> dict[str, object]:
    return {
        "run_id": config.run_id,
        "timeline_id": config.timeline_id or "lightning",
        "process_id": config.process_id,
        "node_id": config.node_id,
        "local_rank": config.local_rank,
        "global_rank": config.global_rank,
        "device_id": config.device_id,
    }


def _merge_metadata(
    *mappings: Mapping[object, object] | None,
) -> dict[str, PrimitiveValue]:
    merged: dict[str, PrimitiveValue] = {}
    for mapping in mappings:
        if mapping is None:
            continue
        for raw_key, raw_value in mapping.items():
            key = raw_key if isinstance(raw_key, str) else str(raw_key)
            if not key:
                continue
            if raw_value is None or isinstance(raw_value, (str, int, float, bool)):
                merged[key] = raw_value
            else:
                merged[key] = repr(raw_value)
    return merged


def _trainer_global_step(trainer: object) -> int | None:
    return _optional_int_attr(trainer, "global_step")


def _trainer_current_epoch(trainer: object) -> int | None:
    return _optional_int_attr(trainer, "current_epoch")


def _optional_int_attr(value: object, name: str) -> int | None:
    raw_value = getattr(value, name, None)
    if raw_value is None or isinstance(raw_value, bool) or not isinstance(raw_value, int):
        return None
    if raw_value < 0:
        return None
    return raw_value


def _probe_id(probe: object) -> str:
    raw_value = getattr(probe, "probe_id", None)
    if isinstance(raw_value, str) and raw_value:
        return raw_value
    return type(probe).__name__ or "training_probe"


def _checkpoint_ref_id(checkpoint_callback: object) -> str | None:
    for attribute in ("last_model_path", "best_model_path"):
        value = _safe_str(getattr(checkpoint_callback, attribute, None))
        if value is not None:
            return value
    best_k_paths = getattr(checkpoint_callback, "best_k_models", None)
    if isinstance(best_k_paths, Mapping) and best_k_paths:
        first_key = next(iter(best_k_paths.keys()))
        return _safe_str(first_key)
    return None


def _safe_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    resolved = str(value)
    return resolved or None


def _completed_result(
    mode: LoopMode,
    output: object,
    *,
    trainer: object,
    mapping: LightningPolicyMapping,
    preflight: LightningDependencyPreflight,
    bridge_profile: TrainingProfile | None = None,
) -> TrainingResult:
    return TrainingResult(
        status=TrainingStatus.COMPLETED,
        mode=mode,
        epoch_count=_coerce_counter(getattr(trainer, "current_epoch", 0), field="current_epoch"),
        step_count=_coerce_counter(getattr(trainer, "global_step", 0), field="global_step"),
        metrics=_metric_summaries(output, mode),
        events=(
            TrainingEventSummary(
                "lightning.preflight",
                status=preflight.status.value,
                metadata={"package": preflight.package_name, "version": preflight.version},
            ),
            TrainingEventSummary(f"lightning.{mode.value}", status="completed"),
        ),
        training_profile=_profile_from_mapping(
            mapping,
            preflight=preflight,
            bridge_profile=bridge_profile,
        ),
        provenance={"engine": "LightningTrainingEngine", "lightning_module": preflight.module_name},
    )


def _failed_result(
    mode: LoopMode,
    exc: Exception,
    mapping: LightningPolicyMapping,
    *,
    preflight: LightningDependencyPreflight,
    bridge_profile: TrainingProfile | None = None,
) -> TrainingResult:
    return TrainingResult(
        status=TrainingStatus.FAILED,
        mode=mode,
        failure=f"{type(exc).__name__}: {exc}",
        events=(
            TrainingEventSummary(
                "lightning.preflight",
                status=preflight.status.value,
                metadata={"package": preflight.package_name, "version": preflight.version},
            ),
            TrainingEventSummary(f"lightning.{mode.value}", status="failed"),
        ),
        training_profile=_profile_from_mapping(
            mapping,
            preflight=preflight,
            unavailable_reason=f"{type(exc).__name__}: {exc}",
            bridge_profile=bridge_profile,
        ),
        provenance={"engine": "LightningTrainingEngine", "lightning_module": preflight.module_name},
    )


def _preflight_failed_result(
    mode: LoopMode,
    preflight: LightningDependencyPreflight,
    mapping: LightningPolicyMapping,
) -> TrainingResult:
    reason = preflight.reason or preflight.status.value
    return TrainingResult(
        status=TrainingStatus.FAILED,
        mode=mode,
        failure=reason,
        events=(
            TrainingEventSummary(
                "lightning.preflight",
                status=preflight.status.value,
                metadata={"package": preflight.package_name, "version": preflight.version},
            ),
        ),
        training_profile=_profile_from_mapping(mapping, preflight=preflight, unavailable_reason=reason),
        provenance={"engine": "LightningTrainingEngine", "lightning_module": preflight.module_name},
    )


def _profile_from_mapping(
    mapping: LightningPolicyMapping,
    *,
    preflight: LightningDependencyPreflight,
    unavailable_reason: str | None = None,
    bridge_profile: TrainingProfile | None = None,
) -> TrainingProfile:
    decisions = list(mapping.diagnostics)
    decisions.append(f"lightning_preflight:{preflight.status.value}")
    if preflight.package_name is not None and preflight.version is not None:
        decisions.append(f"lightning_package:{preflight.package_name}=={preflight.version}")
    unavailable = ()
    if unavailable_reason is not None:
        unavailable = (
            UnavailableProfileProbe(
                "lightning",
                reason=unavailable_reason,
                metadata={
                    "status": preflight.status.value,
                    "package": preflight.package_name,
                    "version": preflight.version,
                    "advisory_url": preflight.advisory_url,
                },
                provenance={"engine": "LightningTrainingEngine"},
            ),
        )
    profile = TrainingProfile(decisions=tuple(decisions), unavailable_spans=unavailable)
    if bridge_profile is not None:
        profile = _merge_profiles(profile, bridge_profile)
    return profile


def _metric_summaries(output: object, mode: LoopMode) -> tuple[TrainingMetricSummary, ...]:
    summaries: list[TrainingMetricSummary] = []
    for name, value in _flatten_metric_output(output, mode=mode):
        primitive = _primitive_metric_value(value)
        if primitive is None:
            continue
        summaries.append(
            TrainingMetricSummary(
                name,
                primitive,
                provenance={"engine": "LightningTrainingEngine"},
            )
        )
    return tuple(summaries)


def _flatten_metric_output(output: object, *, mode: LoopMode) -> tuple[tuple[str, object], ...]:
    if isinstance(output, Mapping):
        return tuple((str(key), value) for key, value in output.items())
    if isinstance(output, Iterable) and not isinstance(output, (str, bytes)):
        flattened: list[tuple[str, object]] = []
        for index, item in enumerate(output):
            if isinstance(item, Mapping):
                for key, value in item.items():
                    name = str(key)
                    if any(existing_name == name for existing_name, _ in flattened):
                        name = f"{mode.value}.{index}.{name}"
                    flattened.append((name, value))
        return tuple(flattened)
    return ()


def _primitive_metric_value(value: object) -> PrimitiveValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    item = getattr(value, "item", None)
    if callable(item):
        try:
            resolved = item()
        except Exception:
            return repr(value)
        if resolved is None or isinstance(resolved, (str, int, float, bool)):
            return resolved
    payload = getattr(value, "value", None)
    if payload is None or isinstance(payload, (str, int, float, bool)):
        return payload
    return repr(value)


def _validate_fit_data_boundary(
    train_dataloaders: object,
    val_dataloaders: object,
    datamodule: object,
) -> None:
    if datamodule is not None and (train_dataloaders is not None or val_dataloaders is not None):
        raise RemotePhysTrainingError(
            "fit_lightning_module accepts datamodule or dataloaders, not both.",
            owner="fit_lightning_module",
            field="datamodule",
        )


def _validate_eval_data_boundary(dataloaders: object, datamodule: object, *, owner: str) -> None:
    if datamodule is not None and dataloaders is not None:
        raise RemotePhysTrainingError(
            f"{owner} accepts datamodule or dataloaders, not both.",
            owner=owner,
            field="datamodule",
        )


def _freeze_trainer_kwargs(values: Mapping[str, object] | None) -> Mapping[str, object]:
    if values is None:
        return MappingProxyType({})
    if not isinstance(values, Mapping):
        raise RemotePhysTrainingError(
            "LightningTrainerConfig trainer_kwargs must be a mapping.",
            owner="LightningTrainerConfig",
            field="trainer_kwargs",
            actual=type(values).__name__,
        )
    copied: dict[str, object] = {}
    for key, value in values.items():
        if not isinstance(key, str) or not key:
            raise RemotePhysTrainingError(
                "LightningTrainerConfig trainer_kwargs keys must be non-empty strings.",
                owner="LightningTrainerConfig",
                field="trainer_kwargs",
                actual=type(key).__name__,
            )
        if key not in LIGHTNING_TRAINER_KWARG_NAMES:
            raise RemotePhysTrainingError(
                "Unsupported Lightning Trainer kwarg.",
                owner="LightningTrainerConfig",
                field="trainer_kwargs",
                key=key,
                expected=tuple(sorted(LIGHTNING_TRAINER_KWARG_NAMES)),
            )
        copied[key] = value
    return MappingProxyType(copied)


def _coerce_optional_policy(value: object, expected_type: type, *, field: str) -> Any:
    if value is None or isinstance(value, expected_type):
        return value
    raise RemotePhysTrainingError(
        "Lightning policy mapping received an invalid policy type.",
        owner="map_lightning_policies",
        field=field,
        expected=expected_type.__name__ + " | None",
        actual=type(value).__name__,
    )


def _coerce_optional_checkpoint_policy(value: object, expected_type: type, *, field: str) -> Any:
    if value is None or isinstance(value, expected_type):
        return value
    raise RemotePhysTrainingError(
        "Lightning checkpoint bridge received an invalid checkpoint record.",
        owner="LightningBridgeConfig",
        field=field,
        expected=expected_type.__name__ + " | None",
        actual=type(value).__name__,
    )


def _coerce_records(
    values: Iterable[object],
    expected_type: type,
    *,
    owner: str,
    field: str,
) -> tuple[object, ...]:
    try:
        records = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            expected=f"iterable of {expected_type.__name__}",
            actual=type(values).__name__,
        ) from exc
    for index, record in enumerate(records):
        if not isinstance(record, expected_type):
            raise RemotePhysTrainingError(
                f"{owner} {field} contains an invalid record.",
                owner=owner,
                field=field,
                index=index,
                expected=expected_type.__name__,
                actual=type(record).__name__,
            )
    return records


def _coerce_training_probes(values: Iterable[object]) -> tuple[object, ...]:
    try:
        probes = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            "LightningBridgeConfig training_probes must be iterable.",
            owner="LightningBridgeConfig",
            field="training_probes",
            expected="iterable of TrainingProbe",
            actual=type(values).__name__,
        ) from exc
    for index, probe in enumerate(probes):
        collect = getattr(probe, "collect", None)
        if not callable(collect):
            raise RemotePhysTrainingError(
                "LightningBridgeConfig training_probes entries must expose collect(context).",
                owner="LightningBridgeConfig",
                field="training_probes",
                index=index,
                expected="collect(context)",
                actual=type(probe).__name__,
            )
    return probes


def _set_bridge_context(
    instance: object,
    *,
    owner: str,
    run_id: str | None,
    timeline_id: str | None,
    process_id: int | None,
    node_id: str | None,
    local_rank: int | None,
    global_rank: int | None,
    device_id: str | None,
) -> None:
    object.__setattr__(
        instance,
        "run_id",
        coerce_optional_non_empty_string(run_id, owner=owner, field="run_id"),
    )
    object.__setattr__(
        instance,
        "timeline_id",
        coerce_optional_non_empty_string(timeline_id, owner=owner, field="timeline_id"),
    )
    object.__setattr__(
        instance,
        "process_id",
        _coerce_optional_non_negative_int(process_id, owner=owner, field="process_id"),
    )
    object.__setattr__(
        instance,
        "node_id",
        coerce_optional_non_empty_string(node_id, owner=owner, field="node_id"),
    )
    object.__setattr__(
        instance,
        "local_rank",
        _coerce_optional_non_negative_int(local_rank, owner=owner, field="local_rank"),
    )
    object.__setattr__(
        instance,
        "global_rank",
        _coerce_optional_non_negative_int(global_rank, owner=owner, field="global_rank"),
    )
    object.__setattr__(
        instance,
        "device_id",
        coerce_optional_non_empty_string(device_id, owner=owner, field="device_id"),
    )


def _coerce_string_tuple(values: Iterable[str], *, owner: str, field: str) -> tuple[str, ...]:
    try:
        coerced = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be iterable.",
            owner=owner,
            field=field,
            actual=type(values).__name__,
        ) from exc
    for index, value in enumerate(coerced):
        if not isinstance(value, str) or not value:
            raise RemotePhysTrainingError(
                f"{owner} {field} values must be non-empty strings.",
                owner=owner,
                field=field,
                index=index,
                actual=type(value).__name__,
            )
    return coerced


def _require_plan(plan: object) -> TrainingPlan:
    if not isinstance(plan, TrainingPlan):
        raise RemotePhysTrainingError(
            "LightningTrainingEngine requires a TrainingPlan.",
            owner="LightningTrainingEngine",
            field="plan",
            expected="TrainingPlan",
            actual=type(plan).__name__,
        )
    return plan


def _coerce_bool(
    value: bool,
    *,
    owner: str = "LightningTrainingEngine",
    field: str = "allow_unsafe_versions",
) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysTrainingError(
            f"{owner} {field} must be boolean.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_counter(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _coerce_optional_non_negative_int(value: int | None, *, owner: str, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-negative integer when provided.",
            owner=owner,
            field=field,
            expected="non-negative integer | None",
            actual=type(value).__name__,
        )
    return value


def _coerce_non_empty_string(value: str, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RemotePhysTrainingError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
            expected="non-empty string",
            actual=type(value).__name__,
        )
    return value


def _parse_version_prefix(value: str) -> tuple[int, ...] | None:
    parts: list[int] = []
    for raw_part in value.split("."):
        digits = []
        for character in raw_part:
            if not character.isdigit():
                break
            digits.append(character)
        if not digits:
            break
        parts.append(int("".join(digits)))
        if len(parts) == 3:
            break
    if not parts:
        return None
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


LightningDependencyPreflight.__hash__ = None  # type: ignore[assignment]
LightningTrainerConfig.__hash__ = None  # type: ignore[assignment]
LightningPolicyMapping.__hash__ = None  # type: ignore[assignment]
LightningCheckpointMapping.__hash__ = None  # type: ignore[assignment]
LightningBridgeConfig.__hash__ = None  # type: ignore[assignment]
