"""Assembled-object training plan records."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from rphys.data import Batch
from rphys.errors import RemotePhysTrainingError
from rphys.learning import LoopMode

from .events import TrainingCallback, TrainingEventSink
from .profiling import TrainingProfiler
from ._validation import (
    PrimitiveMapping,
    coerce_optional_positive_int,
    coerce_positive_int,
    coerce_tuple,
    freeze_primitive_mapping,
)

__all__ = ["TrainingPlan"]

BatchIterable = Iterable[Batch]


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


TrainingPlan.__hash__ = None  # type: ignore[assignment]
