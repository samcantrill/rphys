"""Objective term and result records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import InvalidObjectiveResultError
from rphys.losses import LossTerm

from ._validation import (
    coerce_fields_patch,
    coerce_non_empty_string,
    coerce_optional_non_empty_string,
    coerce_reduction,
    coerce_string_mapping,
    coerce_weight,
)
from .specs import ObjectiveContract

__all__ = ["ObjectiveResult", "ObjectiveTerm"]


@dataclass(frozen=True, init=False, slots=True)
class ObjectiveTerm:
    """One optimizer-relevant scalar handle plus aggregation metadata."""

    name: str
    value: object
    backend: str
    weight: float
    reduction: str
    differentiable: bool
    source_terms: tuple[str, ...]
    gradient_path: str | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        value: object,
        *,
        backend: str,
        weight: float = 1.0,
        reduction: str = "weighted_sum",
        differentiable: bool = True,
        source_terms: Iterable[str] = (),
        gradient_path: str | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="ObjectiveTerm",
                field="name",
                error_type=InvalidObjectiveResultError,
            ),
        )
        if value is None:
            raise InvalidObjectiveResultError(
                "ObjectiveTerm value must preserve a backend-native handle.",
                owner="ObjectiveTerm",
                field="value",
                expected="backend-native handle",
                actual="None",
            )
        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "backend",
            coerce_non_empty_string(
                backend,
                owner="ObjectiveTerm",
                field="backend",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "weight",
            coerce_weight(
                weight,
                owner="ObjectiveTerm",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "reduction",
            coerce_reduction(
                reduction,
                owner="ObjectiveTerm",
                error_type=InvalidObjectiveResultError,
            ),
        )
        if not isinstance(differentiable, bool):
            raise InvalidObjectiveResultError(
                "ObjectiveTerm differentiable must be a boolean.",
                owner="ObjectiveTerm",
                field="differentiable",
                expected="bool",
                actual=type(differentiable).__name__,
            )
        object.__setattr__(self, "differentiable", differentiable)
        object.__setattr__(self, "source_terms", _coerce_source_terms(source_terms))
        object.__setattr__(
            self,
            "gradient_path",
            coerce_optional_non_empty_string(
                gradient_path,
                owner="ObjectiveTerm",
                field="gradient_path",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="ObjectiveTerm",
                field="metadata",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(
                diagnostics,
                owner="ObjectiveTerm",
                field="diagnostics",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="ObjectiveTerm",
                field="provenance",
                error_type=InvalidObjectiveResultError,
            ),
        )

    @classmethod
    def from_loss_term(
        cls,
        loss_term: LossTerm,
        *,
        name: str | None = None,
        weight: float = 1.0,
    ) -> "ObjectiveTerm":
        """Create an objective component from a public ``LossTerm`` record."""

        if not isinstance(loss_term, LossTerm):
            raise InvalidObjectiveResultError(
                "ObjectiveTerm.from_loss_term requires a LossTerm.",
                owner="ObjectiveTerm",
                field="loss_term",
                expected="LossTerm",
                actual=type(loss_term).__name__,
            )
        return cls(
            loss_term.name if name is None else name,
            loss_term.value,
            backend=loss_term.backend,
            weight=weight,
            reduction=loss_term.reduction,
            differentiable=loss_term.differentiable,
            source_terms=(loss_term.name,),
            gradient_path=loss_term.gradient_path,
            metadata={"unit": loss_term.unit} if loss_term.unit is not None else None,
            diagnostics=loss_term.diagnostics,
            provenance=loss_term.provenance,
        )


@dataclass(frozen=True, init=False, slots=True)
class ObjectiveResult:
    """Optimizer-facing objective result with a required ``total`` handle."""

    total: ObjectiveTerm
    terms: tuple[ObjectiveTerm, ...]
    fields: Mapping[FieldLocator, FieldValue]
    contract: ObjectiveContract | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        *,
        total: ObjectiveTerm,
        terms: Iterable[ObjectiveTerm] = (),
        fields: Mapping[FieldLocator | str, FieldValue] | None = None,
        contract: ObjectiveContract | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if not isinstance(total, ObjectiveTerm):
            raise InvalidObjectiveResultError(
                "ObjectiveResult total must be an ObjectiveTerm.",
                owner="ObjectiveResult",
                field="total",
                expected="ObjectiveTerm",
                actual=type(total).__name__,
            )
        if contract is not None and not isinstance(contract, ObjectiveContract):
            raise InvalidObjectiveResultError(
                "ObjectiveResult contract must be an ObjectiveContract when provided.",
                owner="ObjectiveResult",
                field="contract",
                expected="ObjectiveContract | None",
                actual=type(contract).__name__,
            )
        terms_tuple = _coerce_terms(terms)
        if fields and contract is None:
            raise InvalidObjectiveResultError(
                "ObjectiveResult fields patches require a contract with declared writes.",
                owner="ObjectiveResult",
                field="fields",
            )
        object.__setattr__(self, "total", total)
        object.__setattr__(self, "terms", terms_tuple)
        object.__setattr__(
            self,
            "fields",
            coerce_fields_patch(
                fields,
                declared_writes=() if contract is None else contract.writes,
                owner="ObjectiveResult",
            ),
        )
        object.__setattr__(self, "contract", contract)
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="ObjectiveResult",
                field="metadata",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(
                diagnostics,
                owner="ObjectiveResult",
                field="diagnostics",
                error_type=InvalidObjectiveResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="ObjectiveResult",
                field="provenance",
                error_type=InvalidObjectiveResultError,
            ),
        )


def _coerce_source_terms(values: Iterable[str]) -> tuple[str, ...]:
    try:
        terms = tuple(
            coerce_non_empty_string(
                value,
                owner="ObjectiveTerm",
                field="source_terms",
                error_type=InvalidObjectiveResultError,
            )
            for value in values
        )
    except TypeError as exc:
        raise InvalidObjectiveResultError(
            "ObjectiveTerm source_terms must be iterable.",
            owner="ObjectiveTerm",
            field="source_terms",
            expected="iterable of strings",
            actual=type(values).__name__,
        ) from exc
    return terms


def _coerce_terms(values: Iterable[ObjectiveTerm]) -> tuple[ObjectiveTerm, ...]:
    try:
        terms = tuple(values)
    except TypeError as exc:
        raise InvalidObjectiveResultError(
            "ObjectiveResult terms must be iterable.",
            owner="ObjectiveResult",
            field="terms",
            expected="iterable of ObjectiveTerm",
            actual=type(values).__name__,
        ) from exc
    for index, term in enumerate(terms):
        if not isinstance(term, ObjectiveTerm):
            raise InvalidObjectiveResultError(
                "ObjectiveResult terms must contain ObjectiveTerm records.",
                owner="ObjectiveResult",
                field="terms",
                index=index,
                actual=type(term).__name__,
            )
    names = [term.name for term in terms]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise InvalidObjectiveResultError(
            "ObjectiveResult terms must not repeat names.",
            owner="ObjectiveResult",
            field="terms",
            duplicates=tuple(duplicates),
        )
    return terms


ObjectiveTerm.__hash__ = None  # type: ignore[assignment]
ObjectiveResult.__hash__ = None  # type: ignore[assignment]
