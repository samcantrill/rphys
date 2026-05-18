from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    CheckpointCatalog,
    CheckpointMetricDirection,
    CheckpointPruneEvidence,
    CheckpointPruneResult,
    CheckpointPrunePolicy,
    CheckpointRef,
    CheckpointRefStatus,
    CheckpointRetentionReason,
    CheckpointRestoreMode,
    CheckpointRestorePolicy,
    CheckpointRestoreResult,
    CheckpointResultStatus,
    CheckpointSavePolicy,
    CheckpointSaveResult,
    CheckpointSelection,
    CheckpointSelectionMode,
    CheckpointSelectionResult,
)


def _refs() -> tuple[CheckpointRef, ...]:
    return (
        CheckpointRef(
            "ckpt-a",
            stream_id="stream-a",
            status="completed",
            epoch=1,
            step=10,
            timestamp=1.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=0.8,
        ),
        CheckpointRef(
            "ckpt-b",
            stream_id="stream-a",
            status="completed",
            epoch=2,
            step=20,
            timestamp=2.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=0.5,
        ),
        CheckpointRef(
            "ckpt-c",
            stream_id="stream-a",
            status="completed",
            epoch=3,
            step=30,
            timestamp=3.0,
            metric_name="loss",
            metric_direction="min",
            metric_value=0.9,
        ),
        CheckpointRef(
            "ckpt-d",
            stream_id="stream-a",
            status="failed",
            epoch=4,
            step=40,
            timestamp=4.0,
            is_failure=True,
        ),
        CheckpointRef(
            "ckpt-final",
            stream_id="stream-a",
            status="completed",
            epoch=5,
            step=50,
            timestamp=5.0,
            is_final=True,
            metric_name="val_loss",
            metric_direction="max",
            metric_value=0.4,
            global_rank=1,
            provenance={"created_by": "unit"},
        ),
    )


def test_checkpoint_ref_validates_primitive_fields_and_serialization() -> None:
    ref = CheckpointRef(
        "ckpt-1",
        stream_id="stream-1",
        run_id="run-1",
        epoch=10,
        step=100,
        timestamp=12.5,
        path="/tmp/ckpt.pt",
        is_final=True,
        metric_name="loss",
        metric_direction="min",
        metric_value=0.123,
        process_id=17,
        node_id="node-a",
        local_rank=0,
        global_rank=2,
        device_id="cuda:0",
        metadata={"creator": "unit"},
        provenance={"adapter": "unit"},
    )

    assert ref.ref_id == "ckpt-1"
    assert ref.metric_direction is not None
    assert ref.metric_direction.value == "min"
    assert ref.status is CheckpointRefStatus.PENDING
    inspected = asdict(ref)
    assert inspected["metadata"] == {"creator": "unit"}
    assert inspected["provenance"] == {"adapter": "unit"}
    assert inspected["global_rank"] == 2
    assert inspected["device_id"] == "cuda:0"

    with pytest.raises(RemotePhysTrainingError) as invalid_status:
        CheckpointRef("bad", status="bad")  # type: ignore[arg-type]
    assert invalid_status.value.context["field"] == "status"


def test_checkpoint_save_policy_requires_consistent_triggers() -> None:
    with pytest.raises(RemotePhysTrainingError) as metric_name_error:
        CheckpointSavePolicy(on_metric=True)
    assert metric_name_error.value.context["field"] == "metric_name"

    with pytest.raises(RemotePhysTrainingError) as direction_error:
        CheckpointSavePolicy(on_metric=True, metric_name="loss")
    assert direction_error.value.context["field"] == "metric_direction"

    disabled = CheckpointSavePolicy(enabled=False)
    assert disabled.enabled is False
    assert disabled.on_final is False

    with pytest.raises(RemotePhysTrainingError) as disabled_trigger_error:
        CheckpointSavePolicy(enabled=False, on_final=True)
    assert disabled_trigger_error.value.context["field"] == "enabled"

    with pytest.raises(RemotePhysTrainingError) as disabled_metric_error:
        CheckpointSavePolicy(enabled=False, on_final=False, metric_name="loss")
    assert disabled_metric_error.value.context["field"] == "enabled"

    policy = CheckpointSavePolicy(
        enabled=True,
        by_step=10,
        on_metric=True,
        metric_name="loss",
        metric_direction="max",
        on_failure=True,
        on_final=True,
    )
    assert policy.by_step == 10
    assert policy.on_metric is True
    assert policy.metric_direction.value == "max"


