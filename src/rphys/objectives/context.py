"""Objective execution context records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.errors import InvalidObjectiveContextError
from rphys.losses import LossResult

from ._validation import coerce_string_mapping
from .specs import ObjectiveContract

__all__ = ["ObjectiveContext"]


@dataclass(frozen=True, init=False, slots=True)
class ObjectiveContext:
    """Runtime inputs for objective aggregation."""

    contract: ObjectiveContract
    loss_results: tuple[LossResult, ...]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        contract: ObjectiveContract,
        *,
        loss_results: Iterable[LossResult] = (),
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(contract, ObjectiveContract):
            raise InvalidObjectiveContextError(
                "ObjectiveContext contract must be an ObjectiveContract.",
                owner="ObjectiveContext",
                field="contract",
                expected="ObjectiveContract",
                actual=type(contract).__name__,
            )
        object.__setattr__(self, "contract", contract)
        object.__setattr__(self, "loss_results", _coerce_loss_results(loss_results))
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="ObjectiveContext",
                field="metadata",
                error_type=InvalidObjectiveContextError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="ObjectiveContext",
                field="provenance",
                error_type=InvalidObjectiveContextError,
            ),
        )


def _coerce_loss_results(values: Iterable[LossResult]) -> tuple[LossResult, ...]:
    try:
        results = tuple(values)
    except TypeError as exc:
        raise InvalidObjectiveContextError(
            "ObjectiveContext loss_results must be iterable.",
            owner="ObjectiveContext",
            field="loss_results",
            expected="iterable of LossResult",
            actual=type(values).__name__,
        ) from exc
    for index, result in enumerate(results):
        if not isinstance(result, LossResult):
            raise InvalidObjectiveContextError(
                "ObjectiveContext loss_results must contain LossResult records.",
                owner="ObjectiveContext",
                field="loss_results",
                index=index,
                actual=type(result).__name__,
            )
    return results


ObjectiveContext.__hash__ = None  # type: ignore[assignment]
