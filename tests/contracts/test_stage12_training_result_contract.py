from __future__ import annotations

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import TrainingMetricSummary, TrainingResult, TrainingStepSummary


def test_training_result_contract_is_primitive_summary_oriented() -> None:
    result = TrainingResult(
        status="completed",
        mode="test",
        step_count=2,
        batch_count=2,
        metrics=(TrainingMetricSummary("mae", 0.2, unit="bpm"),),
        last_step=TrainingStepSummary("test", step_index=1, batch_index=1, metrics={"mae": 0.2}),
        metadata={"scope": "contract"},
    )

    assert result.metrics["mae"].value == 0.2
    assert result.last_step is not None
    assert result.last_step.metrics == {"mae": 0.2}
    assert result.metadata == {"scope": "contract"}


def test_training_result_contract_rejects_raw_objects_in_summaries() -> None:
    with pytest.raises(RemotePhysTrainingError):
        TrainingMetricSummary("raw", object())  # type: ignore[arg-type]

    with pytest.raises(RemotePhysTrainingError):
        TrainingStepSummary("test", metrics={"raw": object()})