def test_checkpoint_prune_policy_validates_required_fields() -> None:
    with pytest.raises(RemotePhysTrainingError) as best_requires_name:
        CheckpointPrunePolicy(keep_best=2)
    assert best_requires_name.value.context["field"] == "best_metric_name"

    with pytest.raises(RemotePhysTrainingError) as best_requires_direction:
        CheckpointPrunePolicy(keep_best=2, best_metric_name="loss")
    assert best_requires_direction.value.context["field"] == "best_metric_direction"

    with pytest.raises(RemotePhysTrainingError) as keep_rule_error:
        CheckpointPrunePolicy(enabled=False, keep_recent=1)
    assert keep_rule_error.value.context["field"] == "enabled"

    disabled = CheckpointPrunePolicy(enabled=False)
    assert disabled.enabled is False
    assert disabled.keep_final is False
    assert disabled.keep_failure is False

    with pytest.raises(RemotePhysTrainingError) as disabled_keep_error:
        CheckpointPrunePolicy(enabled=False, keep_failure=True)
    assert disabled_keep_error.value.context["field"] == "enabled"

    policy = CheckpointPrunePolicy(keep_recent=2, keep_failure=True, keep_final=True)
    assert policy.keep_recent == 2
    assert policy.best_metric_name is None


def test_checkpoint_selection_result_and_modes_are_deterministic() -> None:
    catalog = CheckpointCatalog(_refs())

    latest = catalog.select(CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED))
    assert latest.status is CheckpointResultStatus.COMPLETED
    assert latest.ref is not None
    assert latest.ref.ref_id == "ckpt-final"
    assert asdict(latest)["ref"]["global_rank"] == 1
    assert asdict(latest)["ref"]["provenance"] == {"created_by": "unit"}

    best_min = catalog.select(
        CheckpointSelection(
            CheckpointSelectionMode.BEST_BY_METRIC,
            metric_name="loss",
            metric_direction="min",
        ),
    )
    assert best_min.status is CheckpointResultStatus.COMPLETED
    assert best_min.ref is not None
    assert best_min.ref.ref_id == "ckpt-b"

    steps_back = catalog.select(CheckpointSelection(CheckpointSelectionMode.N_STEPS_BACK, step_back=25))
    assert steps_back.status is CheckpointResultStatus.COMPLETED
    assert steps_back.ref is not None
    assert steps_back.ref.ref_id == "ckpt-b"

    before = catalog.select(
        CheckpointSelection(
            CheckpointSelectionMode.BEFORE_TIMESTAMP,
            timestamp=3.0,
            inclusive_timestamp=False,
        ),
    )
    assert before.ref is not None
    assert before.ref.timestamp == 2.0

    no_match = catalog.select(
        CheckpointSelection(
            CheckpointSelectionMode.EXPLICIT,
            explicit_ref_id="missing",
        ),
    )
    assert no_match.status is CheckpointResultStatus.UNAVAILABLE
    assert no_match.ref is None

    with pytest.raises(RemotePhysTrainingError) as completed_without_ref:
        CheckpointSelectionResult(
            selection=CheckpointSelection(CheckpointSelectionMode.LATEST_COMPLETED),
            status=CheckpointResultStatus.COMPLETED,
        )
    assert completed_without_ref.value.context["field"] == "status"


def test_checkpoint_rewind_selectors_prioritize_requested_dimension() -> None:
    catalog = CheckpointCatalog(
        (
            CheckpointRef("step-1", status="completed", epoch=1, step=1, timestamp=100.0),
            CheckpointRef("step-8", status="completed", epoch=8, step=8, timestamp=1.0),
            CheckpointRef("step-10", status="completed", epoch=10, step=10, timestamp=10.0),
        ),
    )

    steps_back = catalog.select(CheckpointSelection(CheckpointSelectionMode.N_STEPS_BACK, step_back=2))
    assert steps_back.ref is not None
    assert steps_back.ref.ref_id == "step-8"

    epochs_back = catalog.select(CheckpointSelection(CheckpointSelectionMode.N_EPOCHS_BACK, epoch_back=2))
    assert epochs_back.ref is not None
    assert epochs_back.ref.ref_id == "step-8"


def test_checkpoint_selection_validation_errors() -> None:
    with pytest.raises(RemotePhysTrainingError):
        CheckpointSelection(CheckpointSelectionMode.N_STEPS_BACK)
    with pytest.raises(RemotePhysTrainingError):
        CheckpointSelection(CheckpointSelectionMode.EXPLICIT)
    with pytest.raises(RemotePhysTrainingError):
        CheckpointSelection(CheckpointSelectionMode.EXPLICIT, explicit_ref_id="")


