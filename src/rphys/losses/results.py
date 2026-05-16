"""Loss term and result records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data import FieldValue
from rphys.data.locators import FieldLocator
from rphys.errors import InvalidLossResultError

from ._validation import (
    coerce_fields_patch,
    coerce_non_empty_string,
    coerce_optional_non_empty_string,
    coerce_reduction,
    coerce_string_mapping,
)
from .specs import LossContract

__all__ = ["LossResult", "LossTerm"]


@dataclass(frozen=True, init=False, slots=True)
class LossTerm:
    """One backend-native differentiable loss handle plus metadata."""

    name: str
    value: object
    backend: str
    reduction: str
    differentiable: bool
    gradient_path: str | None
    unit: str | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        value: object,
        *,
        backend: str,
        reduction: str = "mean",
        differentiable: bool = True,
        gradient_path: str | None = None,
        unit: str | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="LossTerm",
                field="name",
                error_type=InvalidLossResultError,
            ),
        )
        if value is None:
            raise InvalidLossResultError(
                "LossTerm value must preserve a backend-native handle.",
                owner="LossTerm",
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
                owner="LossTerm",
                field="backend",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "reduction",
            coerce_reduction(
                reduction,
                owner="LossTerm",
                error_type=InvalidLossResultError,
            ),
        )
        if not isinstance(differentiable, bool):
            raise InvalidLossResultError(
                "LossTerm differentiable must be a boolean.",
                owner="LossTerm",
                field="differentiable",
                expected="bool",
                actual=type(differentiable).__name__,
            )
        object.__setattr__(self, "differentiable", differentiable)
        object.__setattr__(
            self,
            "gradient_path",
            coerce_optional_non_empty_string(
                gradient_path,
                owner="LossTerm",
                field="gradient_path",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "unit",
            coerce_optional_non_empty_string(
                unit,
                owner="LossTerm",
                field="unit",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="LossTerm",
                field="metadata",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(
                diagnostics,
                owner="LossTerm",
                field="diagnostics",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="LossTerm",
                field="provenance",
                error_type=InvalidLossResultError,
            ),
        )


@dataclass(frozen=True, init=False, slots=True)
class LossResult:
    """Structured loss result with terms and immutable field patches."""

    terms: tuple[LossTerm, ...]
    fields: Mapping[FieldLocator, FieldValue]
    contract: LossContract | None
    metadata: Mapping[str, object]
    diagnostics: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        terms: Iterable[LossTerm],
        *,
        fields: Mapping[FieldLocator | str, FieldValue] | None = None,
        contract: LossContract | None = None,
        metadata: Mapping[object, object] | None = None,
        diagnostics: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        if contract is not None and not isinstance(contract, LossContract):
            raise InvalidLossResultError(
                "LossResult contract must be a LossContract when provided.",
                owner="LossResult",
                field="contract",
                expected="LossContract | None",
                actual=type(contract).__name__,
            )
        terms_tuple = _coerce_terms(terms)
        if fields and contract is None:
            raise InvalidLossResultError(
                "LossResult fields patches require a contract with declared writes.",
                owner="LossResult",
                field="fields",
            )
        object.__setattr__(self, "terms", terms_tuple)
        object.__setattr__(
            self,
            "fields",
            coerce_fields_patch(
                fields,
                declared_writes=() if contract is None else contract.writes,
                owner="LossResult",
            ),
        )
        object.__setattr__(self, "contract", contract)
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="LossResult",
                field="metadata",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "diagnostics",
            coerce_string_mapping(
                diagnostics,
                owner="LossResult",
                field="diagnostics",
                error_type=InvalidLossResultError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="LossResult",
                field="provenance",
                error_type=InvalidLossResultError,
            ),
        )

    @property
    def primary(self) -> LossTerm:
        """Return the first term as the conventional scalar logging target."""

        return self.terms[0]


def _coerce_terms(values: Iterable[LossTerm]) -> tuple[LossTerm, ...]:
    try:
        terms = tuple(values)
    except TypeError as exc:
        raise InvalidLossResultError(
            "LossResult terms must be iterable.",
            owner="LossResult",
            field="terms",
            expected="iterable of LossTerm",
            actual=type(values).__name__,
        ) from exc
    if not terms:
        raise InvalidLossResultError(
            "LossResult terms must not be empty.",
            owner="LossResult",
            field="terms",
        )
    for index, term in enumerate(terms):
        if not isinstance(term, LossTerm):
            raise InvalidLossResultError(
                "LossResult terms must contain LossTerm records.",
                owner="LossResult",
                field="terms",
                index=index,
                actual=type(term).__name__,
            )
    names = [term.name for term in terms]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise InvalidLossResultError(
            "LossResult terms must not repeat names.",
            owner="LossResult",
            field="terms",
            duplicates=tuple(duplicates),
        )
    return terms


LossTerm.__hash__ = None  # type: ignore[assignment]
LossResult.__hash__ = None  # type: ignore[assignment]
