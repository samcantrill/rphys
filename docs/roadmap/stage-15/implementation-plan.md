# Roadmap Stage 15 Implementation Plan

Status: draft; ready for maintainer review. Implementation has not started.
Roadmap version: `v15`
Planning document: `docs/roadmap/stage-15/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: none
Blockers: none for implementation-plan drafting. Before code work, refresh
Lightning public API/security evidence and verify whether Stage 14 synthetic
fixtures are available in the target branch.

## Summary

- Goal: make native, Lightning, future-engine, and data-path execution diagnosable through shared events, scalar spans, timestamped resource traces, checkpoint/resume evidence, policy records, and validation examples.
- Source functionality-agreement gate: passed; FQ-15-1 through FQ-15-10 locked or repo-resolved.
- Approved behavior: Stage 15 reuses Stage 9 data-path descriptors and Stage 12 training/event contracts while adding whole-path profiling, lifecycle hooks, checkpoint/resume records, policies, first-class optional Lightning support, data-path profiling, optional resource probes, metric blind-spot coverage, and descriptive tier/restart evidence.
- Source behavior confirmation: passed and locked in `docs/roadmap/stage-15/planning.md`.
- Key design constraints: core imports remain lightweight; no raw framework timelines as public evidence; no Lightning/torch/system-profiler import from base training modules; no workflow runtime, daemon, artifact store, scheduler, cost dashboard, automatic tuning, concrete storage backend, or machine-speed thresholds.
- Source design-agreement gate: passed; DQ-15-1, DQ-15-2, and DQ-15-4 maintainer-approved; DD-15-3 and DD-15-5 through DD-15-8 recorded recommendations.
- Source functionality-agreement queue: FQ-15-1 through FQ-15-10 locked/repo-resolved in `planning.md`.
- Source design-agreement queue: no unresolved design packet remains in `planning.md`.
- Source future-roadmap/reuse safety review: shared rphys result/profile/event/checkpoint/policy contracts preserved for future engines; Lightning-native inputs isolated to `rphys.training.lightning`; resource monitoring and data-path producers remain extension points.
- Examples covered: native whole-path profile, event/resource trace alignment, Lightning parity, checkpoint/resume, policy mapping, data-path benchmark, optional probes, metric blind-spot examples, BatchOperation equivalence, and tier/restart compatibility.
- Source phase shaping: five approved phases, refined by timestamped resource traces, metric taxonomy, and optional monitor-process requirements.
- Source plan quality gate: passed for implementation-plan drafting readiness.
- Out of scope: public workflow/job runner, long-lived monitor daemon, artifact store, default checkpoint writer, real dataset benchmark, mandatory GPU/Lightning/system probes, concrete optimized storage backend, Lightning-specific public result/profile/event family, broad distributed strategy parity.

## Implementation Workflow State

- Implementation-plan quality gate: draft; pending maintainer approval.
- Review pass: pending.
- Refinement pass: pending.
- Confirmation review: pending.
- Automatic merge mode: enabled.
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `shared-observability-profile-schema` | pending | `agent/stage-15-training-profiling-p1-shared-observability-profile-schema` | pending | `src/rphys/training/events.py`, `profiling.py`, `results.py`, training package exports, unit/contract/package tests | Define shared timestamped events, scalar spans, resource traces, recorder/monitor records, and `TrainingResult.training_profile`. | Unit/contract/package tests for primitive records, serialization, timestamps, trace ordering, unavailable probes, import boundaries. | Event/resource trace alignment and metric blind-spot schema examples. |
| 2 | `native-profile-checkpoint-hooks` | pending | `agent/stage-15-training-profiling-p2-native-profile-checkpoint-hooks` | pending | `src/rphys/training/backend.py`, `plan.py`, new checkpoint module if needed, native integration tests | Wire native lifecycle events, scalar spans, fake resource samplers, checkpoint/resume hooks, and teardown-after-failure evidence. | Native synthetic integration, checkpoint hook tests, fake process/thread sampler tests, package checks. | Native whole-path profile and checkpoint/resume examples. |
| 3 | `policies-lightning-adapter` | pending | `agent/stage-15-training-profiling-p3-policies-lightning-adapter` | pending | new `src/rphys/training/policies.py`, optional `src/rphys/training/lightning.py`, fake-Lightning tests, import/security checks | Add precision/compile/kernel policies and first-class optional Lightning support that normalizes into shared records. | Policy unit tests, fake-Lightning contract/integration tests, import-boundary checks, optional installed-Lightning acceptance when safe. | Lightning parity and policy mapping examples. |
| 4 | `datapath-resource-batch-evidence` | pending | `agent/stage-15-training-profiling-p4-datapath-resource-batch-evidence` | pending | `src/rphys/datasources/datapath.py`, optional probe helpers, `src/rphys/ops/batch.py` tests/docs as needed | Produce data-path benchmark/profile evidence, optional resource-probe examples, and BatchOperation optimization equivalence coverage. | Data-path contract/integration tests, fake probe tests, batch operation contract tests, docs/examples. | Data queue starvation, IO/decode/collate bottleneck, optional probe absence, BatchOperation equivalence. |
| 5 | `tier-restart-docs-hardening` | pending | `agent/stage-15-training-profiling-p5-tier-restart-docs-hardening` | pending | tier/restart records/docs, package exports, examples, final validation evidence | Add descriptive tier/restart evidence, complete docs/docstrings/examples, and run broad validation. | Focused tests plus `make test-package`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, `make validate-pr` where feasible. | Debug/smoke/signal/comparison/full tier and restart compatibility examples. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None for implementation-plan drafting. | Stage 15 planning quality gate passed. | Proceed only after maintainer approves this implementation plan. | resolved |
| Lightning API/security may change. | Planning accepted risk; external dependency is unstable. | Recheck official Lightning docs and known unsafe versions before Phase 3 code work and optional acceptance. | preflight required |
| Stage 14 synthetic fixtures may not be code-backed in this checkout. | Planning accepted assumption. | Before phases rely on Stage 14 support, verify target branch availability or use Stage 12/9 synthetic fixtures directly. | preflight required |

## Phase 1: Shared Observability And Profile Schema

Status: pending
Slug: `shared-observability-profile-schema`
Branch: `agent/stage-15-training-profiling-p1-shared-observability-profile-schema`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p1-shared-observability-profile-schema`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: define the public provisional schema that every later phase targets.
- Files/modules owned: `src/rphys/training/events.py`, `src/rphys/training/profiling.py`, `src/rphys/training/results.py`, `src/rphys/training/__init__.py`, `tests/unit/rphys/training/test_events.py`, `tests/unit/rphys/training/test_profiling.py`, `tests/unit/rphys/training/test_results.py`, `tests/contracts/test_stage12_observability_contract.py`, `tests/package/test_import*.py`.
- Behavior implemented: additive lifecycle phases, timestamp/timeline alignment evidence, primitive scalar span records, `TrainingStepProfile`, `ResourceSample`, `ResourceTrace`, `RunDecisionMetrics`, unavailable/unsupported/ambiguous probe evidence, monitor execution-mode evidence, recorder helper, and optional `TrainingResult.training_profile`.
- Decisions applied: DD-15-1 and DD-15-2.
- Future-roadmap/reuse constraints: records are engine-neutral and primitive; no raw framework timeline, tensor, profiler object, callback internals, optimizer state, or checkpoint payload enters the public profile schema.
- Examples or demos covered: schema-only examples for event/resource alignment, unavailable probes, dropped samples, ambiguous attribution, and metric taxonomy coverage.
- Out of scope: native loop wiring, checkpoint hook execution, Lightning adapter, real system/GPU probe implementation, data-path producers.
- Dependencies: approved planning gate and current Stage 12 event/profile/result code.