def test_checkpoint_restore_and_result_records_are_lightweight() -> None:
    restore = CheckpointRestorePolicy(
        mode="catalog",
        selector="best_by_metric",
        preferred_stream_id="stream-a",
    )
    assert restore.mode is CheckpointRestoreMode.CATALOG
    assert restore.selector is CheckpointSelectionMode.BEST_BY_METRIC

    restore_result = CheckpointRestoreResult(
        status=CheckpointResultStatus.UNSUPPORTED,
        mode="catalog",
        run_id="run-1",
        timeline_id="timeline-1",
        process_id=7,
        node_id="node-a",
        local_rank=0,
        global_rank=2,
        device_id="cuda:0",
        metadata={"scope": "restore"},
        provenance={"adapter": "unit"},
    )
    assert restore_result.mode is CheckpointRestoreMode.CATALOG
    assert restore_result.status is CheckpointResultStatus.UNSUPPORTED
    assert restore_result.global_rank == 2
    assert asdict(restore_result)["provenance"] == {"adapter": "unit"}

    save_result = CheckpointSaveResult(
        status=CheckpointResultStatus.UNAVAILABLE,
        reason="disabled",
        run_id="run-1",
        timeline_id="timeline-1",
        process_id=7,
        node_id="node-a",
        local_rank=0,
        global_rank=2,
        device_id="cuda:0",
        metadata={"stream": "main"},
        provenance={"adapter": "unit"},
    )
    assert save_result.status is CheckpointResultStatus.UNAVAILABLE
    assert save_result.reason == "disabled"
    assert save_result.device_id == "cuda:0"
    assert asdict(save_result)["metadata"] == {"stream": "main"}

    with pytest.raises(RemotePhysTrainingError) as rank_error:
        CheckpointSaveResult(status="skipped", local_rank=-1)
    assert rank_error.value.context["field"] == "local_rank"

    with pytest.raises(RemotePhysTrainingError) as save_ref_error:
        CheckpointSaveResult(status=CheckpointResultStatus.COMPLETED)
    assert save_ref_error.value.context["field"] == "ref_id"

    with pytest.raises(RemotePhysTrainingError) as restore_ref_error:
        CheckpointRestoreResult(status=CheckpointResultStatus.COMPLETED, mode="catalog")
    assert restore_ref_error.value.context["field"] == "ref_id"


def test_checkpoint_prune_evidence_retains_reference_and_reason() -> None:
    first = _refs()[0]
    evidence = CheckpointPruneEvidence(first, CheckpointRetentionReason.DROP_AGE)
    assert evidence.ref is first
    assert evidence.reason is CheckpointRetentionReason.DROP_AGE

    with pytest.raises(RemotePhysTrainingError):
        CheckpointPruneEvidence(first, "bad")  # type: ignore[arg-type]

    policy = CheckpointPrunePolicy(
        keep_recent=1,
        keep_best=1,
        best_metric_name="val_loss",
        best_metric_direction=CheckpointMetricDirection.MIN,
        keep_final=True,
        keep_failure=True,
    )
    assert policy.keep_recent == 1
    assert policy.keep_failure is True
    assert asdict(policy) == {
        "enabled": True,
        "keep_recent": 1,
        "keep_best": 1,
        "best_metric_name": "val_loss",
        "best_metric_direction": CheckpointMetricDirection.MIN,
        "keep_final": True,
        "keep_failure": True,
    }


def test_checkpoint_prune_result_models_kept_and_dropped_evidence() -> None:
    kept = CheckpointRef("kept", status="completed", stream_id="s")
    dropped = CheckpointPruneEvidence(kept, CheckpointRetentionReason.RETAIN_FAILURE)
    result = CheckpointPruneResult(
        status=CheckpointResultStatus.COMPLETED,
        kept=(kept,),
        dropped=(dropped,),
        keep_count=1,
        run_id="run-1",
        timeline_id="timeline-1",
        process_id=7,
        node_id="node-a",
        local_rank=0,
        global_rank=2,
        device_id="cuda:0",
        metadata={"pruner": "unit"},
        provenance={"policy": "keep-one"},
    )

    assert result.status is CheckpointResultStatus.COMPLETED
    assert result.kept[0].ref_id == "kept"
    assert result.dropped[0].ref is kept
    assert result.keep_count == 1
    assert result.process_id == 7
    assert asdict(result)["metadata"] == {"pruner": "unit"}
