"""Sample operation foundations for Stage 7.

This module adds the first concrete public sample-bound execution primitive:
``SampleOperation``. It is a callable-first :class:`OperationStep` adapter that
keeps sample declarations, required-field preflight, and runtime result typing
separate from the generic Stage 6 operation contract and result schema.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from rphys.data import Sample
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidFieldLocatorError,
    InvalidOperationContractError,
    InvalidOperationContextError,
    MissingFieldError,
    OperationExecutionError,
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
    "SampleOperation",
]


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
    _operation_contract: OperationContract = field(init=False, repr=False)

    def __init__(
        self,
        *,
        field_permissions: SampleFieldPermissions | None = None,
        required_context: Sequence[str] | None = None,
        failure_modes: Sequence[str] | None = None,
        mutation_policy: OperationMutationPolicy | str = OperationMutationPolicy.PURE,
        side_effects: Sequence[str] | None = None,
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
        object.__setattr__(self, "_operation_contract", operation_contract)

    @property
    def contract(self) -> OperationContract:
        """Adapted generic operation contract."""

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


class SampleOperation(OperationStep):
    """Callable-first sample adapter implementing :class:`OperationStep`."""

    def __init__(
        self,
        function: FunctionalKernel,
        *,
        name: str | None = None,
        contract: SampleOperationContract | None = None,
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

        self._function = function
        self._name = resolved_name
        self._sample_contract = resolved_contract
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

        try:
            result = self._function(input_value, context=execution_context)
        except Exception as exc:
            raise OperationExecutionError(
                "sample operation callable raised during execution.",
                operation_name=self._name,
                role=self._contract.role.value,
                phase="run",
            ) from exc

        return _coerce_and_validate_result(
            result,
            operation_name=self._name,
            contract=self._contract,
            context=execution_context.to_operation_context(),
        )

    def __call__(
        self,
        input_value: object,
        context: OperationContext | SampleOperationContext | None = None,
    ) -> OperationResult:
        """Execute and return a normalized :class:`OperationResult`."""

        return self.run(input_value, context=context)


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


SampleOperationContext.__hash__ = None  # type: ignore[assignment]
SampleReplayRecord.__hash__ = None  # type: ignore[assignment]
SampleOperationContract.__hash__ = None  # type: ignore[assignment]
SampleFieldPermissions.__hash__ = None  # type: ignore[assignment]