### Tasks

- Extend `TrainingEventPhase` additively and preserve Stage 12 phase values.
- Add event timestamp/timeline fields or equivalent primitive metadata with validation and serialization coverage.
- Add profile records for scalar spans, step profiles, resource samples/traces, run-decision metrics, metric kind/unit/scope/availability, monitor execution mode, unavailable/unsupported/ambiguous probes, dropped samples, sample cadence, overhead, and clock-alignment evidence.
- Add `TrainingProfile` with stable rphys-facing inspection helpers for spans, traces, events, decisions, summaries, and unavailable probes.
- Add optional `TrainingResult.training_profile` while preserving `TrainingResult.profiles` compatibility summaries.
- Update package exports intentionally and keep base imports dependency-light.
- Add unit, contract, and package tests for validation, primitive serialization, import boundaries, and backwards compatibility.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_events.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_results.py` | Validate shared record construction, invalid inputs, serialization, timestamps, traces, summaries, and result attachment. | yes |
| `uv run pytest tests/contracts/test_stage12_observability_contract.py` plus new Stage 15 contract tests if added | Prove Stage 12 compatibility and Stage 15 observability contract. | yes |
| `make test-package` | Prove no heavy imports or accidental public exports. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: old and new event phases validate; `TrainingProfile` contains timestamped events, scalar spans, resource traces, unavailable probes, and compatibility summaries.
- Design-decision evidence: DD-15-1 and DD-15-2 are implemented without breaking Stage 12 observers.
- Future-roadmap/reuse evidence: no backend-specific public profile family exists.
- Example/demo evidence: fake profile examples show GPU idle due to queue wait, checkpoint stall, memory pressure, hidden transfer/sync, unavailable probe, and ambiguous attribution records at schema level.
- Documentation evidence: docstrings explain units, timestamps, timeline IDs, sample cadence, dropped samples, and unavailable/unsupported/ambiguous status.
- Scientific contract evidence: timing values are nonnegative, sample ordering is explicit, and synchronization caveats are recorded.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped record-shape refinements
- PR review budget: schema/API review
- Blocker-resolution budget: stop and reopen planning only if profile data cannot stay primitive or engine-neutral
- Pre-submit blocker gate: no heavy imports, no raw framework payloads, no breaking Stage 12 event values
- Merge record: pending

### Risks And Stop Conditions

- Risks: profile schema breadth, timestamp semantics churn, result-schema compatibility, and hidden import regressions.
- Stop conditions: implementation requires raw backend timelines, framework objects in public records, or a non-additive event migration.
- Assumptions: provisional additive records can cover native, Lightning, future engines, and data-path producers without a registry.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 2: Native Whole-Path Profiling And Checkpoint Hooks

Status: pending
Slug: `native-profile-checkpoint-hooks`
Branch: `agent/stage-15-training-profiling-p2-native-profile-checkpoint-hooks`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p2-native-profile-checkpoint-hooks`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: make the native engine the reference implementation for the shared observability contract.
- Files/modules owned: `src/rphys/training/backend.py`, `src/rphys/training/plan.py`, `src/rphys/training/results.py`, `src/rphys/training/profiling.py`, new `src/rphys/training/checkpoint.py` if needed, native unit/integration tests.
- Behavior implemented: native setup/teardown events, data wait/device transfer/forward/objective/backward/optimizer/scheduler/validation/callback/checkpoint/profile-summary spans, fake resource samplers including background-thread/process modes, hook-based checkpoint save/restore, checkpoint refs/results, restart state, failure evidence, and teardown-after-failure events.
- Decisions applied: DD-15-1, DD-15-2, and DD-15-3.
- Future-roadmap/reuse constraints: checkpointing is hook/protocol based; rphys records evidence but does not serialize arbitrary backend state or own artifact lifecycle.
- Examples or demos covered: native whole-path profile, checkpoint/resume evidence, callback failure with teardown evidence, fake monitor process trace.
- Out of scope: Lightning, real GPU/system probes, generic artifact store, default filesystem checkpoint writer, scheduler/runtime.
- Dependencies: Phase 1.

