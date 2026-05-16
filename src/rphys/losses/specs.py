"""Loss input and contract descriptors."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from rphys.data import FieldContainer
from rphys.data.locators import FieldLocator
from rphys.errors import InvalidLossContextError, InvalidLossSpecError

from ._validation import (
    coerce_locator,
    coerce_locator_tuple,
    coerce_missing_policy,
    coerce_non_empty_string,
    coerce_reduction,
    coerce_string_mapping,
    is_empty_mask_payload,
    metadata_has_expected,
)

__all__ = ["LossContract", "LossInputSpec"]


@dataclass(frozen=True, init=False, slots=True)
class LossInputSpec:
    """Declared field consumed by a loss.

    ``role`` is an inspectable loss-level role such as ``prediction``,
    ``target``, ``mask``, or ``weight``. ``locator`` is normalized to
    ``FieldLocator``. Contract validation checks presence, expected metadata,
    and empty mask payloads when the role is ``mask``.
    """

    locator: FieldLocator
    role: str
    required: bool
    missing_policy: str
    expected_metadata: Mapping[str, object]

    def __init__(
        self,
        locator: FieldLocator | str,
        *,
        role: str,
        required: bool = True,
        missing_policy: str = "error",
        expected_metadata: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "locator",
            coerce_locator(
                locator,
                owner="LossInputSpec",
                field="locator",
                error_type=InvalidLossSpecError,
            ),
        )
        object.__setattr__(
            self,
            "role",
            coerce_non_empty_string(
                role,
                owner="LossInputSpec",
                field="role",
                error_type=InvalidLossSpecError,
            ),
        )
        if not isinstance(required, bool):
            raise InvalidLossSpecError(
                "LossInputSpec required must be a boolean.",
                owner="LossInputSpec",
                field="required",
                expected="bool",
                actual=type(required).__name__,
            )
        object.__setattr__(self, "required", required)
        object.__setattr__(
            self,
            "missing_policy",
            coerce_missing_policy(
                missing_policy,
                owner="LossInputSpec",
                field="missing_policy",
            ),
        )
        object.__setattr__(
            self,
            "expected_metadata",
            coerce_string_mapping(
                expected_metadata,
                owner="LossInputSpec",
                field="expected_metadata",
                error_type=InvalidLossSpecError,
            ),
        )
        if required and self.missing_policy != "error":
            raise InvalidLossSpecError(
                "Required loss inputs must use the error missing policy.",
                owner="LossInputSpec",
                field="missing_policy",
                locator=str(self.locator),
            )


@dataclass(frozen=True, init=False, slots=True)
class LossContract:
    """Runtime field contract for a backend-neutral loss."""

    name: str
    inputs: tuple[LossInputSpec, ...]
    writes: tuple[FieldLocator, ...]
    reductions: tuple[str, ...]
    metadata: Mapping[str, object]
    provenance: Mapping[str, object]

    def __init__(
        self,
        name: str,
        inputs: Iterable[LossInputSpec],
        *,
        writes: Iterable[FieldLocator | str] | FieldLocator | str | None = None,
        reductions: Iterable[str] = ("mean",),
        metadata: Mapping[object, object] | None = None,
        provenance: Mapping[object, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "name",
            coerce_non_empty_string(
                name,
                owner="LossContract",
                field="name",
                error_type=InvalidLossSpecError,
            ),
        )
        object.__setattr__(
            self,
            "inputs",
            _coerce_inputs(inputs),
        )
        object.__setattr__(
            self,
            "writes",
            coerce_locator_tuple(
                writes,
                owner="LossContract",
                field="writes",
                error_type=InvalidLossSpecError,
            ),
        )
        object.__setattr__(
            self,
            "reductions",
            _coerce_reductions(reductions),
        )
        object.__setattr__(
            self,
            "metadata",
            coerce_string_mapping(
                metadata,
                owner="LossContract",
                field="metadata",
                error_type=InvalidLossSpecError,
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            coerce_string_mapping(
                provenance,
                owner="LossContract",
                field="provenance",
                error_type=InvalidLossSpecError,
            ),
        )

    def validate(self, container: FieldContainer) -> FieldContainer:
        """Validate required fields and metadata without mutating ``container``."""

        for input_spec in self.inputs:
            if not container.has(input_spec.locator):
                if input_spec.required or input_spec.missing_policy == "error":
                    raise InvalidLossContextError(
                        "Loss context is missing a required field.",
                        owner="LossContract",
                        field="inputs",
                        locator=str(input_spec.locator),
                        role=input_spec.role,
                    )
                continue
            field_value = container.field(input_spec.locator)
            missing_metadata = metadata_has_expected(
                field_value,
                input_spec.expected_metadata,
            )
            if missing_metadata:
                raise InvalidLossContextError(
                    "Loss input field metadata does not match the contract.",
                    owner="LossContract",
                    field="expected_metadata",
                    locator=str(input_spec.locator),
                    missing=missing_metadata,
                )
            if input_spec.role == "mask" and is_empty_mask_payload(field_value.payload):
                raise InvalidLossContextError(
                    "Loss mask inputs must not be empty.",
                    owner="LossContract",
                    field="inputs",
                    locator=str(input_spec.locator),
                    role=input_spec.role,
                )
        return container


def _coerce_inputs(values: Iterable[LossInputSpec]) -> tuple[LossInputSpec, ...]:
    try:
        inputs = tuple(values)
    except TypeError as exc:
        raise InvalidLossSpecError(
            "LossContract inputs must be iterable.",
            owner="LossContract",
            field="inputs",
            expected="iterable of LossInputSpec",
            actual=type(values).__name__,
        ) from exc
    if not inputs:
        raise InvalidLossSpecError(
            "LossContract inputs must not be empty.",
            owner="LossContract",
            field="inputs",
        )
    for index, input_spec in enumerate(inputs):
        if not isinstance(input_spec, LossInputSpec):
            raise InvalidLossSpecError(
                "LossContract inputs must contain LossInputSpec records.",
                owner="LossContract",
                field="inputs",
                index=index,
                actual=type(input_spec).__name__,
            )
    locators = [input_spec.locator for input_spec in inputs]
    duplicates = sorted({str(locator) for locator in locators if locators.count(locator) > 1})
    if duplicates:
        raise InvalidLossSpecError(
            "LossContract inputs must not repeat locators.",
            owner="LossContract",
            field="inputs",
            duplicates=tuple(duplicates),
        )
    return inputs


def _coerce_reductions(values: Iterable[str]) -> tuple[str, ...]:
    try:
        reductions = tuple(
            coerce_reduction(
                value,
                owner="LossContract",
                error_type=InvalidLossSpecError,
            )
            for value in values
        )
    except TypeError as exc:
        raise InvalidLossSpecError(
            "LossContract reductions must be iterable.",
            owner="LossContract",
            field="reductions",
            expected="iterable of strings",
            actual=type(values).__name__,
        ) from exc
    if not reductions:
        raise InvalidLossSpecError(
            "LossContract reductions must not be empty.",
            owner="LossContract",
            field="reductions",
        )
    duplicates = sorted({value for value in reductions if reductions.count(value) > 1})
    if duplicates:
        raise InvalidLossSpecError(
            "LossContract reductions must not contain duplicates.",
            owner="LossContract",
            field="reductions",
            duplicates=tuple(duplicates),
        )
    return reductions


LossInputSpec.__hash__ = None  # type: ignore[assignment]
LossContract.__hash__ = None  # type: ignore[assignment]
