"""Optional Lightning adapter for shared rphys training results.

This module is importable without Lightning, torch, CUDA, NVML, or profiler
packages installed. It inspects package metadata before importing Lightning so
known unsafe package versions are rejected before import-time code can run.
"""

from __future__ import annotations

import importlib
import importlib.metadata as metadata
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from rphys.data import Batch
from rphys.errors import RemotePhysDependencyError, RemotePhysTrainingError
from rphys.learning import Learner, LoopContext, LoopMode

from ._validation import PrimitiveValue, coerce_optional_non_empty_string
from .plan import TrainingPlan
from .policies import CompilePolicy, KernelPolicy, PolicyStatus, PrecisionPolicy
from .profiling import TrainingProfile, UnavailableProfileProbe
from .results import TrainingEventSummary, TrainingMetricSummary, TrainingResult, TrainingStatus

__all__ = [
    "LIGHTNING_SECURITY_ADVISORY_URL",
    "LIGHTNING_TRAINER_KWARG_NAMES",
    "LightningDependencyPreflight",
    "LightningDependencyStatus",
    "LightningPolicyMapping",
    "LightningTrainerConfig",
    "LightningTrainingEngine",
    "fit_lightning_module",
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


type LightningModuleFactory = Callable[[object, TrainingPlan, Learner, LoopMode], object]


class LightningTrainingEngine:
    """Optional Lightning-backed engine returning shared ``TrainingResult`` records."""

    __slots__ = (
        "allow_unsafe_versions",
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
        allow_unsafe_versions=allow_unsafe_versions,
    )


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
) -> TrainingResult:
    trainer_type = getattr(lightning_api, "Trainer", None)
    if not callable(trainer_type):
        raise RemotePhysDependencyError(
            "lightning.pytorch.Trainer is unavailable or invalid.",
            dependency="lightning",
            module=LIGHTNING_MODULE_NAME,
            attribute="Trainer",
            actual=type(trainer_type).__name__,
        )
    trainer = trainer_type(**dict(trainer_kwargs))
    method = getattr(trainer, method_name)
    kwargs: dict[str, object] = {}
    if method_name == "fit":
        kwargs = {
            "train_dataloaders": train_dataloaders,
            "val_dataloaders": val_dataloaders,
            "datamodule": datamodule,
            "ckpt_path": ckpt_path,
        }
    elif method_name in {"validate", "test"}:
        kwargs = {
            "dataloaders": dataloaders,
            "datamodule": datamodule,
            "ckpt_path": ckpt_path,
        }
    elif method_name == "predict":
        kwargs = {
            "dataloaders": dataloaders,
            "datamodule": datamodule,
            "return_predictions": return_predictions,
            "ckpt_path": ckpt_path,
        }
    output = method(model, **{key: value for key, value in kwargs.items() if value is not None})
    return _completed_result(
        mode,
        output,
        trainer=trainer,
        mapping=policy_mapping,
        preflight=preflight,
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


def _completed_result(
    mode: LoopMode,
    output: object,
    *,
    trainer: object,
    mapping: LightningPolicyMapping,
    preflight: LightningDependencyPreflight,
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
        training_profile=_profile_from_mapping(mapping, preflight=preflight),
        provenance={"engine": "LightningTrainingEngine", "lightning_module": preflight.module_name},
    )


def _failed_result(
    mode: LoopMode,
    exc: Exception,
    mapping: LightningPolicyMapping,
    *,
    preflight: LightningDependencyPreflight,
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
    return TrainingProfile(decisions=tuple(decisions), unavailable_spans=unavailable)


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


def _coerce_bool(value: bool) -> bool:
    if not isinstance(value, bool):
        raise RemotePhysTrainingError(
            "LightningTrainingEngine allow_unsafe_versions must be boolean.",
            owner="LightningTrainingEngine",
            field="allow_unsafe_versions",
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_counter(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
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