### Tasks

- Add checkpoint/restart records and structural checkpointer hook/protocol.
- Extend `TrainingPlan` only with explicit, typed hooks/policies; avoid generic `engine_config`.
- Wrap native loop regions with recorder spans and timestamped events.
- Add fake timer and fake resource sampler support for deterministic tests.
- Add fake background-thread and background-process sampler tests that record lifecycle, dropped samples, backpressure, and cleanup evidence without starting long-lived daemons.
- Record checkpoint save/restore success, skip, failure, profile span, and restart compatibility evidence.
- Ensure observer/callback failures remain fail-loud and teardown is best-effort after setup starts.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_checkpoint.py` | Validate native wiring and checkpoint records/hooks. | yes |
| `uv run pytest tests/integration/test_stage12_synthetic_training_flow.py` or new `tests/integration/test_stage15_training_profile_flow.py` | Validate synthetic native success/failure, profile attachment, fake samplers, and checkpoint/resume evidence. | yes |
| `make test-package` | Prove native training core stays import-light. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: native `Trainer.fit` returns `TrainingResult.training_profile` with lifecycle events, scalar spans, resource traces, checkpoint evidence, and teardown-after-failure evidence.
- Design-decision evidence: DD-15-3 hook-only checkpoint boundary is visible in tests and docs.
- Future-roadmap/reuse evidence: future engines can match records without copying native internals.
- Example/demo evidence: native profile examples show data wait, transfer, checkpoint, callback, and unavailable/ambiguous probe cases.
- Documentation evidence: checkpoint docs state writer ownership and `CheckpointRef` is not a generic artifact reference.
- Scientific contract evidence: profiling does not change learner step semantics or output-spec validation.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped failure-order refinements
- PR review budget: native/checkpoint review
- Blocker-resolution budget: escalate if checkpoint hook shape cannot record resume evidence without owning serialization
- Pre-submit blocker gate: no default artifact store, no mandatory monitor process, no hidden datasource import
- Merge record: pending

### Risks And Stop Conditions

- Risks: timing perturbation, callback/checkpoint failure ordering, monitor-process cleanup, and hook interface ambiguity.
- Stop conditions: native resume requires framework-specific serialization in core, or resource monitoring needs scheduler semantics.
- Assumptions: fake samplers and fake checkpointers can validate contracts without optional dependencies.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 3: Policies And Optional Lightning API

Status: pending
Slug: `policies-lightning-adapter`
Branch: `agent/stage-15-training-profiling-p3-policies-lightning-adapter`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p3-policies-lightning-adapter`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add optimization policy records and a concrete optional Lightning adapter that pressure-tests shared outputs.
- Files/modules owned: new `src/rphys/training/policies.py`, optional `src/rphys/training/lightning.py`, selected training package export/import tests, fake-Lightning tests, optional acceptance tests.
- Behavior implemented: `PrecisionPolicy`, `CompilePolicy`, `KernelPolicy`, native unsupported/fallback diagnostics, Lightning-safe version preflight, `LightningTrainingEngine`, Lightning-native entrypoints for module/datamodule/dataloaders, profiler/callback/resource/checkpoint/policy mapping into shared rphys records.
- Decisions applied: DD-15-4 and DD-15-5.
- Future-roadmap/reuse constraints: Lightning-native inputs are allowed only under `rphys.training.lightning`; outputs stay shared rphys `TrainingResult`, `TrainingProfile`, timestamped `TrainingEvent`, resource trace, checkpoint, and policy records.
- Examples or demos covered: rphys learner through Lightning engine, direct LightningModule/DataModule or dataloader entrypoint, policy mapping, `ckpt_path`, normalized profile evidence.
- Out of scope: base Lightning/torch dependency, root import loading Lightning, Lightning-specific result/profile/event families, private trainer state as public contract, full distributed strategy parity.
- Dependencies: Phases 1 and 2; fresh Lightning docs/security preflight.

