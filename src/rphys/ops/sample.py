"""Sample operation foundations for Stage 7.

This module adds deterministic sample operation execution primitives and declared
field-effect enforcement on top of mutable sample containers.

Implemented primitives:

- :class:`SampleOperation`
- :class:`SampleTransform`
- :class:`SampleCheck`
- :class:`SampleDecision`
- :class:`SampleRoute`

Payload materialization is intentionally not intercepted for mutation detection.
Declared read validation and field snapshots only use non-payload APIs.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from rphys.data import Sample
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidFieldLocatorError,
    InvalidOperationContractError,
    InvalidOperationContextError,
    InvalidOperationResultError,
    InvalidOperationInputError,
    MissingFieldError,
    OperationExecutionError,
    UndeclaredSampleFieldMutationError,
)

from ._validation import coerce_non_empty_string, coerce_string_mapping
from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .context import OperationContext, OperationResult
from .core import (
    OperationStep,
    _coerce_and_validate_result,
    _validate_input,
    _validate_required_context,
)
from .kernels import FunctionalKernel

__all__ = [
    "SampleFieldPermissions",
    "SampleOperationContract",
    "SampleOperationContext",
    "SampleReplayRecord",
    "SampleAugmentationParams",
    "SampleAugmentation",
    "SampleOperation",
    "SampleTransform",
    "SampleCheck",
    "SampleDecision",
    "SampleRoute",
]


_COPY_MODES = ("in_place", "shallow", "deep")


@dataclass(frozen=True, init=False, slots=True)
class SampleFieldPermissions:
    """Normalized field declarations for sample operations."""

    reads: tuple[FieldLocator, ...]
    writes: tuple[FieldLocator, ...]
    deletes: tuple[FieldLocator, ...]
    dynamic_writes: tuple[FieldLocator, ...]

    def __init__(
        self,
        *,
        reads: Sequence[FieldLocator | str] | FieldLocator | str | None = None,
        writes: Sequence[FieldLocator | str] | FieldLocator | str | None = None,
        deletes: Sequence[FieldLocator | str] | FieldLocator | str | None = None,
        dynamic_writes: Sequence[FieldLocator | str] | FieldLocator | str | None = None,
    ) -> None:
        reads_tuple = _coerce_locator_sequence(reads, owner="SampleFieldPermissions", field_name="reads")
        writes_tuple = _coerce_locator_sequence(writes, owner="SampleFieldPermissions", field_name="writes")
        deletes_tuple = _coerce_locator_sequence(deletes, owner="SampleFieldPermissions", field_name="deletes")
        dynamic_writes_tuple = _coerce_locator_sequence(
            dynamic_writes,
            owner="SampleFieldPermissions",
            field_name="dynamic_writes",
        )

        _validate_locator_collection_uniqueness(
            reads_tuple,
            owner="SampleFieldPermissions",
            field_name="reads",
        )
        _validate_locator_collection_uniqueness(
            writes_tuple,
            owner="SampleFieldPermissions",
            field_name="writes",
        )
        _validate_locator_collection_uniqueness(
            deletes_tuple,
            owner="SampleFieldPermissions",
            field_name="deletes",
        )
        _validate_locator_collection_uniqueness(
            dynamic_writes_tuple,
            owner="SampleFieldPermissions",
            field_name="dynamic_writes",
        )
        _validate_non_overlapping_permissions(
            writes_tuple,
            deletes_tuple,
            dynamic_writes_tuple,
        )

        object.__setattr__(self, "reads", reads_tuple)
        object.__setattr__(self, "writes", writes_tuple)
        object.__setattr__(self, "deletes", deletes_tuple)
        object.__setattr__(self, "dynamic_writes", dynamic_writes_tuple)


@dataclass(frozen=True, init=False, slots=True)
class SampleOperationContract:
    """Sample-specific operation declaration with adapted generic contract."""

    field_permissions: SampleFieldPermissions
    required_context: tuple[str, ...]
    failure_modes: tuple[str, ...]
    mutation_policy: OperationMutationPolicy
    side_effects: tuple[str, ...]
    copy_mode: str
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
    ) -> None:
        if field_permissions is not None and not isinstance(field_permissions, SampleFieldPermissions):
            raise InvalidOperationContractError(
                "SampleOperationContract field_permissions must be a SampleFieldPermissions record.",
                owner="SampleOperationContract",
                field="field_permissions",
                expected="SampleFieldPermissions | None",
                actual=type(field_permissions).__name__,
            )

        operation_contract = OperationContract(
            role=OperationRole.GENERIC,
            input_type=Sample,
            output_type=Sample,
            mutation_policy=mutation_policy,
            side_effects=side_effects,
            required_context=required_context,
            failure_modes=failure_modes,
        )

        object.__setattr__(
            self,
            "field_permissions",
            SampleFieldPermissions() if field_permissions is None else field_permissions,
        )
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
class SampleOperationContext:
    """Dependency-light sample execution context."""

    metadata: Mapping[str, object]
    provenance: Mapping[str, object]
    run_seed: object | None
    epoch: int | None
    worker_id: object | None
    item_id: object | None
    sample_id: object | None
    operation_index: int | None
    operation_name: str | None
    view_name: str | None
    rng_stream: object | None

    def __init__(
        self,
        *,
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
        run_seed: object | None = None,
        epoch: int | None = None,
        worker_id: object | None = None,
        item_id: object | None = None,
        sample_id: object | None = None,
        operation_index: int | None = None,
        operation_name: str | None = None,
        view_name: str | None = None,
        rng_stream: object | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="SampleOperationContext",
                field="metadata",
                error_type=InvalidOperationContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="SampleOperationContext",
                field="provenance",
                error_type=InvalidOperationContextError,
            ),
        )
        object.__setattr__(self, "run_seed", run_seed)
        object.__setattr__(
            self,
            "epoch",
            _coerce_optional_int(
                epoch,
                field_name="epoch",
            ),
        )
        object.__setattr__(self, "worker_id", worker_id)
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "sample_id", sample_id)
        object.__setattr__(
            self,
            "operation_index",
            _coerce_optional_int(
                operation_index,
                field_name="operation_index",
            ),
        )
        object.__setattr__(
            self,
            "operation_name",
            coerce_non_empty_string(
                operation_name,
                owner="SampleOperationContext",
                field="operation_name",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if operation_name is not None else None,
        )
        object.__setattr__(
            self,
            "view_name",
            coerce_non_empty_string(
                view_name,
                owner="SampleOperationContext",
                field="view_name",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if view_name is not None else None,
        )
        object.__setattr__(self, "rng_stream", rng_stream)

    def to_operation_context(self) -> OperationContext:
        """Convert this context to the generic operation context."""

        return OperationContext(
            metadata=self.metadata,
            provenance=self.provenance,
        )

    def to_replay_record(self) -> "SampleReplayRecord":
        """Convert this context to immutable runtime replay evidence."""

        return SampleReplayRecord(
            run_seed=self.run_seed,
            epoch=self.epoch,
            worker_id=self.worker_id,
            item_id=self.item_id,
            sample_id=self.sample_id,
            operation_index=self.operation_index,
            operation_name=self.operation_name,
            view_name=self.view_name,
            rng_stream=self.rng_stream,
        )


@dataclass(frozen=True, slots=True)
class SampleReplayRecord:
    """Minimal immutable runtime replay record."""

    run_seed: object | None = None
    epoch: int | None = None
    worker_id: object | None = None
    item_id: object | None = None
    sample_id: object | None = None
    operation_index: int | None = None
    operation_name: str | None = None
    view_name: str | None = None
    rng_stream: object | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "epoch",
            _coerce_optional_int(
                self.epoch,
                field_name="epoch",
            ),
        )
        object.__setattr__(
            self,
            "operation_index",
            _coerce_optional_int(
                self.operation_index,
                field_name="operation_index",
            ),
        )
        object.__setattr__(
            self,
            "operation_name",
            coerce_non_empty_string(
                self.operation_name,
                owner="SampleReplayRecord",
                field="operation_name",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if self.operation_name is not None else None,
        )
        object.__setattr__(
            self,
            "view_name",
            coerce_non_empty_string(
                self.view_name,
                owner="SampleReplayRecord",
                field="view_name",
                expected="non-empty string or None",
                error_type=InvalidOperationContextError,
            ) if self.view_name is not None else None,
        )

    def to_mapping(self) -> Mapping[str, object | None]:
        """Export immutable scalar fields for lightweight evidence snapshots."""

        return MappingProxyType(
            {
                "run_seed": self.run_seed,
                "epoch": self.epoch,
                "worker_id": self.worker_id,
                "item_id": self.item_id,
                "sample_id": self.sample_id,
                "operation_index": self.operation_index,
                "operation_name": self.operation_name,
                "view_name": self.view_name,
                "rng_stream": self.rng_stream,
            }
        )


@dataclass(frozen=True, init=False, slots=True)
class SampleAugmentationParams:
    """Immutable lightweight parameters for reproducible sample augmentation.

    Allowed value leaves are dependency-light primitives and nested immutable
    structures. Field locators are normalized to exact ``FieldLocator`` objects,
    and string-keyed payload maps stay immutable. The record intentionally does
    not carry backend arrays, RNG objects, codecs, or field payload objects.
    """

    values: Mapping[str, object]
    linked_fields: tuple[tuple[FieldLocator, ...], ...]
    view_locators: Mapping[str, FieldLocator]

    def __init__(
        self,
        *,
        values: Mapping[str, object] | None = None,
        linked_fields: Sequence[Sequence[FieldLocator | str] | FieldLocator | str] | None = None,
        view_locators: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "values",
            _coerce_augmentation_values(
                values,
                owner="SampleAugmentationParams",
                field="values",
            ),
        )
        object.__setattr__(
            self,
            "linked_fields",
            _coerce_augmentation_linked_fields(
                linked_fields,
                owner="SampleAugmentationParams",
                field="linked_fields",
            ),
        )
        object.__setattr__(
            self,
            "view_locators",
            _coerce_augmentation_view_locators(
                view_locators,
                owner="SampleAugmentationParams",
                field="view_locators",
            ),
        )

    def to_mapping(self) -> Mapping[str, object]:
        """Export lightweight parameter evidence for replay records."""

        return MappingProxyType(
            {
                "values": self.values,
                "linked_fields": tuple(
                    tuple(str(locator) for locator in group)
                    for group in self.linked_fields
                ),
                "view_locators": MappingProxyType(
                    {
                        name: str(locator)
                        for name, locator in self.view_locators.items()
                    }
                ),
            }
        )


class SampleOperation(OperationStep):
    """Callable-first sample adapter implementing :class:`OperationStep`."""

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: SampleOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        if not callable(function):
            raise InvalidOperationContractError(
                "sample operation function must be callable.",
                owner="SampleOperation",
                field="function",
                expected="callable",
                actual=type(function).__name__,
            )

        resolved_contract = SampleOperationContract() if contract is None else contract
        if not isinstance(resolved_contract, SampleOperationContract):
            raise InvalidOperationContractError(
                "operation contract must be a SampleOperationContract.",
                owner="SampleOperation",
                field="contract",
                expected="SampleOperationContract",
                actual=type(contract).__name__,
            )

        resolved_name = _infer_name(name, function)
        if not isinstance(resolved_name, str) or not resolved_name.strip():
            raise InvalidOperationContractError(
                "operation name must be a non-empty string.",
                owner="SampleOperation",
                field="name",
                expected="non-empty string",
                actual=repr(resolved_name),
            )

        resolved_copy_mode = resolved_contract.copy_mode
        if copy_mode is not None:
            requested_copy_mode = _coerce_copy_mode(copy_mode, owner="SampleOperation")
            if resolved_contract._copy_mode_explicit and resolved_copy_mode != requested_copy_mode:
                raise InvalidOperationContractError(
                    "sample operation copy_mode conflicts with contract copy_mode.",
                    owner="SampleOperation",
                    field="copy_mode",
                    expected=resolved_copy_mode,
                    actual=requested_copy_mode,
                )
            resolved_copy_mode = requested_copy_mode

        self._function = function
        self._name = resolved_name
        self._sample_contract = resolved_contract
        self._copy_mode = resolved_copy_mode
        self._contract = resolved_contract.contract

    @property
    def name(self) -> str:
        """Readable operation identifier for diagnostics."""

        return self._name

    @property
    def sample_contract(self) -> SampleOperationContract:
        """Specialized sample contract retained for field-aware inspection."""

        return self._sample_contract

    @property
    def copy_mode(self) -> str:
        """Execution copy policy."""

        return self._copy_mode

    @property
    def contract(self) -> OperationContract:
        """Adapted generic contract for pipeline compatibility."""

        return self._contract

    def run(
        self,
        input_value: object,
        context: OperationContext | SampleOperationContext | None = None,
    ) -> OperationResult:
        execution_context = _coerce_sample_operation_context(
            context,
            operation_name=self._name,
        )
        _validate_required_context(
            self._sample_contract.required_context,
            execution_context.metadata,
            operation_name=self._name,
            role=self._contract.role,
        )
        _validate_input(
            self._contract.input_type,
            input_value,
            operation_name=self._name,
        )
        _validate_required_reads(
            input_value,
            self._sample_contract.field_permissions.reads,
            operation_name=self._name,
        )

        execution_sample = _prepare_execution_sample(input_value, self._copy_mode)
        before_snapshot = _snapshot_field_items(execution_sample)

        try:
            result = self._function(execution_sample, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "sample operation callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="run",
            ) from exc

        normalized_result = _coerce_and_validate_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context.to_operation_context(),
        )

        if normalized_result.output is not execution_sample:
            raise InvalidOperationResultError(
                "sample operation must return the execution sample object.",
                operation_name=self._name,
                field="output",
                expected="execution sample object",
                actual=type(normalized_result.output).__name__,
            )

        if "sample_field_effects" in normalized_result.metadata:
            raise InvalidOperationResultError(
                "sample operation result metadata collides with runtime field-effect key.",
                operation_name=self._name,
                field="metadata.sample_field_effects",
                expected="absent",
                actual="present",
            )

        after_snapshot = _snapshot_field_items(execution_sample)
        effects = _compute_sample_field_effects(before_snapshot, after_snapshot)
        _validate_sample_field_permissions(
            self._name,
            self._sample_contract.field_permissions,
            effects,
        )

        return _attach_sample_field_effects(
            normalized_result,
            self._copy_mode,
            effects,
        )

    def __call__(
        self,
        input_value: object,
        context: OperationContext | SampleOperationContext | None = None,
    ) -> OperationResult:
        """Execute and return a normalized :class:`OperationResult`."""

        return self.run(input_value, context=context)


class SampleTransform(SampleOperation):
    """Deterministic transform wrapper with output intent checks."""

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: SampleOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        resolved_contract = SampleOperationContract() if contract is None else contract
        if not isinstance(resolved_contract, SampleOperationContract):
            raise InvalidOperationContractError(
                "operation contract must be a SampleOperationContract.",
                owner="SampleTransform",
                field="contract",
                expected="SampleOperationContract",
                actual=type(contract).__name__,
            )
        if (
            len(resolved_contract.field_permissions.writes) == 0
            and len(resolved_contract.field_permissions.dynamic_writes) == 0
        ):
            raise InvalidOperationContractError(
                "sample transform operations must declare output fields via writes or dynamic_writes.",
                owner="SampleTransform",
                field="contract.field_permissions",
                expected="writes or dynamic_writes",
                actual="none",
            )
        super().__init__(
            function,
            name=name,
            contract=resolved_contract,
            copy_mode=copy_mode,
        )


@dataclass(frozen=True, slots=True)
class SampleDecision:
    """Informational deterministic decision output from a sample check."""

    label: str
    reason: str | None = None
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        label = coerce_non_empty_string(
            self.label,
            owner="SampleDecision",
            field="label",
            expected="non-empty string",
            error_type=InvalidOperationResultError,
        )
        reason = (
            coerce_non_empty_string(
                self.reason,
                owner="SampleDecision",
                field="reason",
                expected="non-empty string or None",
                error_type=InvalidOperationResultError,
            )
            if self.reason is not None
            else None
        )
        object.__setattr__(
            self,
            "label",
            label,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                self.metadata,
                owner="SampleDecision",
                field="metadata",
                error_type=InvalidOperationResultError,
            ),
        )


@dataclass(frozen=True, slots=True)
class SampleRoute:
    """Informational routing record emitted by a sample check."""

    label: str
    reason: str | None = None
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        label = coerce_non_empty_string(
            self.label,
            owner="SampleRoute",
            field="label",
            expected="non-empty string",
            error_type=InvalidOperationResultError,
        )
        reason = (
            coerce_non_empty_string(
                self.reason,
                owner="SampleRoute",
                field="reason",
                expected="non-empty string or None",
                error_type=InvalidOperationResultError,
            )
            if self.reason is not None
            else None
        )
        object.__setattr__(
            self,
            "label",
            label,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                self.metadata,
                owner="SampleRoute",
                field="metadata",
                error_type=InvalidOperationResultError,
            ),
        )


class SampleCheck(SampleOperation):
    """Deterministic sample check wrapper with optional decision/route records."""

    def run(
        self,
        input_value: object,
        context: OperationContext | SampleOperationContext | None = None,
    ) -> OperationResult:
        result = super().run(input_value, context=context)
        _validate_sample_check_metadata(
            result.metadata,
            operation_name=self._name,
        )
        return result


class SampleAugmentation(SampleOperation):
    """Sample operation with explicit sampling and deterministic application steps."""

    def __init__(
        self,
        sample_params: Callable[[Sample, SampleOperationContext], SampleAugmentationParams],
        apply_params: Callable[[Sample, SampleAugmentationParams, SampleOperationContext], Sample | OperationResult],
        *,
        name: str | None = None,
        contract: SampleOperationContract | None = None,
        copy_mode: str | None = None,
    ) -> None:
        if not callable(sample_params):
            raise InvalidOperationContractError(
                "sample augmentation sampler must be callable.",
                owner="SampleAugmentation",
                field="sample_params",
                expected="callable",
                actual=type(sample_params).__name__,
            )
        if not callable(apply_params):
            raise InvalidOperationContractError(
                "sample augmentation apply function must be callable.",
                owner="SampleAugmentation",
                field="apply_params",
                expected="callable",
                actual=type(apply_params).__name__,
            )

        super().__init__(
            _identity_sample,
            name=name,
            contract=contract,
            copy_mode=copy_mode,
        )
        self._sample_params_kernel = sample_params
        self._apply_params_kernel = apply_params

    @property
    def sample_params_kernel(self) -> Callable[[Sample, SampleOperationContext], SampleAugmentationParams]:
        """Expose the sampler for diagnostics and testing."""

        return self._sample_params_kernel

    @property
    def apply_params_kernel(self) -> Callable[
        [Sample, SampleAugmentationParams, SampleOperationContext],
        Sample | OperationResult,
    ]:
        """Expose the deterministic parameter application function."""

        return self._apply_params_kernel

    def sample_params(
        self,
        sample: Sample,
        context: OperationContext | SampleOperationContext,
    ) -> SampleAugmentationParams:
        """Sample deterministic parameters using the wrapped callable."""

        execution_context = _coerce_sample_operation_context(
            context,
            operation_name=self._name,
        )
        _validate_input(
            self._contract.input_type,
            sample,
            operation_name=self._name,
        )
        try:
            params = self._sample_params_kernel(sample, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "sample augmentation sampling callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="sample_params",
            ) from exc
        if not isinstance(params, SampleAugmentationParams):
            raise InvalidOperationResultError(
                "sample augmentation sampler must return SampleAugmentationParams.",
                operation_name=self._name,
                field="sample_params",
                expected="SampleAugmentationParams",
                actual=type(params).__name__,
            )
        return params

    def apply_params(
        self,
        sample: Sample,
        params: SampleAugmentationParams,
        context: OperationContext | SampleOperationContext,
    ) -> Sample | OperationResult:
        """Apply pre-sampled augmentation parameters deterministically."""

        execution_context = _coerce_sample_operation_context(
            context,
            operation_name=self._name,
        )
        _validate_input(
            self._contract.input_type,
            sample,
            operation_name=self._name,
        )
        if not isinstance(params, SampleAugmentationParams):
            raise InvalidOperationInputError(
                "sample augmentation apply params must be SampleAugmentationParams.",
                owner="SampleAugmentation",
                field="params",
                expected="SampleAugmentationParams",
                actual=type(params).__name__,
            )
        try:
            result = self._apply_params_kernel(
                sample,
                params,
                context=execution_context,
            )
        except Exception as exc:
            raise OperationExecutionError(
                "sample augmentation apply callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="apply_params",
            ) from exc

        if not isinstance(result, (Sample, OperationResult)):
            raise InvalidOperationResultError(
                "sample augmentation apply callable must return a Sample or OperationResult.",
                operation_name=self._name,
                field="apply_params",
                expected="Sample | OperationResult",
                actual=type(result).__name__,
            )

        return result

    def run(
        self,
        input_value: object,
        context: OperationContext | SampleOperationContext | None = None,
    ) -> OperationResult:
        execution_context = _coerce_sample_operation_context(
            context,
            operation_name=self._name,
        )
        _validate_required_context(
            self._sample_contract.required_context,
            execution_context.metadata,
            operation_name=self._name,
            role=self._contract.role,
        )
        _validate_input(
            self._contract.input_type,
            input_value,
            operation_name=self._name,
        )
        _validate_required_reads(
            input_value,
            self._sample_contract.field_permissions.reads,
            operation_name=self._name,
        )

        execution_sample = _prepare_execution_sample(input_value, self._copy_mode)
        before_snapshot = _snapshot_field_items(execution_sample)

        params = self.sample_params(execution_sample, execution_context)
        result = self.apply_params(
            execution_sample,
            params,
            execution_context,
        )

        normalized_result = _coerce_and_validate_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context.to_operation_context(),
        )
        if normalized_result.output is not execution_sample:
            raise InvalidOperationResultError(
                "sample augmentation must return the execution sample object.",
                operation_name=self._name,
                field="output",
                expected="execution sample object",
                actual=type(normalized_result.output).__name__,
            )
        if "sample_augmentation_replay" in normalized_result.metadata:
            raise InvalidOperationResultError(
                "sample augmentation result metadata collides with reserved key.",
                operation_name=self._name,
                field="metadata.sample_augmentation_replay",
                expected="absent",
                actual="present",
            )

        after_snapshot = _snapshot_field_items(execution_sample)
        effects = _compute_sample_field_effects(before_snapshot, after_snapshot)
        _validate_sample_field_permissions(
            self._name,
            self._sample_contract.field_permissions,
            effects,
        )

        effect_result = _attach_sample_field_effects(
            normalized_result,
            self._copy_mode,
            effects,
        )
        return _attach_sample_augmentation_replay(
            effect_result,
            augmentation_name=self._name,
            params=params,
            context=execution_context.to_replay_record(),
        )


def _infer_name(
    explicit_name: str | None,
    function: FunctionalKernel,
) -> str:
    if explicit_name is not None:
        return explicit_name

    explicit_name = getattr(function, "__name__", None)
    if isinstance(explicit_name, str) and explicit_name.strip():
        return explicit_name
    return function.__class__.__name__


def _coerce_copy_mode(
    value: str,
    *,
    owner: str = "SampleOperationContract",
    field: str = "copy_mode",
) -> str:
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


def _coerce_augmentation_values(
    values: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> Mapping[str, object]:
    if values is None:
        return MappingProxyType({})
    if not isinstance(values, Mapping):
        raise InvalidOperationInputError(
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
            error_type=InvalidOperationInputError,
        )
        normalized[normalized_key] = _coerce_augmentation_value(
            value,
            owner=owner,
            field=f"{field}[{normalized_key}]",
        )
    return MappingProxyType(normalized)


def _coerce_augmentation_value(value: object, *, owner: str, field: str) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, Mapping):
        return _coerce_augmentation_values(
            value,
            owner=owner,
            field=field,
        )

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(
            _coerce_augmentation_value(
                item,
                owner=owner,
                field=f"{field}[{index}]",
            )
            for index, item in enumerate(value)
        )

    raise InvalidOperationInputError(
        f"{owner} {field} contains unsupported augmentation value.",
        owner=owner,
        field=field,
        expected="None, bool, int, float, str, tuple, or string-keyed mapping",
        actual=type(value).__name__,
    )


def _coerce_augmentation_linked_fields(
    linked_fields: Sequence[Sequence[FieldLocator | str] | FieldLocator | str] | None,
    *,
    owner: str,
    field: str,
) -> tuple[tuple[FieldLocator, ...], ...]:
    if linked_fields is None:
        return ()
    if isinstance(linked_fields, (str, bytes, bytearray)):
        raise InvalidOperationInputError(
            f"{owner} {field} must be a sequence of locator groups.",
            owner=owner,
            field=field,
            expected="tuple[tuple[FieldLocator, ...], ...]",
            actual=type(linked_fields).__name__,
        )
    if not isinstance(linked_fields, Sequence):
        raise InvalidOperationInputError(
            f"{owner} {field} must be a sequence of locator groups.",
            owner=owner,
            field=field,
            expected="tuple[tuple[FieldLocator, ...], ...]",
            actual=type(linked_fields).__name__,
        )

    groups: list[tuple[FieldLocator, ...]] = []
    seen: set[FieldLocator] = set()

    for group_index, group in enumerate(linked_fields):
        if not isinstance(group, Sequence) or isinstance(group, (str, bytes, bytearray)):
            raise InvalidOperationInputError(
                f"{owner} {field} groups must be sequences of locators.",
                owner=owner,
                field=f"{field}[{group_index}]",
                expected="tuple[FieldLocator | str, ...]",
                actual=type(group).__name__,
            )
        parsed_group = _coerce_locator_sequence(
            group,
            owner=owner,
            field_name=f"{field}[{group_index}]",
        )
        if len(parsed_group) < 2:
            raise InvalidOperationInputError(
                f"{owner} {field}[{group_index}] must include at least two locators.",
                owner=owner,
                field=f"{field}[{group_index}]",
                expected="tuple with at least two locators",
                actual=parsed_group,
            )
        if len(set(parsed_group)) != len(parsed_group):
            raise InvalidOperationInputError(
                f"{owner} {field}[{group_index}] must not repeat locators.",
                owner=owner,
                field=f"{field}[{group_index}]",
                expected="distinct locators",
                actual=tuple(str(item) for item in parsed_group),
            )
        for locator in parsed_group:
            if locator in seen:
                raise InvalidOperationInputError(
                    f"{owner} {field} locators must be unique across groups.",
                    owner=owner,
                    field=field,
                    expected="disjoint locator groups",
                    actual=str(locator),
                )
            seen.add(locator)
        groups.append(parsed_group)
    return tuple(groups)


def _coerce_augmentation_view_locators(
    view_locators: Mapping[object, object] | None,
    *,
    owner: str,
    field: str,
) -> Mapping[str, FieldLocator]:
    if view_locators is None:
        return MappingProxyType({})
    if not isinstance(view_locators, Mapping):
        raise InvalidOperationInputError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            expected="mapping[str, FieldLocator]",
            actual=type(view_locators).__name__,
        )

    normalized: dict[str, FieldLocator] = {}
    for name, locator in view_locators.items():
        normalized_name = coerce_non_empty_string(
            name,
            owner=owner,
            field=f"{field}.key",
            expected="non-empty string keys",
            error_type=InvalidOperationInputError,
        )
        normalized[normalized_name] = _coerce_locator(
            locator,
            owner=owner,
            field_name=f"{field}[{normalized_name}]",
        )
    return MappingProxyType(normalized)


def _identity_sample(payload: Sample, *, context: SampleOperationContext) -> Sample:
    """No-op deterministic identity kernel for parent constructor initialization."""

    return payload


def _attach_sample_augmentation_replay(
    result: OperationResult,
    *,
    augmentation_name: str,
    params: SampleAugmentationParams,
    context: SampleReplayRecord,
) -> OperationResult:
    """Attach lightweight augmentation replay evidence."""

    replay = {
        "operation_name": augmentation_name,
        "context": context.to_mapping(),
        "params": params.to_mapping(),
        "linked_fields": params.to_mapping()["linked_fields"],
        "view_locators": params.to_mapping()["view_locators"],
    }
    metadata = dict(result.metadata)
    metadata["sample_augmentation_replay"] = replay

    return OperationResult(
        output=result.output,
        operation_name=result.operation_name,
        role=result.role,
        metadata=metadata,
        provenance=result.provenance,
        side_effect_evidence=result.side_effect_evidence,
    )


def _prepare_execution_sample(
    sample: Sample,
    copy_mode: str,
) -> Sample:
    if copy_mode == "in_place":
        return sample
    if copy_mode == "shallow":
        return sample.shallow_copy()
    return sample.deep_copy()


def _snapshot_field_items(sample: Sample) -> tuple[tuple[FieldLocator, FieldValue], ...]:
    """Snapshot field identity from non-payload access."""

    return tuple(sample.field_items())


def _compute_sample_field_effects(
    before_snapshot: tuple[tuple[FieldLocator, FieldValue], ...],
    after_snapshot: tuple[tuple[FieldLocator, FieldValue], ...],
) -> dict[str, tuple[FieldLocator, ...]]:
    before_map = {locator: value for locator, value in before_snapshot}
    after_map = {locator: value for locator, value in after_snapshot}

    added = tuple(locator for locator in after_map if locator not in before_map)
    removed = tuple(locator for locator in before_map if locator not in after_map)
    replaced = tuple(
        locator
        for locator, value in after_map.items()
        if locator in before_map and before_map[locator] is not value
    )
    return {"added": added, "removed": removed, "replaced": replaced}


def _validate_sample_field_permissions(
    operation_name: str,
    permissions: SampleFieldPermissions,
    effects: dict[str, tuple[FieldLocator, ...]],
) -> None:
    writes = set(permissions.writes)
    deletes = set(permissions.deletes)
    dynamic_writes = set(permissions.dynamic_writes)
    allowed_add = writes | dynamic_writes
    allowed_replace = writes | dynamic_writes

    for locator in effects["added"]:
        if locator not in allowed_add:
            raise UndeclaredSampleFieldMutationError(
                "sample operation attempted undeclared field addition.",
                operation_name=operation_name,
                effect_type="added",
                locator=str(locator),
                declared_writes=tuple(str(item) for item in permissions.writes),
                declared_deletes=tuple(str(item) for item in permissions.deletes),
                declared_dynamic_writes=tuple(str(item) for item in permissions.dynamic_writes),
                detected_added=tuple(str(item) for item in effects["added"]),
                detected_removed=tuple(str(item) for item in effects["removed"]),
                detected_replaced=tuple(str(item) for item in effects["replaced"]),
            )

    for locator in effects["removed"]:
        if locator not in deletes:
            raise UndeclaredSampleFieldMutationError(
                "sample operation attempted undeclared field deletion.",
                operation_name=operation_name,
                effect_type="removed",
                locator=str(locator),
                declared_writes=tuple(str(item) for item in permissions.writes),
                declared_deletes=tuple(str(item) for item in permissions.deletes),
                declared_dynamic_writes=tuple(str(item) for item in permissions.dynamic_writes),
                detected_added=tuple(str(item) for item in effects["added"]),
                detected_removed=tuple(str(item) for item in effects["removed"]),
                detected_replaced=tuple(str(item) for item in effects["replaced"]),
            )

    for locator in effects["replaced"]:
        if locator not in allowed_replace:
            raise UndeclaredSampleFieldMutationError(
                "sample operation attempted undeclared field replacement.",
                operation_name=operation_name,
                effect_type="replaced",
                locator=str(locator),
                declared_writes=tuple(str(item) for item in permissions.writes),
                declared_deletes=tuple(str(item) for item in permissions.deletes),
                declared_dynamic_writes=tuple(str(item) for item in permissions.dynamic_writes),
                detected_added=tuple(str(item) for item in effects["added"]),
                detected_removed=tuple(str(item) for item in effects["removed"]),
                detected_replaced=tuple(str(item) for item in effects["replaced"]),
            )


def _attach_sample_field_effects(
    result: OperationResult,
    copy_mode: str,
    effects: dict[str, tuple[FieldLocator, ...]],
) -> OperationResult:
    if "sample_field_effects" in result.metadata:
        raise InvalidOperationResultError(
            "sample operation result metadata collides with runtime field-effect key.",
            operation_name=result.operation_name,
            field="metadata.sample_field_effects",
            expected="absent",
            actual="present",
        )

    metadata = dict(result.metadata)
    metadata["sample_field_effects"] = {
        "copy_mode": copy_mode,
        "added": tuple(str(locator) for locator in effects["added"]),
        "removed": tuple(str(locator) for locator in effects["removed"]),
        "replaced": tuple(str(locator) for locator in effects["replaced"]),
    }

    return OperationResult(
        output=result.output,
        operation_name=result.operation_name,
        role=result.role,
        metadata=metadata,
        provenance=result.provenance,
        side_effect_evidence=result.side_effect_evidence,
    )


def _validate_sample_check_metadata(
    metadata: Mapping[str, object],
    *,
    operation_name: str,
) -> None:
    if "sample_decision" in metadata:
        _validate_sample_check_meta_record(
            metadata["sample_decision"],
            "sample_decision",
            SampleDecision,
            operation_name=operation_name,
        )

    if "sample_route" in metadata:
        _validate_sample_check_meta_record(
            metadata["sample_route"],
            "sample_route",
            SampleRoute,
            operation_name=operation_name,
        )


def _validate_sample_check_meta_record(
    value: object,
    field_name: str,
    record_type: type[SampleDecision] | type[SampleRoute],
    *,
    operation_name: str,
) -> None:
    if isinstance(value, record_type):
        return

    if isinstance(value, tuple):
        if not value:
            raise InvalidOperationResultError(
                "sample check metadata tuple must be non-empty.",
                operation_name=operation_name,
                field=f"metadata.{field_name}",
                expected=f"non-empty tuple[{record_type.__name__}]",
                actual="empty tuple",
            )
        if not all(isinstance(item, record_type) for item in value):
            raise InvalidOperationResultError(
                "sample check metadata tuple types must be homogeneous.",
                operation_name=operation_name,
                field=f"metadata.{field_name}",
                expected=f"tuple[{record_type.__name__}]",
                actual=tuple(type(item).__name__ for item in value),
            )
        return

    raise InvalidOperationResultError(
        "sample check metadata field must be a record or a non-empty tuple of records.",
        operation_name=operation_name,
        field=f"metadata.{field_name}",
        expected=f"{record_type.__name__} | tuple[{record_type.__name__}]",
        actual=type(value).__name__,
    )


def _coerce_locator(
    value: FieldLocator | str,
    *,
    owner: str,
    field_name: str,
) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    if not isinstance(value, str):
        raise InvalidFieldLocatorError(
            f"{owner} {field_name} entries must be FieldLocator or locator strings.",
            owner=owner,
            field=field_name,
            expected="FieldLocator or locator string",
            actual=type(value).__name__,
            locator=value,
        )

    try:
        return FieldLocator.parse(value)
    except InvalidFieldLocatorError as exc:
        raise InvalidFieldLocatorError(
            "invalid field declaration in SampleOperationContract.",
            owner=owner,
            field=field_name,
            locator=value,
        ) from exc


def _coerce_locator_sequence(
    value: Sequence[FieldLocator | str] | FieldLocator | str | None,
    *,
    owner: str,
    field_name: str,
) -> tuple[FieldLocator, ...]:
    if value is None:
        return ()
    if isinstance(value, (FieldLocator, str)):
        value = (value,)

    if isinstance(value, (bytes, bytearray)):
        raise InvalidOperationContractError(
            f"{owner} {field_name} must be a locator sequence.",
            owner=owner,
            field=field_name,
            expected="tuple/list of FieldLocator or str",
            actual=type(value).__name__,
        )

    if not isinstance(value, Sequence):
        raise InvalidOperationContractError(
            f"{owner} {field_name} must be a locator sequence.",
            owner=owner,
            field=field_name,
            expected="tuple/list of FieldLocator or str",
            actual=type(value).__name__,
        )

    return tuple(
        _coerce_locator(
            locator,
            owner=owner,
            field_name=field_name,
        )
        for locator in value
    )


def _validate_locator_collection_uniqueness(
    locators: tuple[FieldLocator, ...],
    *,
    owner: str,
    field_name: str,
) -> None:
    if len(locators) != len(set(locators)):
        raise InvalidOperationContractError(
            f"{owner} {field_name} contains duplicate locator declarations.",
            owner=owner,
            field=field_name,
            expected="unique locators",
            actual=tuple(locators),
        )


def _validate_non_overlapping_permissions(
    writes: tuple[FieldLocator, ...],
    deletes: tuple[FieldLocator, ...],
    dynamic_writes: tuple[FieldLocator, ...],
) -> None:
    writes_set = set(writes)
    deletes_set = set(deletes)
    dynamic_set = set(dynamic_writes)

    write_delete_overlap = tuple(
        locator for locator in writes_set
        if locator in deletes_set
    )
    if write_delete_overlap:
        raise InvalidOperationContractError(
            "writes and deletes cannot declare the same locator.",
            owner="SampleFieldPermissions",
            field="field_permissions",
            expected="disjoint writes and deletes",
            actual=write_delete_overlap,
        )

    dynamic_write_overlap = tuple(
        locator for locator in dynamic_set
        if locator in writes_set
    )
    if dynamic_write_overlap:
        raise InvalidOperationContractError(
            "dynamic writes cannot duplicate explicit writes.",
            owner="SampleFieldPermissions",
            field="field_permissions.dynamic_writes",
            expected="disjoint dynamic_writes and writes",
            actual=dynamic_write_overlap,
        )


def _coerce_sample_operation_context(
    context: OperationContext | SampleOperationContext | None,
    *,
    operation_name: str,
) -> SampleOperationContext:
    if context is None:
        return SampleOperationContext(operation_name=operation_name)

    if isinstance(context, SampleOperationContext):
        if context.operation_name is None:
            return SampleOperationContext(
                metadata=context.metadata,
                provenance=context.provenance,
                run_seed=context.run_seed,
                epoch=context.epoch,
                worker_id=context.worker_id,
                item_id=context.item_id,
                sample_id=context.sample_id,
                operation_index=context.operation_index,
                operation_name=operation_name,
                view_name=context.view_name,
                rng_stream=context.rng_stream,
            )
        if context.operation_name != operation_name:
            raise InvalidOperationContextError(
                "sample operation context operation_name must match the executing operation.",
                field="context.operation_name",
                expected=operation_name,
                actual=context.operation_name,
            )
        return context

    if not isinstance(context, OperationContext):
        raise InvalidOperationContextError(
            "operation context must be None, OperationContext, or SampleOperationContext.",
            field="context",
            expected="OperationContext | SampleOperationContext | None",
            actual=type(context).__name__,
        )

    return SampleOperationContext(
        metadata=context.metadata,
        provenance=context.provenance,
        operation_name=operation_name,
    )


def _validate_required_reads(
    sample: object,
    reads: tuple[FieldLocator, ...],
    *,
    operation_name: str,
) -> None:
    if not isinstance(sample, Sample):
        return
    for locator in reads:
        if not sample.has(locator):
            raise MissingFieldError(
                "operation required sample field is missing.",
                operation_name=operation_name,
                locator=str(locator),
            )


def _coerce_optional_int(
    value: object | None,
    *,
    field_name: str,
) -> int | None:
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


SampleDecision.__hash__ = None  # type: ignore[assignment]
SampleRoute.__hash__ = None  # type: ignore[assignment]
SampleOperationContext.__hash__ = None  # type: ignore[assignment]
SampleReplayRecord.__hash__ = None  # type: ignore[assignment]
SampleOperationContract.__hash__ = None  # type: ignore[assignment]
SampleFieldPermissions.__hash__ = None  # type: ignore[assignment]
SampleAugmentationParams.__hash__ = None  # type: ignore[assignment]
SampleAugmentation.__hash__ = None  # type: ignore[assignment]
