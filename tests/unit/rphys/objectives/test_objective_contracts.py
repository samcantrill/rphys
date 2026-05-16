from __future__ import annotations

from dataclasses import dataclass

import pytest

from rphys.data import FieldValue
from rphys.errors import (
    InvalidObjectiveContextError,
    InvalidObjectiveResultError,
    InvalidObjectiveSpecError,
)
from rphys.losses import LossResult, LossTerm
from rphys.objectives import (
    Objective,
    ObjectiveContext,
    ObjectiveContract,
    ObjectiveResult,
    ObjectiveTerm,
    ObjectiveTermSpec,
)


@dataclass(frozen=True, slots=True)
class FakeScalar:
    value: float


class FakeObjective:
    contract = ObjectiveContract(
        "synthetic-objective",
        (ObjectiveTermSpec("loss", source="loss:synthetic-l1", weight=1.0),),
        writes=("objectives/custom.stage11.synthetic_total",),
    )

    def __call__(self, context: ObjectiveContext) -> ObjectiveResult:
        component = ObjectiveTerm.from_loss_term(
            context.loss_results[0].primary,
            name="loss",
        )
        total = ObjectiveTerm(
            "total",
            FakeScalar(component.value.value),
            backend="fake",
            source_terms=(component.name,),
            gradient_path=component.gradient_path,
        )
        return ObjectiveResult(
            total=total,
            terms=(component,),
            fields={"objectives/custom.stage11.synthetic_total": FieldValue(total.value)},
            contract=context.contract,
        )


def _loss_result() -> LossResult:
    term = LossTerm(
        "synthetic-l1",
        FakeScalar(0.5),
        backend="fake",
        reduction="mean",
        differentiable=True,
        gradient_path="prediction->loss",
        unit="bpm",
    )
    return LossResult((term,))


def test_objective_term_spec_validates_weight_reduction_and_schedule() -> None:
    spec = ObjectiveTermSpec(
        "loss",
        source="loss:synthetic-l1",
        weight=0.25,
        reduction="weighted_sum",
        schedule={"kind": "constant"},
    )

    assert spec.weight == 0.25
    assert spec.schedule == {"kind": "constant"}
    with pytest.raises(TypeError):
        spec.schedule["kind"] = "linear"  # type: ignore[index]

    with pytest.raises(InvalidObjectiveSpecError):
        ObjectiveTermSpec("loss", source="loss", weight=-1.0)
    with pytest.raises(InvalidObjectiveSpecError):
        ObjectiveTermSpec("loss", source="loss", reduction="median")


def test_objective_contract_validates_terms_and_declared_writes() -> None:
    spec = ObjectiveTermSpec("loss", source="loss:synthetic-l1")

    contract = ObjectiveContract(
        "objective",
        (spec,),
        writes=("objectives/custom.stage11.total",),
        metadata={"optimizer_target": True},
    )

    assert contract.terms == (spec,)
    assert str(contract.writes[0]) == "objectives/custom.stage11.total"
    assert contract.metadata == {"optimizer_target": True}

    with pytest.raises(InvalidObjectiveSpecError):
        ObjectiveContract("duplicate", (spec, spec))
    with pytest.raises(InvalidObjectiveSpecError):
        ObjectiveContract(
            "duplicate-writes",
            (spec,),
            writes=(
                "objectives/custom.stage11.total",
                "objectives/custom.stage11.total",
            ),
        )


def test_objective_context_accepts_public_loss_results_only() -> None:
    contract = FakeObjective.contract
    loss_result = _loss_result()

    context = ObjectiveContext(contract, loss_results=(loss_result,), metadata={"split": "train"})

    assert context.contract is contract
    assert context.loss_results == (loss_result,)
    assert context.metadata == {"split": "train"}

    with pytest.raises(InvalidObjectiveContextError):
        ObjectiveContext(contract, loss_results=(object(),))  # type: ignore[arg-type]


def test_objective_term_preserves_handles_and_can_reference_loss_terms() -> None:
    loss_term = _loss_result().primary

    component = ObjectiveTerm.from_loss_term(loss_term, name="weighted-loss", weight=2.0)

    assert component.value is loss_term.value
    assert component.backend == "fake"
    assert component.weight == 2.0
    assert component.source_terms == ("synthetic-l1",)
    assert component.gradient_path == "prediction->loss"

    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveTerm("bad", None, backend="fake")
    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveTerm("bad", FakeScalar(1.0), backend="fake", weight=-1.0)
    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveTerm("bad", FakeScalar(1.0), backend="fake", differentiable="yes")  # type: ignore[arg-type]


def test_objective_result_requires_total_and_validates_patch_fields() -> None:
    contract = FakeObjective.contract
    component = ObjectiveTerm("loss", FakeScalar(0.5), backend="fake")
    total = ObjectiveTerm("total", FakeScalar(0.5), backend="fake", source_terms=("loss",))
    patch = FieldValue(total.value)

    result = ObjectiveResult(
        total=total,
        terms=(component,),
        fields={"objectives/custom.stage11.synthetic_total": patch},
        contract=contract,
        metadata={"aggregation": "weighted_sum"},
    )

    assert result.total is total
    assert result.terms == (component,)
    assert result.fields[next(iter(result.fields))] is patch
    with pytest.raises(TypeError):
        result.fields["objectives/custom.stage11.other"] = patch  # type: ignore[index]

    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveResult(total=total, fields={"objectives/custom.stage11.synthetic_total": patch})
    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveResult(
            total=total,
            fields={"objectives/custom.stage11.undeclared": patch},
            contract=contract,
        )
    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveResult(total=object())  # type: ignore[arg-type]
    with pytest.raises(InvalidObjectiveResultError):
        ObjectiveResult(total=total, terms=(component, component))


def test_fake_objective_satisfies_protocol_and_exposes_total() -> None:
    objective = FakeObjective()
    context = ObjectiveContext(objective.contract, loss_results=(_loss_result(),))

    assert isinstance(objective, Objective)
    result = objective(context)

    assert isinstance(result, ObjectiveResult)
    assert result.total.name == "total"
    assert result.total.value == FakeScalar(0.5)
    assert tuple(str(locator) for locator in result.fields) == (
        "objectives/custom.stage11.synthetic_total",
    )