### Tasks

- Add primitive policy records with requested/applied/fallback/unsupported/determinism/equivalence evidence.
- Add package/import checks proving base `rphys.training` imports do not load Lightning, torch, CUDA/NVML, or system profilers.
- Add Lightning package/version preflight that rejects or clearly reports known unsafe versions before adapter execution.
- Implement optional `LightningTrainingEngine` for the shared `Trainer`/`TrainingEngine` path.
- Implement explicit Lightning-native public entrypoints under `rphys.training.lightning`.
- Map Lightning callbacks/profiler/checkpoints/`ckpt_path`/trainer kwargs/policies into shared rphys records.
- Add fake-Lightning tests for absent dependency, unsafe version, learner-wrapper path, Lightning-native path, checkpoint mapping, resource monitor mapping, and unsupported distributed/private-state diagnostics.
- Add optional installed-Lightning acceptance guarded by marker/skip/unavailable evidence when safe and installed.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_policies.py` | Validate policy records and fallback/unsupported diagnostics. | yes |
| Fake-Lightning focused tests under `tests/unit` or `tests/contracts` | Validate adapter behavior without installing Lightning. | yes |
| `make test-package` | Validate lazy optional imports and public exports. | yes |
| Optional `uv run pytest -m lightning_acceptance ...` | Validate against installed safe Lightning when available. | no, optional but record skip/unavailable evidence |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: both Lightning entrypoint families return shared rphys results/profiles/events/checkpoints/policies in fake tests.
- Design-decision evidence: DD-15-4 first-class optional API and DD-15-5 backend-neutral policy records are implemented.
- Future-roadmap/reuse evidence: future adapters can follow the same optional-module and shared-output pattern.
- Example/demo evidence: learner-wrapper and Lightning-native examples show normalized spans, resource traces, checkpoint refs, and policy diagnostics.
- Documentation evidence: docs explain optional dependency, security preflight, unsupported distributed/private-state boundary, and no raw Lightning timelines.
- Scientific contract evidence: precision/compile/kernel policy evidence records requested/applied/fallback state and no silent dtype/device change.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle after Lightning preflight refresh
- Implementation/refinement budget: 1 implementation pass plus adapter refinements
- PR review budget: optional dependency/import boundary review
- Blocker-resolution budget: stop if Lightning support requires shared-output exceptions
- Pre-submit blocker gate: no base Lightning/torch import, no unsafe-version execution, no Lightning-specific result family
- Merge record: pending

### Risks And Stop Conditions

- Risks: upstream Lightning API/security churn, public optional API breadth, trainer kwargs leakage, distributed attribution, and private-state temptation.
- Stop conditions: current Lightning docs/security make safe implementation impossible, or adapter requires exposing private trainer state.
- Assumptions: fake-Lightning tests can cover contract behavior, with installed-Lightning acceptance optional.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Data-Path Profiling, Resource Probes, And BatchOperation Evidence

Status: pending
Slug: `datapath-resource-batch-evidence`
Branch: `agent/stage-15-training-profiling-p4-datapath-resource-batch-evidence`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p4-datapath-resource-batch-evidence`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: extend diagnosis beyond the model loop without adding a storage/runtime backend.
- Files/modules owned: `src/rphys/datasources/datapath.py` or sibling datasource profiling helpers, optional probe helper modules if needed, `src/rphys/ops/batch.py` tests/docs as needed, data-path/BatchOperation tests.
- Behavior implemented: synthetic data-path profile/benchmark producers over Stage 9 records, reserved measurement keys, IO/decode/cache/queue/worker/collate/network/throughput evidence, fake optional probes, optional real probe acceptance, BatchOperation equivalence/replay/provenance/mask/alignment/dtype/device validation.
- Decisions applied: DD-15-6 and DD-15-7, with DD-15-2 metric taxonomy constraints.
- Future-roadmap/reuse constraints: future storage backends can produce comparable evidence over Stage 9 descriptors; production optimization changes are added only for concrete contract gaps.
- Examples or demos covered: GPU idle due to data queue starvation, IO/decode/collate bottleneck, unavailable optional probe, hidden transfer/sync evidence, BatchOperation equivalence and non-equivalence.
- Out of scope: concrete optimized storage backend, implicit caches, raw-data benchmarks, machine-speed thresholds, automatic vectorizer, backend execution planner.
- Dependencies: Phase 1; can run independently of Phase 3 once shared schema is merged.

