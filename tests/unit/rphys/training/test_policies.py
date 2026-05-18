from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import CompilePolicy, KernelPolicy, PrecisionPolicy, PolicyStatus
from rphys.training.lightning import map_lightning_policies


def test_precision_policy_records_requested_applied_fallback_state() -> None:
    policy = PrecisionPolicy(
        "fp32",
        applied_precision="fp16",
        fallback_precision="bf16",
        status=PolicyStatus.FALLBACK,
        supported_backends=("torch", "triton"),
        numerical_equivalence="fp16-equivalent",
        metadata={"requested_by": "unit"},
        provenance={"scope": "train"},
    )

    assert policy.requested_precision == "fp32"
    assert policy.status is PolicyStatus.FALLBACK
    assert policy.applied_precision == "fp16"
    assert policy.fallback_precision == "bf16"
    assert policy.supported_backends == ("torch", "triton")
    assert asdict(policy)["provenance"] == {"scope": "train"}

    with pytest.raises(RemotePhysTrainingError) as reason_error:
        PrecisionPolicy("fp32", status=PolicyStatus.UNSUPPORTED)
    assert reason_error.value.context["field"] == "unsupported_reason"

    with pytest.raises(RemotePhysTrainingError) as fallback_error:
        PrecisionPolicy("fp32", status=PolicyStatus.FALLBACK, applied_precision="fp16")
    assert fallback_error.value.context["field"] == "fallback_precision"


def test_compile_policy_requires_applied_mode_and_supported_backends() -> None:
    compile_policy = CompilePolicy(
        "enabled",
        applied_mode="enabled",
        status=PolicyStatus.APPLIED,
        backend="torch",
        supported_backends=("torch",),
        backend_equivalence_note="reference",
    )

    assert compile_policy.requested_mode == "enabled"
    assert compile_policy.applied_mode == "enabled"
    assert compile_policy.backend == "torch"
    assert compile_policy.supported_backends == ("torch",)

    unsupported = CompilePolicy(
        status=PolicyStatus.UNSUPPORTED,
        unsupported_reason="backend lacks compiler",
    )
    assert unsupported.status is PolicyStatus.UNSUPPORTED


def test_kernel_policy_disabled_and_fallback_validation() -> None:
    disabled = KernelPolicy(status=PolicyStatus.DISABLED)
    assert disabled.status is PolicyStatus.DISABLED
    assert disabled.requested_kernel is None

    active = KernelPolicy(
        "inductor",
        applied_kernel="inductor",
        status=PolicyStatus.APPLIED,
        backend="torch",
        supported_backends=("torch", "jax"),
        backend_scope="training",
    )
    assert active.supported_backends == ("torch", "jax")

    with pytest.raises(RemotePhysTrainingError) as status_error:
        KernelPolicy("in1d", status=PolicyStatus.DISABLED, applied_kernel="in1d")
    assert status_error.value.context["field"] == "status"


def test_lightning_policy_mapping_applies_precision_and_records_unsupported_boundaries() -> None:
    mapping = map_lightning_policies(
        trainer_kwargs={"max_epochs": 2},
        precision_policy=PrecisionPolicy("bf16"),
        compile_policy=CompilePolicy("enabled"),
        kernel_policy=KernelPolicy("flash-attention"),
    )

    assert mapping.trainer_kwargs["precision"] == "bf16-mixed"
    assert mapping.precision_policy is not None
    assert mapping.precision_policy.status is PolicyStatus.APPLIED
    assert mapping.compile_policy is not None
    assert mapping.compile_policy.status is PolicyStatus.UNSUPPORTED
    assert mapping.kernel_policy is not None
    assert mapping.kernel_policy.status is PolicyStatus.UNSUPPORTED
    assert "compile.unsupported:trainer_kwarg_absent" in mapping.diagnostics

    unsupported_precision = map_lightning_policies(
        precision_policy=PrecisionPolicy("tf32"),
    )
    assert unsupported_precision.precision_policy is not None
    assert unsupported_precision.precision_policy.status is PolicyStatus.UNSUPPORTED

    with pytest.raises(RemotePhysTrainingError) as conflict_error:
        map_lightning_policies(
            trainer_kwargs={"precision": "16-mixed"},
            precision_policy=PrecisionPolicy("32"),
        )
    assert conflict_error.value.context["field"] == "precision"
