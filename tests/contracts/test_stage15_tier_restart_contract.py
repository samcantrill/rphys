from __future__ import annotations

from dataclasses import asdict, fields

from rphys.training import (
    CheckpointRef,
    ExperimentTierName,
    ExperimentTierSpec,
    RestartState,
    default_experiment_tiers,
)


def test_stage15_standard_tiers_cover_validation_breadths_without_scheduler_fields() -> None:
    tiers = default_experiment_tiers()
    forbidden_fields = {
        "artifact_store",
        "cost_dashboard",
        "executor",
        "job_runner",
        "queue",
        "retry_policy",
        "scheduler",
        "storage_backend",
        "workflow",
    }

    assert {tier.tier for tier in tiers} == set(ExperimentTierName)
    assert not forbidden_fields.intersection({field.name for field in fields(ExperimentTierSpec)})
    assert all(tier.same_execution_path for tier in tiers)


def test_stage15_restart_state_contract_is_checkpoint_and_evidence_linked() -> None:
    checkpoint = CheckpointRef(
        "ckpt-signal-20",
        run_id="run-signal",
        timeline_id="timeline-signal",
        status="completed",
        epoch=2,
        step=20,
        metadata={"stream": "main"},
        provenance={"engine": "native"},
    )

    state = RestartState(
        checkpoint_ref=checkpoint,
        tier=ExperimentTierName.SIGNAL,
        run_id="run-signal",
        timeline_id="timeline-signal",
        epoch=2,
        step=20,
        batch_index=5,
        loader_fingerprint="loader:synthetic:v1",
        materialization_fingerprint="materialized:none",
        data_path_fingerprint="data-path:stage9:v1",
        profile_fingerprint="profile:stage15:v1",
        profile_summary_id="summary:signal:20",
        checkpoint_fingerprint="checkpoint:signal:20",
        completion_markers=("epoch:2", "step:20", "checkpoint:completed"),
        compatibility_status="compatible",
        compatibility_note="checkpoint, loader, materialization, and profile evidence describe the same path",
        metadata={"selector": "latest_completed"},
        provenance={"scope": "contract"},
    )
    payload = asdict(state)

    assert payload["checkpoint_ref_id"] == "ckpt-signal-20"
    assert payload["checkpoint_ref"]["provenance"] == {"engine": "native"}
    assert payload["loader_fingerprint"] == "loader:synthetic:v1"
    assert payload["materialization_fingerprint"] == "materialized:none"
    assert payload["profile_summary_id"] == "summary:signal:20"
    assert payload["compatibility_status"] == "compatible"


def test_stage15_tier_and_restart_contracts_are_primitive_at_public_edges() -> None:
    tier = ExperimentTierSpec(
        "comparison",
        subject_limit=3,
        record_limit=3,
        expected_evidence=("profile_fingerprint", "restart_state"),
        profile_fingerprint="profile:comparison",
        metadata={"threshold_free": True},
        provenance={"stage": "15"},
    )
    restart = RestartState(
        checkpoint_ref_id="ckpt-comparison",
        tier=tier.tier,
        step=30,
        data_path_fingerprint="data-path:comparison",
        profile_fingerprint=tier.profile_fingerprint,
        completion_markers=("step:30", "profile:recorded"),
        compatibility_status="ambiguous",
        compatibility_note="checkpoint payload is external; fingerprint compatibility is recorded only as evidence",
    )

    tier_payload = asdict(tier)
    restart_payload = asdict(restart)
    assert tier_payload["tier"] == "comparison"
    assert tier_payload["metadata"] == {"threshold_free": True}
    assert restart_payload["checkpoint_ref"] is None
    assert restart_payload["checkpoint_ref_id"] == "ckpt-comparison"
    assert restart_payload["profile_fingerprint"] == "profile:comparison"
