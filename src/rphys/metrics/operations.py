"""Field-native metric operation adapters."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from rphys.collections import CollectionItem
from rphys.data import Batch, FieldValue, Sample
from rphys.data.collections import SampleCollection
from rphys.data.locators import FieldLocator
from rphys.errors import (
    InvalidMetricContextError,
    InvalidMetricResultError,
    InvalidMetricSpecError,
    InvalidOperationContextError,
    InvalidOperationResultError,
    OperationExecutionError,
)
from rphys.ops.context import OperationContext, OperationResult
from rphys.ops.contracts import OperationContract, OperationRole
from rphys.ops.core import OperationStep
from rphys.ops.sample import (
    SampleFieldPermissions,
    SampleOperation,
    SampleOperationContext,
    SampleOperationContract,
)

from .context import MetricContext
from .core import Metric
from .results import MetricValue
from .specs import MetricContract

__all__ = [
    "MetricCollectionOperation",
    "MetricSampleOperation",
    "collect_metric_fields",
]


def collect_metric_fields(
    metric: Metric,
    context: MetricContext,
) -> Mapping[FieldLocator, FieldValue]:
    """Run ``metric`` and bind its output to declared ``MetricContract.writes``.

    A metric with one declared write may return a single ``MetricValue``,
    ``FieldValue``, or raw detached scalar. Metrics with multiple declared
    writes must return a mapping. All returned fields must be declared, and all
    declared writes must be produced so missing metric values are explicit.
    """

    _validate_metric(metric)
    if not isinstance(context, MetricContext):
        raise InvalidMetricContextError(
            "collect_metric_fields requires a MetricContext.",
            owner="collect_metric_fields",
            field="context",
            expected="MetricContext",
            actual=type(context).__name__,
        )
    try:
        output = metric(context)
    except Exception as exc:
        raise InvalidMetricResultError(
            "Metric callable raised while producing metric fields.",
            owner="collect_metric_fields",
            field="metric",
            metric=metric.contract.name,
        ) from exc
    return bind_metric_fields(output, contract=context.contract)


def bind_metric_fields(
    output: object,
    *,
    contract: MetricContract,
) -> Mapping[FieldLocator, FieldValue]:
    """Normalize a metric callable output into immutable field values."""

    if not isinstance(contract, MetricContract):
        raise InvalidMetricSpecError(
            "bind_metric_fields requires a MetricContract.",
            owner="bind_metric_fields",
            field="contract",
            expected="MetricContract",
            actual=type(contract).__name__,
        )
    if not contract.writes:
        raise InvalidMetricResultError(
            "Metric contracts must declare writes before outputs can be field-bound.",
            owner="bind_metric_fields",
            field="contract.writes",
            metric=contract.name,
        )

    if isinstance(output, Mapping):
        resolved = {
            _coerce_output_locator(locator): _coerce_output_field(value, contract=contract)
            for locator, value in output.items()
        }
    else:
        if len(contract.writes) != 1:
            raise InvalidMetricResultError(
                "Single metric outputs require exactly one declared write.",
                owner="bind_metric_fields",
                field="output",
                metric=contract.name,
                declared=tuple(str(locator) for locator in contract.writes),
            )
        resolved = {contract.writes[0]: _coerce_output_field(output, contract=contract)}

    undeclared = tuple(locator for locator in resolved if locator not in contract.writes)
    if undeclared:
        raise InvalidMetricResultError(
            "Metric output includes undeclared field locators.",
            owner="bind_metric_fields",
            field="output",
            metric=contract.name,
            undeclared=tuple(str(locator) for locator in undeclared),
            declared=tuple(str(locator) for locator in contract.writes),
        )
    missing = tuple(locator for locator in contract.writes if locator not in resolved)
    if missing:
        raise InvalidMetricResultError(
            "Metric output is missing declared field locators.",
            owner="bind_metric_fields",
            field="output",
            metric=contract.name,
            missing=tuple(str(locator) for locator in missing),
        )
    return MappingProxyType(dict(resolved))


class MetricSampleOperation(SampleOperation):
    """Adapt a field-native metric into a sample operation.

    The operation reads the fields declared by ``MetricContract.inputs`` from a
    ``Sample`` and writes the exact declared ``metrics/*`` fields back onto the
    returned sample. No observation rows, evaluator state, or prediction
    storage are created.
    """

    def __init__(
        self,
        metric: Metric,
        *,
        name: str | None = None,
        copy_mode: str = "shallow",
    ) -> None:
        _validate_metric(metric)
        self.metric = metric
        super().__init__(
            self._apply_metric,
            name=name or metric.contract.name,
            contract=SampleOperationContract(
                field_permissions=SampleFieldPermissions(
                    reads=tuple(input_spec.locator for input_spec in metric.contract.inputs),
                    writes=metric.contract.writes,
                ),
                failure_modes=(
                    "missing_metric_input",
                    "metric_callable_failed",
                    "metric_output_contract_mismatch",
                    "metric_field_conflict",
                ),
            ),
            copy_mode=copy_mode,
        )

    def _apply_metric(
        self,
        sample: Sample,
        *,
        context: SampleOperationContext,
    ) -> Sample:
        fields = collect_metric_fields(
            self.metric,
            MetricContext(
                self.metric.contract,
                fields=sample,
                samples=SampleCollection(
                    (CollectionItem(sample, metadata=_metric_sample_item_metadata(context)),),
                    metadata={"metric_scope": "sample"},
                    provenance=context.provenance,
                ),
                metadata={**context.metadata, "metric_scope": "sample"},
                provenance=context.provenance,
            ),
        )
        _write_metric_fields(sample, fields, owner="MetricSampleOperation")
        return sample


class MetricCollectionOperation(OperationStep):
    """Apply a metric to a ``SampleCollection`` and return metric-bearing samples.

    The adapter copies collection members, runs the metric with both
    ``MetricContext.samples`` and a collection-level field view when available,
    then writes declared metric fields onto each returned sample. Replication is
    explicit in collection metadata and provenance so downstream reductions can
    distinguish collection-level metric fields from per-sample metric calls.
    """

    def __init__(
        self,
        metric: Metric,
        *,
        name: str | None = None,
    ) -> None:
        _validate_metric(metric)
        self.metric = metric
        self._name = name or metric.contract.name
        self._contract = OperationContract(
            input_type=SampleCollection,
            output_type=SampleCollection,
            failure_modes=(
                "empty_collection",
                "metric_callable_failed",
                "metric_output_contract_mismatch",
                "metric_field_conflict",
            ),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def contract(self) -> OperationContract:
        return self._contract

    def run(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        if not isinstance(input_value, SampleCollection):
            raise InvalidOperationResultError(
                "MetricCollectionOperation input must be a SampleCollection.",
                operation_name=self.name,
                field="input_value",
                expected="SampleCollection",
                actual=type(input_value).__name__,
            )
        execution_context = _coerce_operation_context(context)
        fields = collect_metric_fields(
            self.metric,
            MetricContext(
                self.metric.contract,
                samples=input_value,
                metadata={
                    **execution_context.metadata,
                    "metric_scope": "sample_collection",
                    "source_count": len(input_value),
                },
                provenance={**input_value.provenance, **execution_context.provenance},
            ),
        )

        entries: list[CollectionItem[Sample]] = []
        for entry in input_value.entries:
            copied = entry.value.shallow_copy()
            _write_metric_fields(copied, fields, owner="MetricCollectionOperation")
            entries.append(
                CollectionItem(
                    copied,
                    metadata={
                        **entry.metadata,
                        "metric_operation": self.name,
                        "metric_fields": tuple(str(locator) for locator in fields),
                    },
                    provenance={**entry.provenance, "metric_operation": self.name},
                )
            )
        output = SampleCollection(
            tuple(entries),
            metadata={
                **input_value.metadata,
                "metric_operation": self.name,
                "metric_binding": "replicated_collection_fields",
                "metric_fields": tuple(str(locator) for locator in fields),
            },
            provenance={**input_value.provenance, "metric_operation": self.name},
        )
        return OperationResult(
            output,
            operation_name=self.name,
            role=OperationRole.GENERIC,
            metadata={
                **execution_context.metadata,
                "metric_fields": tuple(str(locator) for locator in fields),
                "source_count": len(input_value),
            },
            provenance={**execution_context.provenance, "metric": self.metric.contract.name},
        )

    def __call__(
        self,
        input_value: object,
        context: OperationContext | None = None,
    ) -> OperationResult:
        return self.run(input_value, context=context)


def _validate_metric(metric: object) -> None:
    contract = getattr(metric, "contract", None)
    if not callable(metric) or not isinstance(contract, MetricContract):
        raise InvalidMetricSpecError(
            "Metric adapters require a callable metric with a MetricContract.",
            owner="Metric",
            field="metric",
            expected="callable with MetricContract",
            actual=type(metric).__name__,
        )


def _coerce_output_locator(locator: object) -> FieldLocator:
    if isinstance(locator, FieldLocator):
        return locator
    try:
        return FieldLocator.parse(locator)  # type: ignore[arg-type]
    except Exception as exc:
        raise InvalidMetricResultError(
            "Metric output locators must be FieldLocator-compatible.",
            owner="bind_metric_fields",
            field="output",
            actual=repr(locator),
        ) from exc


def _coerce_output_field(value: object, *, contract: MetricContract) -> FieldValue:
    if isinstance(value, FieldValue):
        return value
    if isinstance(value, MetricValue):
        metadata = {
            "metric.name": contract.name,
            "metric.level": contract.level,
            "metric.detached": value.detached,
            "metric.differentiable": value.differentiable,
        }
        if value.backend is not None:
            metadata["metric.backend"] = value.backend
        if value.unit is not None:
            metadata["metric.unit"] = value.unit
        metadata.update(value.metadata)
        return FieldValue(value, metadata=metadata)
    return FieldValue(
        value,
        metadata={
            "metric.name": contract.name,
            "metric.level": contract.level,
        },
    )


def _write_metric_fields(
    container: Sample | Batch,
    fields: Mapping[FieldLocator, FieldValue],
    *,
    owner: str,
) -> None:
    for locator, field_value in fields.items():
        if container.has(locator):
            raise InvalidMetricResultError(
                "Metric operation output field conflicts with an existing field.",
                owner=owner,
                field="fields",
                locator=str(locator),
            )
        container.set_field(locator, field_value)


def _metric_sample_item_metadata(context: SampleOperationContext) -> Mapping[str, object]:
    metadata = dict(context.metadata)
    if context.sample_id is not None:
        metadata["sample_id"] = context.sample_id
    if context.item_id is not None:
        metadata["item_id"] = context.item_id
    return MappingProxyType(metadata)


def _coerce_operation_context(context: OperationContext | None) -> OperationContext:
    if context is None:
        return OperationContext()
    if isinstance(context, OperationContext):
        return context
    raise InvalidOperationContextError(
        "MetricCollectionOperation context must be an OperationContext.",
        operation_name="MetricCollectionOperation",
        field="context",
        expected="OperationContext | None",
        actual=type(context).__name__,
    )
