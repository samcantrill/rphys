from __future__ import annotations

from dataclasses import dataclass

from rphys.data import FieldValue, Sample
from rphys.losses import (
    LossContext,
    LossContract,
    LossInputSpec,
    LossResult,
    LossTerm,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SyntheticLoss:
    contract = LossContract(
        "synthetic-contract-loss",
        (
            LossInputSpec("predictions/signal.pulse", role="prediction"),
            LossInputSpec("targets/signal.pulse", role="target"),
        ),
        writes=("losses/custom.stage11.synthetic_contract_loss",),
    )

    def __call__(self, context: LossContext) -> LossResult:
        return LossResult(
            (
                LossTerm(
                    "synthetic-contract-loss",
                    FakeScalar(0.1),
                    backend="fake",
                    reduction="mean",
                    differentiable=True,
                    gradient_path="fake-gradient-path",
                    diagnostics={"empty_mask": False},
                ),
            ),
            fields={"losses/custom.stage11.synthetic_contract_loss": FieldValue(FakeScalar(0.1))},
            contract=context.contract,
            provenance={"fixture": "contract"},
        )


def test_fake_loss_consumes_synthetic_field_container_and_returns_patch_only_result() -> None:
    sample = Sample(
        {
            "predictions/signal.pulse": FieldValue([1.0, 2.0]),
            "targets/signal.pulse": FieldValue([1.5, 2.5]),
        }
    )
    before = sample.field_items()
    loss = SyntheticLoss()

    result = loss(LossContext(loss.contract, sample))

    assert result.primary.value == FakeScalar(0.1)
    assert result.primary.backend == "fake"
    assert result.primary.differentiable is True
    assert tuple(str(locator) for locator in result.fields) == (
        "losses/custom.stage11.synthetic_contract_loss",
    )
    assert sample.field_items() == before
