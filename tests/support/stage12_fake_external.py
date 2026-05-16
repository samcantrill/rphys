"""Test-only fake external engine pressure for Stage 12."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from rphys.errors import RemotePhysTrainingError
from rphys.learning import Learner
from rphys.training import (
    ProfileSummary,
    TrainingEventSummary,
    TrainingMetricSummary,
    TrainingPlan,
    TrainingResult,
)


@dataclass(frozen=True, slots=True)
class FakeExternalEvidence:
    metrics: Mapping[str, float] = field(default_factory=dict)
    checkpoint_id: str | None = None
    callback_statuses: Mapping[str, str] = field(default_factory=dict)
    profile_statuses: Mapping[str, str] = field(default_factory=dict)
    unavailable_probes: Mapping[str, str] = field(default_factory=dict)
    event_counts: Mapping[str, int] = field(default_factory=dict)


class FakeExternalEngine:
    """Fake adapter that maps primitive external-like evidence into results."""

    def __init__(self, evidence: FakeExternalEvidence) -> None:
        self.evidence = evidence
        self.calls: list[tuple[str, TrainingPlan, Learner]] = []

    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        self.calls.append(("fit", plan, learner))
        return self._result("train")

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        self.calls.append(("validate", plan, learner))
        return self._result("validate")

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        self.calls.append(("test", plan, learner))
        return self._result("test")

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        self.calls.append(("predict", plan, learner))
        return self._result("predict")

    def _result(self, mode: str) -> TrainingResult:
        return TrainingResult(
            status="completed",
            mode=mode,
            step_count=1,
            metrics=tuple(
                TrainingMetricSummary(name, value, provenance={"engine": "fake-external"})
                for name, value in self.evidence.metrics.items()
            ),
            events=tuple(
                TrainingEventSummary(name, status=status)
                for name, status in self.evidence.callback_statuses.items()
            )
            + tuple(
                TrainingEventSummary(name, count=count)
                for name, count in self.evidence.event_counts.items()
            ),
            profiles=tuple(
                ProfileSummary(name, status=status)
                for name, status in self.evidence.profile_statuses.items()
            )
            + tuple(
                ProfileSummary(name, status="unavailable", metadata={"reason": reason})
                for name, reason in self.evidence.unavailable_probes.items()
            ),
            checkpoint_id=self.evidence.checkpoint_id,
            provenance={"engine": "FakeExternalEngine"},
        )


class FakeModule:
    def __init__(self, name: str, *, children: tuple["FakeModule", ...] = ()) -> None:
        self.name = name
        self.children = children


class FakeMethod:
    def __init__(self, module: FakeModule | None) -> None:
        self.module = module


class FakeTrainableOwnerRegistry:
    """Adapter-local fake owner registry; not a public rphys helper."""

    def __init__(self) -> None:
        self._owners: set[int] = set()

    def register_method(self, method: FakeMethod) -> FakeModule:
        module = getattr(method, "module", None)
        if not isinstance(module, FakeModule):
            raise RemotePhysTrainingError(
                "Fake external adapter requires one FakeModule trainable owner.",
                owner="FakeTrainableOwnerRegistry",
                field="module",
                expected="FakeModule",
                actual=type(module).__name__,
            )
        for owner in _walk_modules(module):
            owner_id = id(owner)
            if owner_id in self._owners:
                raise RemotePhysTrainingError(
                    "Fake external adapter rejected duplicate trainable owner.",
                    owner="FakeTrainableOwnerRegistry",
                    field="module",
                    module=owner.name,
                )
            self._owners.add(owner_id)
        return module


def _walk_modules(module: FakeModule) -> tuple[FakeModule, ...]:
    nested = [module]
    for child in module.children:
        nested.extend(_walk_modules(child))
    return tuple(nested)
