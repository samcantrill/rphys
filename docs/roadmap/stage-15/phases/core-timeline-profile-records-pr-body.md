# Summary

Adds the Stage 15 Phase 1 training profiling substrate: additive timeline event metadata, append-only event logs, scalar span and unavailable profiling evidence, a provisional `TrainingProfile` aggregate/recorder, and an optional `TrainingResult.training_profile` attachment. Existing Stage 12 observability phases, callback/sink fanout behavior, and `TrainingResult.profiles` summary compatibility are preserved.

This phase creates the shared primitive record target for later profiling phases without adding resource traces, probe protocols, checkpoint/policy records, native engine instrumentation, Lightning integration, or data-path producers.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-15/phases/core-timeline-profile-records.md`
- Implementation plan: `docs/roadmap/stage-15/implementation-plan.md`
- Scientific review: `tests/contracts/test_stage12_observability_contract.py`, `tests/contracts/test_stage12_training_result_contract.py`, `tests/contracts/test_stage15_training_profile_contract.py`

# Phase Isolation

- Branch: `agent/stage-15-training-profiling-p1-core-timeline-profile-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p1-core-timeline-profile-records`
- Base branch: `develop`
- Head branch: `agent/stage-15-training-profiling-p1-core-timeline-profile-records`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: training events now accept optional run, timeline, sequence, timestamp, clock, process, node, rank, and device evidence; `TrainingEventLog` exposes immutable append-only event snapshots; profiling records expose scalar span and unavailable evidence; `TrainingProfileRecorder` returns frozen `TrainingProfile` snapshots; `TrainingResult.training_profile` is optional.
- Units/shapes/dtypes: timing values are non-negative seconds/timestamps represented as primitive numbers; sequence and rank/process fields are non-negative integers; profile/event collections are tuples; metadata and provenance remain primitive mappings.
- Sampling/alignment/provenance: timeline ordering is local to append-only event logs through strictly increasing sequence ids. Timestamp, clock name, and clock-origin fields are descriptive evidence and do not imply cross-process/device merge semantics. Missing timestamp evidence remains absent rather than encoded as zero.
- Pipeline-order implications: this phase records timeline/profile evidence only. It does not change loop control, callback return handling, learner execution order, device synchronization, checkpoint behavior, or data-path processing.
- Leakage or subject/split implications: no dataset split, subject identity, label, sampler, or datasource behavior changes are introduced.
- Legacy parity or intentional behavior changes: Stage 12 event phases and observe-only callback/sink behavior remain compatible. `TrainingResult.profiles` still accepts explicit profile summaries; when omitted and `training_profile` is provided, summaries are derived deterministically from scalar and unavailable profile evidence.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present in this repository
- [x] Acceptance or opt-in checks not present in this repository
- [x] Scientific/workflow contract review completed

Commands run:

```text
targeted unit coverage for training events/profiling/results: 18 passed
targeted contract coverage for Stage 12/15 training observability/results/profile contracts: 10 passed
make test-package: 72 passed
uv lock --check: passed after cache escalation
make test-summary: overall 1042 passed; package 72 passed, unit 760 passed, contract 180 passed, integration 30 passed; e2e and acceptance suites not present
make validate-pr: passed, including uv build and git diff --check
```

# Risks And Follow-Up

Phase 1 intentionally leaves resource trace schemas and persistence to Phase 3, probe/checkpoint/policy records to Phase 2 and later, native engine wiring to Phase 4, data-path profiling producers to Phase 5, and Lightning integration to Phases 6 and 7. The new profile aggregate is provisional and primitive-inspection friendly, but it does not define a durable file, JSON, or schema-versioned export format in this phase.

Pre-submit review blockers around dataclass inspection, non-finite timing values, and recorder-created sequence ids were resolved with focused unit/contract coverage before PR opening.
