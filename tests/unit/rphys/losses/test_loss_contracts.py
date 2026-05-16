from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.data import FieldValue, Sample
from rphys.errors import (
    InvalidLossContextError,
    InvalidLossResultError,
    InvalidLossSpecError,
)
from rphys.losses import (
    Loss,
    LossContext,
    LossContract,
    LossInputSpec,
    LossResult,
    LossTerm,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class FakeLoss:
    contract = LossContract(
        "synthetic-l1",
        (
            LossInputSpec(
                "predictions/signal.pulse",
                role="prediction",
                expected_metadata={"unit": "bpm"},
            ),
            LossInputSpec(
                "targets/signal.pulse",
                role="target",
                expected_metadata={"unit": "bpm"},
            ),
        ),
        writes=("losses/custom.stage11.synthetic_l1",),
        reductions=("mean",),
    )

    def __call__(self, context: LossContext) -> LossResult:
        return LossResult(
            (
                LossTerm(
                    "synthetic-l1",
                    FakeScalar(0.5),
                    backend="fake",
                    reduction="mean",
                    differentiable=True,
                    gradient_path="prediction->loss",
                    unit="bpm",
                ),
            ),
            fields={"losses/custom.stage11.synthetic_l1": FieldValue(FakeScalar(0.5))},
            contract=context.contract,
            metadata={"example": "patch"},
        )


def _sample() -> Sample:
    return Sample(
        {
            "predictions/signal.pulse": FieldValue(70.0, metadata={"unit": "bpm"}),
            "targets/signal.pulse": FieldValue(72.0, metadata={"unit": "bpm"}),
            "inputs/mask.valid": FieldValue([True, True]),
        }
    )


def test_loss_input_spec_normalizes_locators_and_metadata() -> None:
    spec = LossInputSpec(
        "predictions/signal.pulse",
        role="prediction",
        expected_metadata={"unit": "bpm"},
    )

    assert str(spec.locator) == "predictions/signal.pulse"
    assert spec.role == "prediction"
    assert spec.required is True
    assert spec.missing_policy == "error"
    assert spec.expected_metadata == {"unit": "bpm"}
    with pytest.raises(TypeError):
        spec.expected_metadata["unit"] = "hz"  # type: ignore[index]


def test_loss_input_spec_rejects_invalid_missing_policy_for_required_field() -> None:
    with pytest.raises(InvalidLossSpecError):
        LossInputSpec("predictions/signal.pulse", role="prediction", missing_policy="allow")


def test_loss_contract_validates_duplicates_and_reductions() -> None:
    prediction = LossInputSpec("predictions/signal.pulse", role="prediction")

    with pytest.raises(InvalidLossSpecError):
        LossContract("duplicate", (prediction, prediction))
    with pytest.raises(InvalidLossSpecError):
        LossContract("bad-reduction", (prediction,), reductions=("median",))
    with pytest.raises(InvalidLossSpecError):
        LossContract("duplicate-writes", (prediction,), writes=("losses/custom.stage11.a", "losses/custom.stage11.a"))


def test_loss_context_validates_required_fields_metadata_and_masks() -> None:
    contract = LossContract(
        "with-mask",
        (
            LossInputSpec("predictions/signal.pulse", role="prediction", expected_metadata={"unit": "bpm"}),
            LossInputSpec("inputs/mask.valid", role="mask"),
        ),
    )

    context = LossContext(contract, _sample(), metadata={"split": "train"})
    assert context.contract is contract
    assert context.metadata == {"split": "train"}

    missing = Sample({"predictions/signal.pulse": FieldValue(70.0, metadata={"unit": "bpm"})})
    with pytest.raises(InvalidLossContextError):
        LossContext(contract, missing)

    mismatch = Sample(
        {
            "predictions/signal.pulse": FieldValue(70.0, metadata={"unit": "hz"}),
            "inputs/mask.valid": FieldValue([True]),
        }
    )
    with pytest.raises(InvalidLossContextError):
        LossContext(contract, mismatch)

    empty_mask = Sample(
        {
            "predictions/signal.pulse": FieldValue(70.0, metadata={"unit": "bpm"}),
            "inputs/mask.valid": FieldValue([]),
        }
    )
    with pytest.raises(InvalidLossContextError):
        LossContext(contract, empty_mask)


def test_loss_term_preserves_raw_handle_and_backend_metadata() -> None:
    handle = FakeScalar(1.25)
    term = LossTerm(
        "pulse-mae",
        handle,
        backend="fake",
        reduction="mean",
        differentiable=True,
        gradient_path="predictions/signal.pulse",
        unit="bpm",
        diagnostics={"flat_signal": False},
        provenance={"loss": "synthetic"},
    )

    assert term.value is handle
    assert term.backend == "fake"
    assert term.differentiable is True
    assert term.gradient_path == "predictions/signal.pulse"
    assert term.diagnostics == {"flat_signal": False}

    with pytest.raises(InvalidLossResultError):
        LossTerm("none", None, backend="fake")
    with pytest.raises(InvalidLossResultError):
        LossTerm("bad", handle, backend="fake", reduction="median")
    with pytest.raises(InvalidLossResultError):
        LossTerm("bad", handle, backend="fake", differentiable="yes")  # type: ignore[arg-type]


def test_loss_result_validates_terms_and_declared_patch_fields() -> None:
    contract = FakeLoss.contract
    term = LossTerm("synthetic-l1", FakeScalar(0.5), backend="fake")
    patch = FieldValue(FakeScalar(0.5), metadata={"unit": "loss"})

    result = LossResult(
        (term,),
        fields={"losses/custom.stage11.synthetic_l1": patch},
        contract=contract,
        metadata={"stage": 11},
    )

    assert result.primary is term
    assert result.fields[next(iter(result.fields))] is patch
    assert result.metadata == {"stage": 11}
    with pytest.raises(TypeError):
        result.fields["losses/other"] = patch  # type: ignore[index]

    with pytest.raises(InvalidLossResultError):
        LossResult((term,), fields={"losses/custom.stage11.synthetic_l1": patch})
    with pytest.raises(InvalidLossResultError):
        LossResult((term,), fields={"losses/custom.stage11.undeclared": patch}, contract=contract)
    with pytest.raises(InvalidLossResultError):
        LossResult((term, LossTerm("synthetic-l1", FakeScalar(1.0), backend="fake")))


def test_fake_loss_satisfies_protocol_and_does_not_mutate_context_fields() -> None:
    loss = FakeLoss()
    sample = _sample()
    before = sample.field_items()
    context = LossContext(loss.contract, sample)

    assert isinstance(loss, Loss)
    result = loss(context)

    assert isinstance(result, LossResult)
    assert result.primary.name == "synthetic-l1"
    assert str(next(iter(result.fields))) == "losses/custom.stage11.synthetic_l1"
    assert sample.field_items() == before
