"""Provisional batch operation primitives for Stage 7.

Batch operations are dependency-light optimization contracts over loaded
``Batch`` containers. They record descriptive equivalence and dtype/device
metadata but do not allocate backend arrays, move devices, or define loader,
model, cache, export, or workflow policy.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from rphys.data import Batch
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidOperationContractError,
    InvalidOperationContextError,
    InvalidOperationInputError,
    InvalidOperationResultError,
    MissingFieldError,
    OperationExecutionError,
    UndeclaredSampleFieldMutationError,
)

from ._validation import coerce_non_empty_string, coerce_string_mapping, coerce_string_sequence
from .contracts import OperationContract, OperationMutationPolicy, OperationRole
from .context import OperationContext, OperationResult
from .core import OperationStep, _coerce_and_validate_result, _validate_input, _validate_required_context
from .kernels import FunctionalKernel
from .sample import SampleFieldPermissions

__all__ = [
    "BatchParameterScope",
    "BatchEquivalenceClaim",
    "BatchFieldEffects",
    "BatchOperationContext",
    "BatchOperationContract",
    "BatchAugmentationParams",
    "BatchEquivalenceReport",
    "BatchOperation",
    "BatchTransform",
    "BatchAugmentation",
]


_COPY_MODES = ("in_place", "shallow", "deep")


class BatchParameterScope(StrEnum):
    """Parameter scope for provisional batch augmentations."""

    BATCH = "batch"
    PER_SAMPLE = "per_sample"


class BatchEquivalenceClaim(StrEnum):
    """Allowed sample/batch replacement claim categories."""

    IDENTICAL = "identical"
    APPROXIMATE = "approximate"
    DIAGNOSTIC = "diagnostic"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class BatchFieldEffects:
    """String-rendered field-effect evidence for a batch operation."""

    copy_mode: str
    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    replaced: tuple[str, ...] = ()

    def to_mapping(self) -> Mapping[str, object]:
        """Return immutable field-effect metadata."""

        return MappingProxyType(
            {
                "copy_mode": self.copy_mode,
                "added": self.added,
                "removed": self.removed,
                "replaced": self.replaced,
            }
        )


@dataclass(frozen=True, init=False, slots=True)
class BatchOperationContext:
    """Dependency-light runtime context for provisional batch execution."""

    metadata: Mapping[str, object]
    provenance: Mapping[str, object]
    run_seed: object | None
    epoch: int | None
    worker_id: object | None
    batch_id: object | None
    operation_index: int | None
    operation_name: str | None
    batch_size: int | None
    dtype: str | None
    device: str | None
    parameter_scope: BatchParameterScope | None

    def __init__(
        self,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
        run_seed: object | None = None,
        epoch: int | None = None,
        worker_id: object | None = None,
        batch_id: object | None = None,
        operation_index: int | None = None,
        operation_name: str | None = None,
        batch_size: int | None = None,
        dtype: str | None = None,
        device: str | None = None,
        parameter_scope: BatchParameterScope | str | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="BatchOperationContext",
                field="metadata",
                error_type=InvalidOperationContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="BatchOperationContext",
                field="provenance",
                error_type=InvalidOperationContextError,
            ),
        )
        object.__setattr__(self, "run_seed", run_seed)
        object.__setattr__(self, "epoch", _coerce_optional_int(epoch, field_name="epoch"))
        object.__setattr__(self, "worker_id", worker_id)
        object.__setattr__(self, "batch_id", batch_id)
        object.__setattr__(self, "operation_index", _coerce_optional_int(operation_index, field_name="operation_index"))
        object.__setattr__(
            self,
            "operation_name",
            coerce_non_empty_string(
                operation_name,
                owner="BatchOperationContext",
                field="operation_name",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if operation_name is not None else None,
        )
        object.__setattr__(self, "batch_size", _coerce_optional_int(batch_size, field_name="batch_size"))
        object.__setattr__(
            self,
            "dtype",
            coerce_non_empty_string(
                dtype,
                owner="BatchOperationContext",
                field="dtype",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if dtype is not None else None,
        )
        object.__setattr__(
            self,
            "device",
            coerce_non_empty_string(
                device,
                owner="BatchOperationContext",
                field="device",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if device is not None else None,
        )
        object.__setattr__(
            self,
            "parameter_scope",
            _coerce_parameter_scope(
                parameter_scope,
                owner="BatchOperationContext",
                field="parameter_scope",
                error_type=InvalidOperationContextError,
            ),
        )

    def to_operation_context(self) -> OperationContext:
        """Convert to generic operation metadata/provenance context."""

        return OperationContext(metadata=self.metadata, provenance=self.provenance)

    def to_mapping(self) -> Mapping[str, object | None]:
        """Return immutable runtime evidence for diagnostics and replay."""

        return MappingProxyType(
            {
                "run_seed": self.run_seed,
                "epoch": self.epoch,
                "worker_id": self.worker_id,
                "batch_id": self.batch_id,
                "operation_index": self.operation_index,
                "operation_name": self.operation_name,
                "batch_size": self.batch_size,
                "dtype": self.dtype,
                "device": self.device,
                "parameter_scope": self.parameter_scope.value if self.parameter_scope is not None else None,
            }
        )


@dataclass(frozen=True, init=False, slots=True)
class BatchOperationContract:
    """Provisional batch operation contract with descriptive batch metadata."""

    field_permissions: SampleFieldPermissions
    required_context: tuple[str, ...]
    failure_modes: tuple[str, ...]
    mutation_policy: OperationMutationPolicy
    side_effects: tuple[str, ...]
    copy_mode: str
    parameter_scope: BatchParameterScope | None
    dtype: str | None
    device: str | None
    equivalence: "BatchEquivalenceReport"
    _copy_mode_explicit: bool = field(init=False, repr=False)
    _operation_contract: OperationContract = field(init=False, repr=False)

    def __init__(
        self,
        *,
        field_permissions: SampleFieldPermissions | None = None,
        required_context: Sequence[str] | None = None,
        failure_modes: Sequence[str] | None = None,
        mutation_policy: OperationMutationPolicy | str = OperationMutationPolicy.PURE,
        side_effects: Sequence[str] | None = None,
        copy_mode: str | None = None,
        parameter_scope: BatchParameterScope | str | None = None,
        dtype: str | None = None,
        device: str | None = None,
        equivalence: "BatchEquivalenceReport | None" = None,
    ) -> None:
        if field_permissions is not None and not isinstance(field_permissions, SampleFieldPermissions):
            raise InvalidOperationContractError(
                "BatchOperationContract field_permissions must be a SampleFieldPermissions record.",
                owner="BatchOperationContract",
                field="field_permissions",
                expected="SampleFieldPermissions | None",
                actual=type(field_permissions).__name__,
            )
        if equivalence is not None and not isinstance(equivalence, BatchEquivalenceReport):
            raise InvalidOperationContractError(
                "BatchOperationContract equivalence must be a BatchEquivalenceReport.",
                owner="BatchOperationContract",
                field="equivalence",
                expected="BatchEquivalenceReport | None",
                actual=type(equivalence).__name__,
            )

        operation_contract = OperationContract(
            role=OperationRole.GENERIC,
            input_type=Batch,
            output_type=Batch,
            mutation_policy=mutation_policy,
            side_effects=side_effects,
            required_context=required_context,
            failure_modes=failure_modes,
        )

        object.__setattr__(self, "field_permissions", SampleFieldPermissions() if field_permissions is None else field_permissions)
        object.__setattr__(self, "required_context", operation_contract.required_context)
        object.__setattr__(self, "failure_modes", operation_contract.failure_modes)
        object.__setattr__(self, "mutation_policy", operation_contract.mutation_policy)
        object.__setattr__(self, "side_effects", operation_contract.side_effects)
        if copy_mode is None:
            object.__setattr__(self, "copy_mode", "in_place")
            object.__setattr__(self, "_copy_mode_explicit", False)
        else:
            object.__setattr__(self, "copy_mode", _coerce_copy_mode(copy_mode))
            object.__setattr__(self, "_copy_mode_explicit", True)
        object.__setattr__(
            self,
            "parameter_scope",
            _coerce_parameter_scope(
                parameter_scope,
                owner="BatchOperationContract",
                field="parameter_scope",
                error_type=InvalidOperationContractError,
            ),
        )
        object.__setattr__(self, "dtype", _coerce_optional_text(dtype, owner="BatchOperationContract", field="dtype", error_type=InvalidOperationContractError))
        object.__setattr__(self, "device", _coerce_optional_text(device, owner="BatchOperationContract", field="device", error_type=InvalidOperationContractError))
        object.__setattr__(self, "equivalence", BatchEquivalenceReport() if equivalence is None else equivalence)
        object.__setattr__(self, "_operation_contract", operation_contract)

    @property
    def contract(self) -> OperationContract:
        """Adapted generic contract for pipeline compatibility."""

        return self._operation_contract

    @property
    def operation_contract(self) -> OperationContract:
        """Compatibility alias for the adapted generic contract."""

        return self._operation_contract


@dataclass(frozen=True, init=False, slots=True)
class BatchAugmentationParams:
    """Immutable lightweight parameters for provisional batch augmentation."""

    scope: BatchParameterScope
    values: Mapping[str, object]
    per_sample: tuple[Mapping[str, object], ...]

    def __init__(
        self,
        *,
        scope: BatchParameterScope | str = BatchParameterScope.BATCH,
        values: Mapping[str, object] | None = None,
        per_sample: Sequence[Mapping[str, object]] | None = None,
    ) -> None:
        scope_value = _coerce_parameter_scope(
            scope,
            owner="BatchAugmentationParams",
            field="scope",
            error_type=InvalidOperationInputError,
        )
        if scope_value is None:
            raise InvalidOperationInputError(
                "BatchAugmentationParams scope must be explicit.",
                owner="BatchAugmentationParams",
                field="scope",
                expected="batch | per_sample",
                actual=None,
            )
        per_sample_values = _coerce_per_sample_params(per_sample)
        if scope_value is BatchParameterScope.PER_SAMPLE and len(per_sample_values) == 0:
            raise InvalidOperationInputError(
                "per-sample batch augmentation params require per_sample entries.",
                owner="BatchAugmentationParams",
                field="per_sample",
                expected="non-empty sequence of mappings",
                actual="empty",
            )
        object.__setattr__(self, "scope", scope_value)
        object.__setattr__(self, "values", _coerce_augmentation_values(values, owner="BatchAugmentationParams", field="values"))
        object.__setattr__(self, "per_sample", per_sample_values)

    def to_mapping(self) -> Mapping[str, object]:
        """Return immutable parameter evidence."""

        return MappingProxyType(
            {
                "scope": self.scope.value,
                "values": self.values,
                "per_sample": self.per_sample,
            }
        )


@dataclass(frozen=True, init=False, slots=True)
class BatchEquivalenceReport:
    """Descriptive claim about replacing sample-side behavior with batch execution."""

    claim: BatchEquivalenceClaim
    reference_operation: str | None
    tolerances: Mapping[str, object]
    diagnostics: tuple[str, ...]
    sample_count: int | None

    def __init__(
        self,
        *,
        claim: BatchEquivalenceClaim | str = BatchEquivalenceClaim.DIAGNOSTIC,
        reference_operation: str | None = None,
        tolerances: Mapping[str, object] | None = None,
        diagnostics: Sequence[str] | None = None,
        sample_count: int | None = None,
    ) -> None:
        claim_value = _coerce_equivalence_claim(claim)
        diagnostics_tuple = coerce_string_sequence(
            diagnostics,
            owner="BatchEquivalenceReport",
            field="diagnostics",
            expected="ordered non-empty diagnostic strings",
            error_type=InvalidOperationResultError,
            allow_none=True,
        )
        if claim_value in {BatchEquivalenceClaim.APPROXIMATE, BatchEquivalenceClaim.UNSUPPORTED} and not diagnostics_tuple:
            raise InvalidOperationResultError(
                "approximate and unsupported batch equivalence claims require diagnostics.",
                owner="BatchEquivalenceReport",
                field="diagnostics",
                expected="non-empty diagnostics",
                actual=diagnostics_tuple,
            )
        object.__setattr__(self, "claim", claim_value)
        object.__setattr__(self, "reference_operation", _coerce_optional_text(reference_operation, owner="BatchEquivalenceReport", field="reference_operation", error_type=InvalidOperationResultError))
        object.__setattr__(
            self,
            "tolerances",
            _coerce_augmentation_values(
                tolerances,
                owner="BatchEquivalenceReport",
                field="tolerances",
                error_type=InvalidOperationResultError,
            ),
        )
        object.__setattr__(self, "diagnostics", diagnostics_tuple)
        object.__setattr__(self, "sample_count", _coerce_optional_int(sample_count, field_name="sample_count"))

    def to_mapping(self) -> Mapping[str, object | None]:
        """Return immutable equivalence evidence."""

        return MappingProxyType(
            {
                "claim": self.claim.value,
                "reference_operation": self.reference_operation,
                "tolerances": self.tolerances,
                "diagnostics": self.diagnostics,
                "sample_count": self.sample_count,
            }
        )


class BatchOperation(OperationStep):
    """Callable-first provisional batch adapter implementing ``OperationStep``."""

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: BatchOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        if not callable(function):
            raise InvalidOperationContractError(
                "batch operation function must be callable.",
                owner="BatchOperation",
                field="function",
                expected="callable",
                actual=type(function).__name__,
            )
        resolved_contract = BatchOperationContract() if contract is None else contract
        if not isinstance(resolved_contract, BatchOperationContract):
            raise InvalidOperationContractError(
                "operation contract must be a BatchOperationContract.",
                owner="BatchOperation",
                field="contract",
                expected="BatchOperationContract",
                actual=type(contract).__name__,
            )
        resolved_copy_mode = resolved_contract.copy_mode
        if copy_mode is not None:
            requested_copy_mode = _coerce_copy_mode(copy_mode, owner="BatchOperation")
            if resolved_contract._copy_mode_explicit and resolved_copy_mode != requested_copy_mode:
                raise InvalidOperationContractError(
                    "batch operation copy_mode conflicts with contract copy_mode.",
                    owner="BatchOperation",
                    field="copy_mode",
                    expected=resolved_copy_mode,
                    actual=requested_copy_mode,
                )
            resolved_copy_mode = requested_copy_mode

        self._function = function
        self._name = _infer_name(name, function)
        self._batch_contract = resolved_contract
        self._copy_mode = resolved_copy_mode
        self._contract = resolved_contract.contract

    @property
    def name(self) -> str:
        return self._name

    @property
    def batch_contract(self) -> BatchOperationContract:
        return self._batch_contract

    @property
    def copy_mode(self) -> str:
        return self._copy_mode

    @property
    def contract(self) -> OperationContract:
        return self._contract

    def run(self, input_value: object, context: OperationContext | BatchOperationContext | None = None) -> OperationResult:
        execution_context = _coerce_batch_operation_context(context, operation_name=self._name)
        _validate_required_context(
            self._batch_contract.required_context,
            execution_context.metadata,
            operation_name=self._name,
            role=self._contract.role,
        )
        _validate_input(self._contract.input_type, input_value, operation_name=self._name)
        _validate_required_reads(input_value, self._batch_contract.field_permissions.reads, operation_name=self._name)

        execution_batch = _prepare_execution_batch(input_value, self._copy_mode)
        before_snapshot = _snapshot_field_items(execution_batch)
        try:
            result = self._function(execution_batch, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "batch operation callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="run",
            ) from exc

        return _finalize_batch_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context,
            execution_batch=execution_batch,
            before_snapshot=before_snapshot,
            copy_mode=self._copy_mode,
            field_permissions=self._batch_contract.field_permissions,
            equivalence=self._batch_contract.equivalence,
        )

    def __call__(self, input_value: object, context: OperationContext | BatchOperationContext | None = None) -> OperationResult:
        return self.run(input_value, context=context)


class BatchTransform(BatchOperation):
    """Batch transform wrapper that must declare output fields."""

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: BatchOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        resolved_contract = BatchOperationContract() if contract is None else contract
        if not isinstance(resolved_contract, BatchOperationContract):
            raise InvalidOperationContractError(
                "operation contract must be a BatchOperationContract.",
                owner="BatchTransform",
                field="contract",
                expected="BatchOperationContract",
                actual=type(contract).__name__,
            )
        if len(resolved_contract.field_permissions.writes) == 0 and len(resolved_contract.field_permissions.dynamic_writes) == 0:
            raise InvalidOperationContractError(
                "batch transform operations must declare output fields via writes or dynamic_writes.",
                owner="BatchTransform",
                field="contract.field_permissions",
                expected="writes or dynamic_writes",
                actual="none",
            )
        super().__init__(function, name=name, contract=resolved_contract, copy_mode=copy_mode)


class BatchAugmentation(BatchOperation):
    """Batch operation with explicit parameter sampling and deterministic application."""

    def __init__(
        self,
        sample_params: Callable[[Batch, BatchOperationContext], BatchAugmentationParams],
        apply_params: Callable[[Batch, BatchAugmentationParams, BatchOperationContext], Batch | OperationResult],
        *,
        name: str | None = None,
        contract: BatchOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        if not callable(sample_params):
            raise InvalidOperationContractError(
                "batch augmentation sampler must be callable.",
                owner="BatchAugmentation",
                field="sample_params",
                expected="callable",
                actual=type(sample_params).__name__,
            )
        if not callable(apply_params):
            raise InvalidOperationContractError(
                "batch augmentation apply function must be callable.",
                owner="BatchAugmentation",
                field="apply_params",
                expected="callable",
                actual=type(apply_params).__name__,
            )
        super().__init__(_identity_batch, name=name, contract=contract, copy_mode=copy_mode)
        self._sample_params_kernel = sample_params
        self._apply_params_kernel = apply_params

    @property
    def sample_params_kernel(self) -> Callable[[Batch, BatchOperationContext], BatchAugmentationParams]:
        return self._sample_params_kernel

    @property
    def apply_params_kernel(self) -> Callable[[Batch, BatchAugmentationParams, BatchOperationContext], Batch | OperationResult]:
        return self._apply_params_kernel

    def sample_params(self, batch: Batch, context: OperationContext | BatchOperationContext) -> BatchAugmentationParams:
        execution_context = _coerce_batch_operation_context(context, operation_name=self._name)
        _validate_input(self._contract.input_type, batch, operation_name=self._name)
        before_snapshot = _snapshot_field_items(batch)
        try:
            params = self._sample_params_kernel(batch, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "batch augmentation sampling callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="sample_params",
            ) from exc
        _validate_no_batch_field_effects(
            self._name,
            "sample_params",
            _compute_field_effects(before_snapshot, _snapshot_field_items(batch)),
        )
        if not isinstance(params, BatchAugmentationParams):
            raise InvalidOperationResultError(
                "batch augmentation sampler must return BatchAugmentationParams.",
                operation_name=self._name,
                field="sample_params",
                expected="BatchAugmentationParams",
                actual=type(params).__name__,
            )
        return params

    def apply_params(
        self,
        batch: Batch,
        params: BatchAugmentationParams,
        context: OperationContext | BatchOperationContext,
    ) -> Batch | OperationResult:
        execution_context = _coerce_batch_operation_context(context, operation_name=self._name)
        _validate_input(self._contract.input_type, batch, operation_name=self._name)
        if not isinstance(params, BatchAugmentationParams):
            raise InvalidOperationInputError(
                "batch augmentation apply params must be BatchAugmentationParams.",
                owner="BatchAugmentation",
                field="params",
                expected="BatchAugmentationParams",
                actual=type(params).__name__,
            )
        try:
            result = self._apply_params_kernel(batch, params, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "batch augmentation apply callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="apply_params",
            ) from exc
        if not isinstance(result, (Batch, OperationResult)):
            raise InvalidOperationResultError(
                "batch augmentation apply callable must return a Batch or OperationResult.",
                operation_name=self._name,
                field="apply_params",
                expected="Batch | OperationResult",
                actual=type(result).__name__,
            )
        return result

    def run(self, input_value: object, context: OperationContext | BatchOperationContext | None = None) -> OperationResult:
        execution_context = _coerce_batch_operation_context(context, operation_name=self._name)
        _validate_required_context(
            self._batch_contract.required_context,
            execution_context.metadata,
            operation_name=self._name,
            role=self._contract.role,
        )
        _validate_input(self._contract.input_type, input_value, operation_name=self._name)
        _validate_required_reads(input_value, self._batch_contract.field_permissions.reads, operation_name=self._name)

        execution_batch = _prepare_execution_batch(input_value, self._copy_mode)
        params = self.sample_params(execution_batch, execution_context)
        before_apply_snapshot = _snapshot_field_items(execution_batch)
        result = self.apply_params(execution_batch, params, execution_context)
        normalized = _finalize_batch_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context,
            execution_batch=execution_batch,
            before_snapshot=before_apply_snapshot,
            copy_mode=self._copy_mode,
            field_permissions=self._batch_contract.field_permissions,
            equivalence=self._batch_contract.equivalence,
        )
        return _attach_batch_augmentation_replay(normalized, params=params, context=execution_context)


def _infer_name(explicit_name: str | None, function: FunctionalKernel) -> str:
    if explicit_name is not None:
        return coerce_non_empty_string(
            explicit_name,
            owner="BatchOperation",
            field="name",
            expected="non-empty string",
            error_type=InvalidOperationContractError,
        )
    inferred = getattr(function, "__name__", None)
    if isinstance(inferred, str) and inferred.strip():
        return inferred
    return function.__class__.__name__


def _identity_batch(payload: Batch, *, context: BatchOperationContext) -> Batch:
    return payload


def _coerce_copy_mode(value: str, *, owner: str = "BatchOperationContract", field: str = "copy_mode") -> str:
    normalized = coerce_non_empty_string(
        value,
        owner=owner,
        field=field,
        expected="in_place, shallow, or deep",
        error_type=InvalidOperationContractError,
    )
    if normalized not in _COPY_MODES:
        raise InvalidOperationContractError(
            f"{owner} {field} must be one of {_COPY_MODES}.",
            owner=owner,
            field=field,
            expected=_COPY_MODES,
            actual=normalized,
        )
    return normalized


def _coerce_parameter_scope(
    value: BatchParameterScope | str | None,
    *,
    owner: str,
    field: str,
    error_type: type[InvalidOperationContextError] | type[InvalidOperationContractError] | type[InvalidOperationInputError],
) -> BatchParameterScope | None:
    if value is None:
        return None
    if isinstance(value, BatchParameterScope):
        return value
    try:
        return BatchParameterScope(value)
    except (TypeError, ValueError):
        raise error_type(
            f"{owner} {field} must be a BatchParameterScope.",
            owner=owner,
            field=field,
            expected="batch | per_sample",
            actual=repr(value),
        )


def _coerce_equivalence_claim(value: BatchEquivalenceClaim | str) -> BatchEquivalenceClaim:
    if isinstance(value, BatchEquivalenceClaim):
        return value
    try:
        return BatchEquivalenceClaim(value)
    except (TypeError, ValueError):
        raise InvalidOperationResultError(
            "BatchEquivalenceReport claim must be a BatchEquivalenceClaim.",
            owner="BatchEquivalenceReport",
            field="claim",
            expected="identical | approximate | diagnostic | unsupported",
            actual=repr(value),
        )


def _coerce_optional_text(value: object | None, *, owner: str, field: str, error_type):
    if value is None:
        return None
    return coerce_non_empty_string(value, owner=owner, field=field, expected="non-empty string or None", error_type=error_type)


def _coerce_optional_int(value: object | None, *, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise InvalidOperationContextError(
            f"{field_name} must be an integer or None.",
            field=field_name,
            expected="int | None",
            actual=type(value).__name__,
        )
    return value


def _coerce_augmentation_values(
    values: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
    error_type=InvalidOperationInputError,
) -> Mapping[str, object]:
    if values is None:
        return MappingProxyType({})
    if not isinstance(values, Mapping):
        raise error_type(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, object]",
            actual=type(values).__name__,
        )
    normalized: dict[str, object] = {}
    for key, value in values.items():
        normalized_key = coerce_non_empty_string(
            key,
            owner=owner,
            field=f"{field}.key",
            expected="non-empty string keys",
            error_type=error_type,
        )
        normalized[normalized_key] = _coerce_augmentation_value(
            value,
            owner=owner,
            field=f"{field}[{normalized_key}]",
            error_type=error_type,
        )
    return MappingProxyType(normalized)


def _coerce_augmentation_value(
    value: object,
    *,
    owner: str,
    field: str,
    error_type=InvalidOperationInputError,
) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return _coerce_augmentation_values(
            value,
            owner=owner,
            field=field,
            error_type=error_type,
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(
            _coerce_augmentation_value(
                item,
                owner=owner,
                field=f"{field}[{index}]",
                error_type=error_type,
            )
            for index, item in enumerate(value)
        )
    raise error_type(
        f"{owner} {field} contains unsupported lightweight value.",
        owner=owner,
        field=field,
        expected="None, bool, int, float, str, tuple, or string-keyed mapping",
        actual=type(value).__name__,
    )


def _coerce_per_sample_params(per_sample: Sequence[Mapping[str, object]] | None) -> tuple[Mapping[str, object], ...]:
    if per_sample is None:
        return ()
    if isinstance(per_sample, (str, bytes, bytearray)) or not isinstance(per_sample, Sequence):
        raise InvalidOperationInputError(
            "BatchAugmentationParams per_sample must be a sequence of mappings.",
            owner="BatchAugmentationParams",
            field="per_sample",
            expected="sequence of mapping[str, object]",
            actual=type(per_sample).__name__,
        )
    return tuple(
        _coerce_augmentation_values(mapping, owner="BatchAugmentationParams", field=f"per_sample[{index}]")
        for index, mapping in enumerate(per_sample)
    )


def _coerce_batch_operation_context(
    context: OperationContext | BatchOperationContext | None,
    *,
    operation_name: str,
) -> BatchOperationContext:
    if context is None:
        return BatchOperationContext(operation_name=operation_name)
    if isinstance(context, BatchOperationContext):
        if context.operation_name is None:
            return BatchOperationContext(
                metadata=context.metadata,
                provenance=context.provenance,
                run_seed=context.run_seed,
                epoch=context.epoch,
                worker_id=context.worker_id,
                batch_id=context.batch_id,
                operation_index=context.operation_index,
                operation_name=operation_name,
                batch_size=context.batch_size,
                dtype=context.dtype,
                device=context.device,
                parameter_scope=context.parameter_scope,
            )
        if context.operation_name != operation_name:
            raise InvalidOperationContextError(
                "batch operation context operation_name must match the executing operation.",
                field="context.operation_name",
                expected=operation_name,
                actual=context.operation_name,
            )
        return context
    if isinstance(context, OperationContext):
        return BatchOperationContext(metadata=context.metadata, provenance=context.provenance, operation_name=operation_name)
    raise InvalidOperationContextError(
        "batch operation context must be None, OperationContext, or BatchOperationContext.",
        field="context",
        expected="OperationContext | BatchOperationContext | None",
        actual=type(context).__name__,
    )


def _prepare_execution_batch(batch: Batch, copy_mode: str) -> Batch:
    if copy_mode == "in_place":
        return batch
    if copy_mode == "shallow":
        return batch.shallow_copy()
    return batch.deep_copy()


def _snapshot_field_items(batch: Batch) -> tuple[tuple[FieldLocator, FieldValue], ...]:
    return tuple(batch.field_items())


def _compute_field_effects(
    before_snapshot: tuple[tuple[FieldLocator, FieldValue], ...],
    after_snapshot: tuple[tuple[FieldLocator, FieldValue], ...],
) -> dict[str, tuple[FieldLocator, ...]]:
    before_map = {locator: value for locator, value in before_snapshot}
    after_map = {locator: value for locator, value in after_snapshot}
    return {
        "added": tuple(locator for locator in after_map if locator not in before_map),
        "removed": tuple(locator for locator in before_map if locator not in after_map),
        "replaced": tuple(locator for locator, value in after_map.items() if locator in before_map and before_map[locator] is not value),
    }


def _validate_required_reads(batch: object, reads: tuple[FieldLocator, ...], *, operation_name: str) -> None:
    if not isinstance(batch, Batch):
        return
    for locator in reads:
        if not batch.has(locator):
            raise MissingFieldError("operation required batch field is missing.", operation_name=operation_name, locator=str(locator))


def _validate_field_permissions(operation_name: str, permissions: SampleFieldPermissions, effects: dict[str, tuple[FieldLocator, ...]]) -> None:
    writes = set(permissions.writes)
    deletes = set(permissions.deletes)
    dynamic_writes = set(permissions.dynamic_writes)
    allowed_add = writes | dynamic_writes
    allowed_replace = writes | dynamic_writes
    for effect_name, allowed in (("added", allowed_add), ("removed", deletes), ("replaced", allowed_replace)):
        for locator in effects[effect_name]:
            if locator in allowed:
                continue
            raise UndeclaredSampleFieldMutationError(
                f"batch operation attempted undeclared field {effect_name}.",
                operation_name=operation_name,
                effect_type=effect_name,
                locator=str(locator),
                declared_writes=tuple(str(item) for item in permissions.writes),
                declared_deletes=tuple(str(item) for item in permissions.deletes),
                declared_dynamic_writes=tuple(str(item) for item in permissions.dynamic_writes),
                detected_added=tuple(str(item) for item in effects["added"]),
                detected_removed=tuple(str(item) for item in effects["removed"]),
                detected_replaced=tuple(str(item) for item in effects["replaced"]),
            )


def _attach_batch_field_effects(result: OperationResult, copy_mode: str, effects: dict[str, tuple[FieldLocator, ...]]) -> OperationResult:
    if "batch_field_effects" in result.metadata:
        raise InvalidOperationResultError(
            "batch operation result metadata collides with runtime field-effect key.",
            operation_name=result.operation_name,
            field="metadata.batch_field_effects",
            expected="absent",
            actual="present",
        )
    metadata = dict(result.metadata)
    metadata["batch_field_effects"] = BatchFieldEffects(
        copy_mode=copy_mode,
        added=tuple(str(locator) for locator in effects["added"]),
        removed=tuple(str(locator) for locator in effects["removed"]),
        replaced=tuple(str(locator) for locator in effects["replaced"]),
    ).to_mapping()
    return OperationResult(
        output=result.output,
        operation_name=result.operation_name,
        role=result.role,
        metadata=metadata,
        provenance=result.provenance,
        side_effect_evidence=result.side_effect_evidence,
    )


def _attach_batch_equivalence(result: OperationResult, equivalence: BatchEquivalenceReport) -> OperationResult:
    if "batch_equivalence" in result.metadata:
        raise InvalidOperationResultError(
            "batch operation result metadata collides with runtime equivalence key.",
            operation_name=result.operation_name,
            field="metadata.batch_equivalence",
            expected="absent",
            actual="present",
        )
    metadata = dict(result.metadata)
    metadata["batch_equivalence"] = equivalence.to_mapping()
    return OperationResult(
        output=result.output,
        operation_name=result.operation_name,
        role=result.role,
        metadata=metadata,
        provenance=result.provenance,
        side_effect_evidence=result.side_effect_evidence,
    )


def _attach_batch_augmentation_replay(
    result: OperationResult,
    *,
    params: BatchAugmentationParams,
    context: BatchOperationContext,
) -> OperationResult:
    if "batch_augmentation_replay" in result.metadata:
        raise InvalidOperationResultError(
            "batch augmentation result metadata collides with reserved key.",
            operation_name=result.operation_name,
            field="metadata.batch_augmentation_replay",
            expected="absent",
            actual="present",
        )
    metadata = dict(result.metadata)
    metadata["batch_augmentation_replay"] = {
        "context": context.to_mapping(),
        "params": params.to_mapping(),
    }
    return OperationResult(
        output=result.output,
        operation_name=result.operation_name,
        role=result.role,
        metadata=metadata,
        provenance=result.provenance,
        side_effect_evidence=result.side_effect_evidence,
    )


def _validate_no_batch_field_effects(operation_name: str, phase: str, effects: dict[str, tuple[FieldLocator, ...]]) -> None:
    if not effects["added"] and not effects["removed"] and not effects["replaced"]:
        return
    raise InvalidOperationResultError(
        "batch augmentation sampling phase must not mutate batch fields.",
        operation_name=operation_name,
        field=phase,
        expected="no batch field mutations",
        actual={
            effect_name: tuple(str(locator) for locator in locators)
            for effect_name, locators in effects.items()
        },
    )


def _finalize_batch_result(
    result: object,
    *,
    operation_name: str,
    contract: OperationContract,
    context: BatchOperationContext,
    execution_batch: Batch,
    before_snapshot: tuple[tuple[FieldLocator, FieldValue], ...],
    copy_mode: str,
    field_permissions: SampleFieldPermissions,
    equivalence: BatchEquivalenceReport,
) -> OperationResult:
    normalized = _coerce_and_validate_result(
        result,
        operation_name=operation_name,
        contract=contract,
        context=context.to_operation_context(),
    )
    if normalized.output is not execution_batch:
        raise InvalidOperationResultError(
            "batch operation must return the execution batch object.",
            operation_name=operation_name,
            field="output",
            expected="execution batch object",
            actual=type(normalized.output).__name__,
        )
    effects = _compute_field_effects(before_snapshot, _snapshot_field_items(execution_batch))
    _validate_field_permissions(operation_name, field_permissions, effects)
    return _attach_batch_equivalence(
        _attach_batch_field_effects(normalized, copy_mode, effects),
        equivalence,
    )


BatchFieldEffects.__hash__ = None  # type: ignore[assignment]
BatchOperationContext.__hash__ = None  # type: ignore[assignment]
BatchOperationContract.__hash__ = None  # type: ignore[assignment]
BatchAugmentationParams.__hash__ = None  # type: ignore[assignment]
BatchEquivalenceReport.__hash__ = None  # type: ignore[assignment]
BatchOperation.__hash__ = None  # type: ignore[assignment]
BatchTransform.__hash__ = None  # type: ignore[assignment]
BatchAugmentation.__hash__ = None  # type: ignore[assignment]
