from __future__ import annotations

from dataclasses import dataclass

from rphys.data import FieldValue
from rphys.losses import LossResult, LossTerm
from rphys.objectives import (
    ObjectiveContext,
    ObjectiveContract,
    ObjectiveResult,
    ObjectiveTerm,
    ObjectiveTermSpec,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class SyntheticObjective:
    contract = ObjectiveContract(
        "synthetic-objective-contract",
        (ObjectiveTermSpec("loss", source="loss:contract", weight=1.0),),
        writes=("objectives/custom.stage11.contract_total",),
    )

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        component = ObjectiveTerm.from_loss_term(context.loss_results[0].primary, name="loss")
        total = ObjectiveTerm(
            "total",
            FakeScalar(component.value.value),
            backend=component.backend,
            source_terms=(component.name,),
            gradient_path=component.gradient_path,
        )
        return ObjectiveResult(
            total=total,
            terms=(component,),
            fields={"objectives/custom.stage11.contract_total": FieldValue(total.value)},
            contract=context.contract,
        )


def test_fake_objective_aggregates_public_loss_result_and_exposes_total() -> None:
    loss_result = LossResult(
        (
            LossTerm(
                "contract-loss",
                FakeScalar(0.2),
                backend="fake",
                reduction="mean",
                gradient_path="prediction->loss",
            ),
        )
    )
    objective = SyntheticObjective()

    result = objective(ObjectiveContext(objective.contract, loss_results=(loss_result,)))

    assert result.total.name == "total"
    assert result.total.value == FakeScalar(0.2)
    assert result.terms[0].source_terms == ("contract-loss",)
    assert tuple(str(locator) for locator in result.fields) == (
        "objectives/custom.stage11.contract_total",
    )
