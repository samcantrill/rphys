from __future__ import annotations

from dataclasses import asdict

import pytest

from rphys.errors import RemotePhysTrainingError
from rphys.training import (
    CheckpointRef,
    CheckpointRefStatus,
    ExperimentTierName,
    ExperimentTierSpec,
    RestartCompatibilityStatus,
    RestartState,
    default_experiment_tiers,
)


def test_default_experiment_tiers_are_descriptive_same_path_specs() -> None:
    tiers = default_experiment_tiers()

    assert tuple(tier.tier for tier in tiers) == (
        ExperimentTierName.DEBUG,
        ExperimentTierName.SMOKE,
        ExperimentTierName.SIGNAL,
        ExperimentTierName.COMPARISON,
        ExperimentTierName.FULL,
    )
    assert all(tier.same_execution_path for tier in tiers)
    assert all(tier.expected_evidence for tier in tiers)
    assert tiers[0].step_limit == 1
    assert tiers[-1].step_limit is None


def test_experiment_tier_spec_validates_scale_knobs_and_evidence() -> None:
    spec = ExperimentTierSpec(
        "smoke",
        sample_limit=8,
        epoch_limit=1,
        expected_evidence=("profile_spans", "checkpoint_refs"),
        loader_fingerprint="loader:v1",
        materialization_fingerprint="materialization:v1",
        metadata={"synthetic": True},
        provenance={"scope": "unit"},
    )

    inspected = asdict(spec)
    assert spec.tier is ExperimentTierName.SMOKE
    assert inspected["loader_fingerprint"] == "loader:v1"
    assert inspected["metadata"] == {"synthetic": True}

    with pytest.raises(RemotePhysTrainingError) as alternate_path:
        ExperimentTierSpec("debug", same_execution_path=False)
    assert alternate_path.value.context["field"] == "same_execution_path"

    with pytest.raises(RemotePhysTrainingError) as bad_limit:
        ExperimentTierSpec("debug", step_limit=0)
    assert bad_limit.value.context["field"] == "step_limit"

    with pytest.raises(RemotePhysTrainingError) as bad_evidence:
        ExperimentTierSpec("debug", expected_evidence=("events", ""))
    assert bad_evidence.value.context["field"] == "expected_evidence"

    with pytest.raises(RemotePhysTrainingError) as non_primitive:
        ExperimentTierSpec("debug", metadata={"bad": object()})
    assert non_primitive.value.context["field"] == "metadata"


def test_restart_state_links_checkpoint_profile_and_datapath_evidence() -> None:
    ref = CheckpointRef(
        "ckpt-10",
        run_id="run-a",
        timeline_id="timeline-a",
        status=CheckpointRefStatus.COMPLETED,
        epoch=2,
        step=10,
        path="/tmp/ckpt-10.pt",
    )

    state = RestartState(
        checkpoint_ref=ref,
        tier="signal",
        run_id="run-a",
        timeline_id="timeline-a",
        epoch=2,
        step=10,
        batch_index=4,
        loader_fingerprint="loader:fingerprint",
        materialization_fingerprint="materialized:fingerprint",
        data_path_fingerprint="data-path:fingerprint",
        profile_fingerprint="profile:fingerprint",
        profile_summary_id="profile-summary-a",
        checkpoint_fingerprint="checkpoint:fingerprint",
        completion_markers=("epoch:2", "step:10", "checkpoint:completed"),
        compatibility_status="compatible",
        compatibility_note="loader and materialization fingerprints match the checkpoint evidence",
        metadata={"resume": "latest"},
        provenance={"source": "unit"},
    )

    inspected = asdict(state)
    assert state.checkpoint_ref_id == "ckpt-10"
    assert state.tier is ExperimentTierName.SIGNAL
    assert state.compatibility_status is RestartCompatibilityStatus.COMPATIBLE
    assert inspected["checkpoint_ref"]["ref_id"] == "ckpt-10"
    assert inspected["data_path_fingerprint"] == "data-path:fingerprint"
    assert inspected["completion_markers"] == ("epoch:2", "step:10", "checkpoint:completed")


def test_restart_state_validates_required_restart_evidence() -> None:
    ref = CheckpointRef("ckpt-1", status="completed")

    with pytest.raises(RemotePhysTrainingError) as missing_checkpoint:
        RestartState(
            completion_markers=("step:1",),
            compatibility_status="ambiguous",
            compatibility_note="missing checkpoint reference",
        )
    assert missing_checkpoint.value.context["field"] == "checkpoint_ref_id"

    with pytest.raises(RemotePhysTrainingError) as mismatched_ref:
        RestartState(
            checkpoint_ref=ref,
            checkpoint_ref_id="other",
            completion_markers=("step:1",),
            compatibility_status="ambiguous",
            compatibility_note="mismatched checkpoint reference",
        )
    assert mismatched_ref.value.context["field"] == "checkpoint_ref_id"

    with pytest.raises(RemotePhysTrainingError) as missing_markers:
        RestartState(
            checkpoint_ref=ref,
            completion_markers=(),
            compatibility_status="ambiguous",
            compatibility_note="no completion marker",
        )
    assert missing_markers.value.context["field"] == "completion_markers"

    with pytest.raises(RemotePhysTrainingError) as missing_note:
        RestartState(
            checkpoint_ref=ref,
            completion_markers=("step:1",),
            compatibility_status="ambiguous",
        )
    assert missing_note.value.context["field"] == "compatibility_note"

    with pytest.raises(RemotePhysTrainingError) as bad_index:
        RestartState(
            checkpoint_ref=ref,
            batch_index=-1,
            completion_markers=("step:1",),
            compatibility_status="ambiguous",
            compatibility_note="invalid batch index",
        )
    assert bad_index.value.context["field"] == "batch_index"
