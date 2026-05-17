"""Assembled-object training plan records."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from rphys.data import Batch, BatchOutputFieldSpec, BatchOutputSpec
from rphys.data.fields import FieldValue
from rphys.data.locators import FieldLocator, FieldRole
from rphys.errors import RemotePhysLearningError, RemotePhysTrainingError
from rphys.learning import LoopMode, require_backwardable_scalar
from rphys.metrics import MetricValue

from .events import TrainingCallback, TrainingEventSink
from .profiling import TrainingProfiler
from ._validation import (
    PrimitiveMapping,
    coerce_optional_positive_int,
    coerce_positive_int,
    coerce_tuple,
    freeze_primitive_mapping,
)

__all__ = ["TrainingOutputSpec", "TrainingPlan"]

BatchIterable = Iterable[Batch]


@dataclass(frozen=True, slots=True)
class TrainingOutputSpec:
    """TrainingPlan-owned declaration of learner-returned ``Batch`` fields.

    Native engines read only fields declared here. Train mode requires an
    objective locator whose payload exposes ``backward()`` or can be handled by
    the plan's explicit backward hook.
    """

    objective: FieldLocator | str | None = None
    losses: Sequence[BatchOutputFieldSpec | FieldLocator | str] = ()
    metrics: Sequence[BatchOutputFieldSpec | FieldLocator | str] = ()
    diagnostics: Sequence[BatchOutputFieldSpec | FieldLocator | str] = ()
    required_by_mode: Mapping[LoopMode | str, Sequence[FieldLocator | str]] | None = None

    def __post_init__(self) -> None:
        objective_spec = None
        if self.objective is not None:
            objective_spec = BatchOutputFieldSpec(
                "objective",
                self.objective,
                required=False,
                allowed_roles=(FieldRole.OBJECTIVES,),
            )
        losses = _coerce_training_specs(self.losses, role=FieldRole.LOSSES, field="losses")
        metrics = _coerce_training_specs(self.metrics, role=FieldRole.METRICS, field="metrics")
        diagnostics = _coerce_training_specs(
            self.diagnostics,
            role=FieldRole.DIAGNOSTICS,
            field="diagnostics",
        )
        required_by_mode = _coerce_required_by_mode(self.required_by_mode)
        all_specs = tuple(
            spec
            for spec in (objective_spec, *losses, *metrics, *diagnostics)
            if spec is not None
        )
        _validate_unique_training_locators(all_specs, required_by_mode)
        object.__setattr__(self, "objective", None if objective_spec is None else objective_spec.locator)
        object.__setattr__(self, "losses", losses)
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "required_by_mode", required_by_mode)

    @property
    def fields(self) -> tuple[BatchOutputFieldSpec, ...]:
        """Return all declared training output fields."""

        objective = (
            ()
            if self.objective is None
            else (
                BatchOutputFieldSpec(
                    "objective",
                    self.objective,
                    required=False,
                    allowed_roles=(FieldRole.OBJECTIVES,),
                ),
            )
        )
        return (*objective, *self.losses, *self.metrics, *self.diagnostics)

    def validate_batch(self, batch: Batch, mode: LoopMode | str) -> Batch:
        """Validate the learner-returned batch for ``mode``."""

        resolved_mode = LoopMode.coerce(mode)
        BatchOutputSpec(self.fields).validate(batch, owner="TrainingOutputSpec")
        for locator in self.required_by_mode.get(resolved_mode, ()):
            if not batch.has(locator):
                raise RemotePhysTrainingError(
                    "Returned learner batch is missing a mode-required field.",
                    owner="TrainingOutputSpec",
                    mode=resolved_mode.value,
                    locator=str(locator),
                )
        if resolved_mode is LoopMode.TRAIN:
            if self.objective is None:
                raise RemotePhysTrainingError(
                    "Train mode requires TrainingOutputSpec.objective.",
                    owner="TrainingOutputSpec",
                    mode=resolved_mode.value,
                )
            if not batch.has(self.objective):
                raise RemotePhysTrainingError(
                    "Returned learner batch is missing the train objective field.",
                    owner="TrainingOutputSpec",
                    mode=resolved_mode.value,
                    field="objective",
                    locator=str(self.objective),
                )
            objective = batch.require(self.objective)
            try:
                require_backwardable_scalar(objective)
            except RemotePhysLearningError as exc:
                raise RemotePhysTrainingError(
                    "Returned learner batch objective field is not backwardable.",
                    owner="TrainingOutputSpec",
                    mode=resolved_mode.value,
                    field="objective",
                    locator=str(self.objective),
                    actual=type(objective).__name__,
                ) from exc
        return batch

    def objective_value(self, batch: Batch, mode: LoopMode | str) -> object | None:
        """Return the declared objective payload for train mode."""

        resolved_mode = LoopMode.coerce(mode)
        if resolved_mode is not LoopMode.TRAIN or self.objective is None:
            return None
        return batch.require(self.objective)

    def metric_values(self, batch: Batch) -> Mapping[str, object]:
        """Return declared metric field payloads present in ``batch``."""

        values: dict[str, object] = {}
        for spec in self.metrics:
            if not batch.has(spec.locator):
                continue
            payload = batch.require(spec.locator)
            values[str(spec.locator)] = payload
        return values

    def field_value(self, batch: Batch, locator: FieldLocator | str) -> FieldValue | None:
        """Return a declared field value when present."""

        resolved = FieldLocator.parse(locator) if isinstance(locator, str) else locator
        if not batch.has(resolved):
            return None
        return batch.field(resolved)


@dataclass(frozen=True, init=False, slots=True)
class TrainingPlan:
    """Caller-assembled inputs and loop limits for a selected training engine.

    The plan stores already-built batch iterables/loaders and backend hooks. It
    does not scan datasources, build dataloaders, parse project config, own a
    learner, create artifacts, or carry a generic ``engine_config`` escape
    hatch. Engine-specific configuration belongs on the selected engine or
    adapter object.
    """

    train_batches: BatchIterable | None
    validation_batches: BatchIterable | None
    test_batches: BatchIterable | None
    predict_batches: BatchIterable | None
    max_epochs: int
    max_train_steps: int | None
    max_validate_steps: int | None
    max_test_steps: int | None
    max_predict_steps: int | None
    device_mover: Callable[[Batch], Batch] | None
    optimizer: object | None
    scheduler: object | None
    backward: Callable[[object], object] | None
    output_spec: TrainingOutputSpec
    event_sinks: tuple[TrainingEventSink, ...]
    callbacks: tuple[TrainingCallback, ...]
    profilers: tuple[TrainingProfiler, ...]
    metadata: PrimitiveMapping
    provenance: PrimitiveMapping

    def __init__(
        self,
        *,
        train_batches: BatchIterable | None = None,
        validation_batches: BatchIterable | None = None,
        test_batches: BatchIterable | None = None,
        predict_batches: BatchIterable | None = None,
        max_epochs: int = 1,
        max_train_steps: int | None = None,
        max_validate_steps: int | None = None,
        max_test_steps: int | None = None,
        max_predict_steps: int | None = None,
        device_mover: Callable[[Batch], Batch] | None = None,
        optimizer: object | None = None,
        scheduler: object | None = None,
        backward: Callable[[object], object] | None = None,
        output_spec: TrainingOutputSpec | None = None,
        event_sinks: Iterable[TrainingEventSink] = (),
        callbacks: Iterable[TrainingCallback] = (),
        profilers: Iterable[TrainingProfiler] = (),
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "train_batches",
            _coerce_batches(train_batches, field="train_batches"),
        )
        object.__setattr__(
            self,
            "validation_batches",
            _coerce_batches(validation_batches, field="validation_batches"),
        )
        object.__setattr__(
            self,
            "test_batches",
            _coerce_batches(test_batches, field="test_batches"),
        )
        object.__setattr__(
            self,
            "predict_batches",
            _coerce_batches(predict_batches, field="predict_batches"),
        )
        object.__setattr__(
            self,
            "max_epochs",
            coerce_positive_int(max_epochs, owner="TrainingPlan", field="max_epochs"),
        )
        object.__setattr__(
            self,
            "max_train_steps",
            coerce_optional_positive_int(
                max_train_steps,
                owner="TrainingPlan",
                field="max_train_steps",
            ),
        )
        object.__setattr__(
            self,
            "max_validate_steps",
            coerce_optional_positive_int(
                max_validate_steps,
                owner="TrainingPlan",
                field="max_validate_steps",
            ),
        )
        object.__setattr__(
            self,
            "max_test_steps",
            coerce_optional_positive_int(
                max_test_steps,
                owner="TrainingPlan",
                field="max_test_steps",
            ),
        )
        object.__setattr__(
            self,
            "max_predict_steps",
            coerce_optional_positive_int(
                max_predict_steps,
                owner="TrainingPlan",
                field="max_predict_steps",
            ),
        )
        object.__setattr__(
            self,
            "device_mover",
            _coerce_optional_callable(device_mover, field="device_mover"),
        )
        object.__setattr__(self, "optimizer", optimizer)
        object.__setattr__(self, "scheduler", scheduler)
        object.__setattr__(
            self,
            "backward",
            _coerce_optional_callable(backward, field="backward"),
        )
        resolved_output_spec = _coerce_output_spec(output_spec)
        if self.train_batches is not None and resolved_output_spec.objective is None:
            raise RemotePhysTrainingError(
                "TrainingPlan with train_batches requires TrainingOutputSpec.objective.",
                owner="TrainingPlan",
                field="output_spec",
                mode=LoopMode.TRAIN.value,
            )
        object.__setattr__(self, "output_spec", resolved_output_spec)
        object.__setattr__(
            self,
            "event_sinks",
            _coerce_observers(event_sinks, field="event_sinks", method_name="record"),
        )
        object.__setattr__(
            self,
            "callbacks",
            _coerce_observers(callbacks, field="callbacks", method_name="on_event"),
        )
        object.__setattr__(
            self,
            "profilers",
            _coerce_observers(profilers, field="profilers", method_name="span"),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_primitive_mapping(
                metadata,
                owner="TrainingPlan",
                field="metadata",
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            freeze_primitive_mapping(
                provenance,
                owner="TrainingPlan",
                field="provenance",
            ),
        )

    def batches_for(self, mode: LoopMode | str) -> BatchIterable | None:
        """Return the configured batch iterable for a loop mode."""

        resolved = LoopMode.coerce(mode)
        if resolved is LoopMode.TRAIN:
            return self.train_batches
        if resolved is LoopMode.VALIDATE:
            return self.validation_batches
        if resolved is LoopMode.TEST:
            return self.test_batches
        if resolved is LoopMode.PREDICT:
            return self.predict_batches
        raise AssertionError("unreachable loop mode")

    def max_steps_for(self, mode: LoopMode | str) -> int | None:
        """Return the configured max-step limit for a loop mode."""

        resolved = LoopMode.coerce(mode)
        if resolved is LoopMode.TRAIN:
            return self.max_train_steps
        if resolved is LoopMode.VALIDATE:
            return self.max_validate_steps
        if resolved is LoopMode.TEST:
            return self.max_test_steps
        if resolved is LoopMode.PREDICT:
            return self.max_predict_steps
        raise AssertionError("unreachable loop mode")


def _coerce_batches(
    values: BatchIterable | None,
    *,
    field: str,
) -> BatchIterable | None:
    if values is None:
        return None
    batches = coerce_tuple(values, owner="TrainingPlan", field=field)
    assert batches is not None
    for index, batch in enumerate(batches):
        if not isinstance(batch, Batch):
            raise RemotePhysTrainingError(
                "TrainingPlan batch iterables must contain Batch objects.",
                owner="TrainingPlan",
                field=field,
                index=index,
                expected="Batch",
                actual=type(batch).__name__,
            )
    return batches


def _coerce_optional_callable(
    value: object | None,
    *,
    field: str,
) -> object | None:
    if value is None:
        return None
    if not callable(value):
        raise RemotePhysTrainingError(
            f"TrainingPlan {field} must be callable when provided.",
            owner="TrainingPlan",
            field=field,
            expected="callable | None",
            actual=type(value).__name__,
        )
    return value


def _coerce_observers(
    values: Iterable[object],
    *,
    field: str,
    method_name: str,
) -> tuple[object, ...]:
    try:
        observers = tuple(values)
    except TypeError as exc:
        raise RemotePhysTrainingError(
            f"TrainingPlan {field} must be iterable.",
            owner="TrainingPlan",
            field=field,
            expected="iterable",
            actual=type(values).__name__,
        ) from exc
    for index, observer in enumerate(observers):
        method = getattr(observer, method_name, None)
        if not callable(method):
            raise RemotePhysTrainingError(
                f"TrainingPlan {field} entries must expose {method_name}().",
                owner="TrainingPlan",
                field=field,
                index=index,
                expected=f"{method_name}()",
                actual=type(observer).__name__,
            )
    return observers


def _coerce_output_spec(value: TrainingOutputSpec | None) -> TrainingOutputSpec:
    if value is None:
        return TrainingOutputSpec()
    if not isinstance(value, TrainingOutputSpec):
        raise RemotePhysTrainingError(
            "TrainingPlan output_spec must be a TrainingOutputSpec.",
            owner="TrainingPlan",
            field="output_spec",
            expected="TrainingOutputSpec | None",
            actual=type(value).__name__,
        )
    return value


def _coerce_training_specs(
    values: Sequence[BatchOutputFieldSpec | FieldLocator | str],
    *,
    role: FieldRole,
    field: str,
) -> tuple[BatchOutputFieldSpec, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RemotePhysTrainingError(
            "TrainingOutputSpec field groups must be sequences.",
            owner="TrainingOutputSpec",
            field=field,
            actual=type(values).__name__,
        )
    specs: list[BatchOutputFieldSpec] = []
    for index, value in enumerate(values):
        if isinstance(value, BatchOutputFieldSpec):
            if value.locator.role is not role:
                raise RemotePhysTrainingError(
                    "TrainingOutputSpec field has the wrong role.",
                    owner="TrainingOutputSpec",
                    field=field,
                    index=index,
                    locator=str(value.locator),
                    expected=role.value,
                    actual=value.locator.role.value,
                )
            specs.append(value)
            continue
        specs.append(
            BatchOutputFieldSpec(
                f"{field}.{index}",
                value,
                required=False,
                allowed_roles=(role,),
            )
        )
    return tuple(specs)


def _coerce_required_by_mode(
    value: Mapping[LoopMode | str, Sequence[FieldLocator | str]] | None,
) -> Mapping[LoopMode, tuple[FieldLocator, ...]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise RemotePhysTrainingError(
            "TrainingOutputSpec required_by_mode must be a mapping.",
            owner="TrainingOutputSpec",
            field="required_by_mode",
            actual=type(value).__name__,
        )
    required: dict[LoopMode, tuple[FieldLocator, ...]] = {}
    for mode, locators in value.items():
        resolved_mode = LoopMode.coerce(mode)
        if isinstance(locators, (str, bytes)) or not isinstance(locators, Sequence):
            raise RemotePhysTrainingError(
                "TrainingOutputSpec mode-required locators must be a sequence.",
                owner="TrainingOutputSpec",
                field="required_by_mode",
                mode=resolved_mode.value,
                actual=type(locators).__name__,
            )
        required[resolved_mode] = tuple(
            FieldLocator.parse(locator) if isinstance(locator, str) else locator
            for locator in locators
        )
    return required


def _validate_unique_training_locators(
    specs: tuple[BatchOutputFieldSpec, ...],
    required_by_mode: Mapping[LoopMode, tuple[FieldLocator, ...]],
) -> None:
    locators: set[FieldLocator] = set()
    duplicates: list[str] = []
    for spec in specs:
        if spec.locator in locators:
            duplicates.append(str(spec.locator))
        locators.add(spec.locator)
    for required in required_by_mode.values():
        for locator in required:
            if locator in locators:
                continue
            locators.add(locator)
    if duplicates:
        raise RemotePhysTrainingError(
            "TrainingOutputSpec locators must be unique.",
            owner="TrainingOutputSpec",
            locators=sorted(duplicates),
        )


TrainingPlan.__hash__ = None  # type: ignore[assignment]