### Tasks

- Add or refine data-path profiling helpers that output existing `DataPathProfile`/`DataPathBenchmark` compatible evidence.
- Define and document reserved measurement keys and units for decode, collate, queue, worker, network, bytes, throughput, and unavailable evidence.
- Add fake-timer tests for cache hit/miss, prepared/materialized paths, decode/collate/queue/network attribution, serialization, and no thresholds.
- Add fake resource probe examples over the shared `ResourceTrace` schema where useful for data-path bottleneck examples.
- Add optional real probe acceptance only if safe and installed, with explicit unavailable evidence otherwise.
- Add BatchOperation tests/examples for equivalence, replay, masks, alignment, dtype/device, provenance, unsupported fields, and failure diagnostics.
- Escalate only if reserved measurement keys cannot validate attribution clearly enough.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/contracts/test_data_path_records_contract.py` | Validate data-path record compatibility and serialization. | yes |
| `uv run pytest tests/integration/test_stage9_data_path_flow.py` or new Stage 15 data-path tests | Validate synthetic profile/benchmark producers. | yes |
| Focused BatchOperation contract/integration tests | Validate scientific equivalence and failure behavior. | yes |
| Fake optional-probe tests | Validate unavailable/unsupported/ambiguous probe evidence and metric taxonomy examples. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: data-path benchmarks identify source/cache/prepared/decode/collate/queue/network/throughput evidence without speed thresholds.
- Design-decision evidence: DD-15-6 and DD-15-7 are implemented without duplicate descriptor families or automatic optimization claims.
- Future-roadmap/reuse evidence: future storage adapters can emit comparable benchmark evidence.
- Example/demo evidence: GPU idle/data queue, checkpoint stall, memory pressure, transfer/sync, and unavailable probe examples are represented.
- Documentation evidence: reserved measurement keys, units, and attribution limitations are documented.
- Scientific contract evidence: BatchOperation optimization evidence preserves masks, alignment, dtype/device, provenance, and replay semantics.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus attribution refinements
- PR review budget: data-path and scientific contract review
- Blocker-resolution budget: add a small typed timing child record only if validation proves reserved keys too vague
- Pre-submit blocker gate: no storage backend, no implicit cache, no speed thresholds, no automatic vectorizer
- Merge record: pending

### Risks And Stop Conditions

- Risks: reserved-key drift, attribution ambiguity, probe overhead, and accidental loader/runtime scope creep.
- Stop conditions: profiling helpers require new storage backend, real data, or machine-specific assertions.
- Assumptions: Stage 9 descriptors can carry Stage 15 measurements initially.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: Experiment Tiers, Restart Compatibility, Docs, And Final Hardening

Status: pending
Slug: `tier-restart-docs-hardening`
Branch: `agent/stage-15-training-profiling-p5-tier-restart-docs-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p5-tier-restart-docs-hardening`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: close the public contract with descriptive tiers, restart compatibility, docs, examples, import/security checks, and broad validation.
- Files/modules owned: tier/restart record modules if not already added, docs/docstrings/examples touched by prior phases, package/export checks, final validation artifacts.
- Behavior implemented: `ExperimentTierSpec` or equivalent descriptive tier records, restart snapshots linked to checkpoints/profile/data-path evidence, docs for profiles/checkpoints/policies/Lightning/resource monitors/data-path metrics, broad validation evidence, revisit triggers.
- Decisions applied: DD-15-8 plus final obligations from DD-15-1 through DD-15-7.
- Future-roadmap/reuse constraints: tiers are descriptive evidence only; downstream/`loom` may orchestrate using them, but rphys does not schedule work or manage artifacts.
- Examples or demos covered: debug/smoke/signal/comparison/full tier descriptors and restart compatibility examples.
- Out of scope: workflow scheduler, cost dashboard, artifact lifecycle, alternate fake execution path, new behavior beyond accepted scope.
- Dependencies: Phases 1-4.

### Tasks

- Add descriptive tier/restart records if not completed by earlier checkpoint work.
- Link restart evidence to checkpoint refs, loader/materialization fingerprints, profile summaries, completion markers, and compatibility notes.
- Finalize docs/docstrings for event timestamps, scalar spans, resource traces, monitor-process mode, metric taxonomy, unavailable probes, checkpoint boundaries, policies, Lightning optional API, data-path profiling, and Stage 9/12/13 reuse.
- Ensure package exports are intentional and code-backed.
- Run focused tests from touched phases and broaden to package/contract/integration/summary/lock/PR validation as feasible.
- Record accepted risks and deferred optional real-probe/Lightning acceptance if environment support is unavailable.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Focused `uv run pytest ...` for changed tier/restart/docs examples | Validate closeout records and examples. | yes |
| `make test-package` | Validate public API and import boundaries. | yes |
| `make test-contract` | Validate public contracts. | yes |
| `make test-integration` | Validate integrated native/data-path flows. | yes |
| `make test-summary` | Produce test summary evidence. | yes, unless blocked and recorded |
| `uv lock --check` | Validate dependency lock state. | yes |
| `git diff --check` | Catch whitespace issues. | yes |
| `make validate-pr` | Final PR validation. | yes, unless blocked and recorded |

### Acceptance Evidence

- Behavior evidence: tier/restart evidence is descriptive and linked to profile/checkpoint/data-path fingerprints.
- Design-decision evidence: no stage decision remains undocumented or unvalidated.
- Future-roadmap/reuse evidence: downstream/`loom` can orchestrate over typed evidence without rphys owning runtime.
- Example/demo evidence: public examples cover native, Lightning, data-path, metric blind spots, checkpoint/resume, and tiers.
- Documentation evidence: public records document units, timestamps, resource trace semantics, monitor lifecycle, optional dependency behavior, and unsupported/unavailable cases.
- Scientific contract evidence: no hidden synchronization, no speed thresholds, no raw timelines, no opaque checkpoint payloads, and no altered BatchOperation meaning.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus final hardening
- PR review budget: final API/docs/validation review
- Blocker-resolution budget: record blocked broad commands with residual risk; do not add workflow runtime to make validation convenient
- Pre-submit blocker gate: docs complete, package imports clean, no unresolved optional dependency/security issue
- Merge record: pending

### Risks And Stop Conditions

- Risks: docs drift, late import/security failures, optional acceptance unavailable, and tier fields drifting into scheduling semantics.
- Stop conditions: closeout requires scheduler/artifact lifecycle, mandatory hardware tests, or real dataset benchmarks.
- Assumptions: default validation can stay CPU-only, synthetic, deterministic, and threshold-free.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: run phase-focused `uv run pytest ...` first, then broaden to `make test-package`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` as scope allows.
- Docs/template checks: ensure all public/provisional records have docstrings covering units, timestamps, sample cadence, resource attribution, unavailable/unsupported/ambiguous status, checkpoint ownership, and optional dependency behavior.
- Scientific/workflow contract checks: no hidden synchronization, no raw framework timeline payloads, no workflow runtime, no artifact store, no speed thresholds, no concrete storage backend, no public helper registry, and no engine-specific output family.
- Example/demo checks: native whole-path profile, Lightning parity, checkpoint/resume, policy mapping, data-path bottleneck, optional monitor-process probe, metric blind-spot examples, BatchOperation equivalence, and tier/restart compatibility.
- Manual review focus: import boundaries, provisional public schema breadth, resource monitor lifecycle, checkpoint hook boundary, Lightning adapter isolation, and data-path attribution clarity.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Implementation phases preserve the five planning-approved review boundaries. | note | Phase 1 schema, Phase 2 native/checkpoint, Phase 3 policies/Lightning, Phase 4 data-path/resource/batch, and Phase 5 docs/final hardening map directly to `planning.md`. | recorded |
| Resource monitor process support is included without daemon/runtime ownership. | note | Phase 1 defines primitive records; Phase 2 validates fake lifecycle; Phase 4 may add optional real probes; all phases keep monitor process optional and run-scoped. | recorded |
| Lightning acceptance depends on current upstream API/security state. | concern | Phase 3 has a required preflight and optional real acceptance only when dependency is installed and safe. | open preflight |
| Stage 14 synthetic fixture availability is not assumed. | concern | Phase work can use Stage 9/12 synthetic flows unless Stage 14 fixtures are present in the target branch. | open preflight |

Gate result:

- Status: draft; pending maintainer approval.
- Review evidence: manager-drafted from `planning.md` after plan-quality pass and maintainer refinements for resource traces, metric taxonomy, and monitor-process support.
- Accepted risks: schema may need additive revision after native/Lightning pressure; optional real probes and installed-Lightning acceptance may be unavailable locally; resource attribution may be ambiguous for system-wide probes.
- Revisit triggers: Lightning security/API changes; profile schema cannot represent a material metric without opaque payloads; resource monitoring needs daemon/scheduler semantics; data-path reserved keys cannot support attribution; checkpoint hooks require core-owned serialization.

## Final Approval

- Approval status: pending maintainer review.
- Approved scope: pending.
- Accepted risks: pending.
- Deferred items: concrete optimized storage backend, workflow runtime, artifact store, cost dashboard, automatic tuning, real dataset benchmarks, mandatory hardware acceptance, and full distributed/private-state Lightning parity.
