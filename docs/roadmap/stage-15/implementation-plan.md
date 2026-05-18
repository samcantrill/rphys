# Roadmap Stage 15 Implementation Plan

Status: in implementation; Phase 1, Phase 2, Phase 3, and Phase 4 merged.
Roadmap version: `v15`
Planning document: `docs/roadmap/stage-15/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 5 pending
Blockers: none for implementation-plan approval. Before Lightning and
fixture-dependent code work, refresh Lightning public API/security evidence and
verify whether Stage 14 synthetic fixtures are available in the target branch.

## Summary

- Goal: make native, Lightning, future-engine, and data-path execution diagnosable through shared events, append-only timeline logs, scalar spans, timestamped resource traces, checkpoint/resume evidence, policy records, and validation examples.
- Source functionality-agreement gate: passed; FQ-15-1 through FQ-15-10 locked or repo-resolved.
- Approved behavior: Stage 15 reuses Stage 9 data-path descriptors and Stage 12 training/event contracts while adding whole-path profiling, lifecycle hooks, checkpoint/resume records, policies, first-class optional Lightning support, data-path profiling, optional resource probes, metric blind-spot coverage, and descriptive tier/restart evidence.
- Source behavior confirmation: passed and locked in `docs/roadmap/stage-15/planning.md`.
- Key design constraints: core imports remain lightweight; no raw framework timelines as public evidence; no Lightning/torch/system-profiler import from base training modules; no workflow runtime, daemon, artifact store, scheduler, cost dashboard, automatic tuning, concrete storage backend, or machine-speed thresholds.
- Source design-agreement gate: passed; DQ-15-1, DQ-15-2, and DQ-15-4 maintainer-approved; DD-15-3 and DD-15-5 through DD-15-8 recorded recommendations.
- Source functionality-agreement queue: FQ-15-1 through FQ-15-10 locked/repo-resolved in `planning.md`.
- Source design-agreement queue: no unresolved design packet remains in `planning.md`.
- Source future-roadmap/reuse safety review: shared rphys result/profile/event/checkpoint/policy contracts preserved for future engines; Lightning-native inputs isolated to `rphys.training.lightning`; resource monitoring and data-path producers remain extension points.
- Examples covered: native whole-path profile, event/resource trace alignment, rank/device-aware metric series, Lightning parity, checkpoint/resume, policy mapping, data-path benchmark, optional probes, metric blind-spot examples, BatchOperation equivalence, and tier/restart compatibility.
- Source phase shaping: original five approved phases have been re-reviewed and rebalanced into eight implementation phases after expanded probe, checkpoint, pipeline-stage, resource-monitoring, and Lightning bridge scope.
- Source plan quality gate: passed for initial implementation-plan drafting and startup implementation review/refinement/confirmation.
- Out of scope: public workflow/job runner, long-lived monitor daemon, artifact store, default checkpoint writer, real dataset benchmark, mandatory GPU/Lightning/system probes, concrete optimized storage backend, Lightning-specific public result/profile/event family, broad distributed strategy parity.

## Planned Runtime Observability Shape

- `Trainer` remains the public facade. It validates that the selected engine
  implements `fit`, `validate`, `test`, and `predict`, then delegates loop
  ownership to that engine.
- `TrainingEngine` remains the shared engine protocol. Native, Lightning, and
  future engines return the same `TrainingResult` and shared profile/event
  records even when their inputs differ.
- `NativeTrainingEngine` owns the reference Python loop and can emit rphys
  events/spans directly around setup, data wait, device transfer, learner step,
  objective, backward, optimizer, scheduler, validation, callback, checkpoint,
  summary, teardown, and failure regions.
- `LightningTrainingEngine` is planned as an optional adapter under
  `rphys.training.lightning`. It should translate Lightning public callbacks,
  profiler hooks, checkpoint hooks, `ckpt_path`, precision, and trainer state
  summaries into the same rphys event/profile/checkpoint/policy records instead
  of exposing a Lightning-specific result family.
- `TrainingEventLog` or equivalent append-only timeline evidence should record
  timestamped events with sequence ids, timeline ids, run ids, engine ids,
  process ids, node ids, local ranks, global ranks, device ids where relevant,
  and enough clock-origin metadata to merge per-process traces without claiming
  impossible global ordering.
- `TrainingProfileRecorder` should be the low-overhead shared fanout point for
  events, scalar spans, resource traces, callback timings, checkpoint timings,
  unavailable probes, dropped samples, and writer lifecycle evidence.
- `Probe` should be the generic inspection protocol for producing diagnostic
  evidence during a run. Probes inspect a hook context and emit primitive
  profile records, scalar metrics, trace samples, or unavailable evidence. They
  should declare cadence, hook points, selectors, attribution needs, and failure
  policy so engines can invoke them without knowing their internal logic.
- `ModelProbe` should cover model-specific diagnostics such as parameter norms,
  gradient norms, gradient-to-weight ratios, update norms, activation summaries,
  NaN/Inf counts, zero fractions, saturation/clipping evidence, and selected
  layer statistics. It should store summaries by default, not raw tensors.
- `DataProbe` should cover data-specific diagnostics such as batch schema
  validity, missing fields, NaN/Inf counts, mask validity, shape/dtype/device
  drift, value distributions, label/target distributions, sample provenance,
  decode/collate anomalies, and pre/post-device-transfer statistics.
- Dataset and data-pipeline probe hook points should be locked over the
  existing Stage 9 `SampleSource`, `IndexSampleSource`, `CachedSampleSource`,
  `PreparedSampleSource`, `StreamingReadPlan`, `DataLoaderState`, and
  `DataPathProfile` contracts. Stage 15 should not introduce a competing
  dataset abstraction, but it should define stable pipeline-stage names such as
  `indexed`, `pre_cache_processing`, `cache_lookup`, `cache_hit_load`,
  `cache_miss_source_read`, `cache_write`, `prepared_read`,
  `pre_augmentation`, `post_augmentation`, `post_processing`,
  `collate`, `pre_device_transfer`, `post_device_transfer`, and
  `learner_output_validation`.
- The pipeline-stage contract should support both common flows:
  `Process -> Cache -> Augment -> Process` and
  `Load from cache/prepared -> Augment -> Process`. Probe records must identify
  which stage produced the observation, whether the sample came from source,
  cache, prepared/materialized storage, or augmentation, and which request,
  operation, materialization, cache, split, worker, and rank fingerprints apply.
- `ResourceProfiler` should be a structural component protocol. Concrete
  optional profilers can include `AcceleratorProfiler`, `GPUProfiler`,
  `ProcessorProfiler`, `DiskProfiler`, `NetworkProfiler`, data-loader/queue
  profilers, and framework/compiler profilers. They produce primitive
  `ResourceTrace` samples rather than framework objects.
- Resource profilers may be implemented as asynchronous `ResourceProbe`
  components when they sample independently of engine hook points. Model and
  data probes are usually hook-driven because they need access to model,
  gradient, output, or batch objects at precise lifecycle points.
- Profiler components should be engine-neutral by default. A GPU, CPU, disk,
  network, or async-writer profiler should work under Native, Lightning, and
  future engines when the required process/device information is available.
  Engine-specific code should usually be a bridge or hook adapter, not a
  separate public profile family.
- Native-specific instrumentation should mean native loop hooks around regions
  that only the native loop owns, such as direct `device_mover`, learner step,
  backward, optimizer, and scheduler calls. It should feed the shared recorder
  instead of creating a `NativeProfile` object family.
- Lightning-specific instrumentation should mean a Lightning callback/profiler
  bridge under `rphys.training.lightning`. It should translate Lightning public
  lifecycle, profiler, checkpoint, rank, and trainer evidence into shared rphys
  events, spans, resource traces, checkpoint records, and policy records.
- Users should be able to combine Lightning execution with custom rphys
  profilers. For example, a user can rely on Lightning for DDP, precision,
  checkpoint integration, and torchmetrics while adding rphys disk/network/GPU
  profilers that start and stop through the Lightning adapter lifecycle and tag
  samples with Lightning global/local rank evidence.
- Checkpointing should be governed by engine-neutral checkpoint policies and
  normalized checkpoint records. Policies should support multiple checkpoint
  streams, cadence by step/epoch/time/metric/failure/final, retention by
  recency and metric quality, and explicit pruning evidence. Engines may use
  native hooks or framework callbacks to perform the save/load/delete work, but
  rphys should record `CheckpointRef`, save/restore/prune results, retention
  reason, rank/process evidence, and failure behavior.
- Checkpoint discovery and restart selection should be programmatic. A
  `CheckpointIndex` or `CheckpointCatalog` should record where checkpoints live
  and enough metadata to select one by policy instead of hard-coding a path:
  latest completed, best by metric, N epochs back, N steps back, before/after a
  timestamp, failure checkpoint, final checkpoint, or an explicitly supplied
  ref. The catalog is evidence and selection logic, not an artifact store.
- Rewind and resume should be represented by `RestartPolicy` or equivalent
  selection records. Example semantics include `resume="latest"`,
  `resume=BestCheckpoint("val_loss")`, `resume=RewindEpochs(2)`, and
  `resume=BeforeFailure()`. Engines resolve those policies against the shared
  checkpoint catalog and then pass the resulting checkpoint to the native hook
  or Lightning `ckpt_path`/restore behavior.
- Lightning checkpoint support should map directly onto public Lightning
  checkpoint callbacks where possible. Best-k metric retention maps to
  Lightning `ModelCheckpoint(save_top_k=k, monitor=..., mode=...)`; periodic
  saving maps to `every_n_train_steps`, `every_n_epochs`, or
  `train_time_interval`; deterministic latest access maps to `save_last`.
  Rolling recency retention such as "keep the last 10 step checkpoints" may
  require an rphys Lightning retention bridge or pruner because Lightning's
  built-in `save_top_k` is metric-oriented and `save_last` keeps one latest
  checkpoint.
- Model-analysis metrics should be profile producers, not ordinary task
  metrics. A `ModelAnalysisProbe` or equivalent should be able to measure
  layer/parameter/gradient/update/activation statistics at selected hook points,
  with explicit cadence, layer selectors, aggregation, rank/device attribution,
  and no raw tensor capture by default. Native can run these probes around
  direct backward/optimizer boundaries; Lightning should run them through public
  callback hooks such as backward and optimizer-step hooks.
- Data-analysis metrics should use the same probe mechanism. Native can invoke
  `DataProbe` instances after batch fetch/collation, before and after device
  transfer, after learner output validation, and around data-path producer
  boundaries. Lightning can invoke compatible data probes from public batch
  lifecycle hooks and from rphys adapter points where dataloaders or batches are
  normalized.
- Background profiling may use a thread or subprocess per run. It starts during
  engine setup, stops during teardown or failure cleanup, communicates through a
  bounded queue or temporary trace file, records backpressure/dropped-sample
  evidence, and never becomes a daemon, scheduler, or required runtime service.
- Profile persistence should be asynchronous and periodic. The implementation
  should support bounded buffering and explicit flush points at step/epoch/run
  boundaries without synchronously writing every callback event on the hot path.
- Metric naming should be field-driven first, with a stable derived series key
  for export. Examples: `event_log.global_rank=0`,
  `resource.gpu.global_rank=0.device=0.memory.used.bytes`,
  `resource.disk.global_rank=0.mount=data.read.bytes_per_second`. Export
  adapters may later map these records into existing rphys data-field
  components, but the core public profile schema should remain training-profile
  records rather than requiring a `Batch` or `DataField` container.

## Implementation Workflow State

- Implementation-plan quality gate: passed after startup review/refinement/confirmation.
- Review pass: scope-expansion review recorded on 2026-05-18.
- Refinement pass: eight-phase implementation split recorded; startup quality-gate blocker refinement recorded.
- Confirmation review: passed on 2026-05-18.
- Automatic merge mode: enabled.
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Expanded Scope Review

Scope expansion review on 2026-05-18 found that the original five phases were no
longer balanced after adding generic probes, pipeline-stage hooks, checkpoint
catalogs, restart selectors, async resource monitoring, model/data analysis, and
the split between Lightning API foundation and Lightning observability bridges.
The implementation plan is reshaped into eight phases below.

| Finding | Impact | Refinement |
| --- | --- | --- |
| Core schema was carrying too many unrelated contracts. | A single PR would mix event logs, probes, checkpoint catalogs, resource monitoring, and result attachment. | Split core timeline/profile records from probe/checkpoint/pipeline policy records. |
| Resource monitoring has independent lifecycle and failure modes. | Background processes, async writers, dropped samples, and probe health need focused validation. | Give resource monitoring and profile persistence a dedicated phase. |
| Native integration was too broad. | Native loop spans, checkpoint hooks, probes, writers, and restart behavior need a reference implementation without Lightning churn. | Keep Native as one integration phase after shared contracts are locked. |
| Data-pipeline probes need Stage 9 alignment. | Pre-cache, post-cache, prepared, augmentation, collation, and device-transfer stages require their own contract tests. | Give Stage 9 data-path and BatchOperation evidence a dedicated phase. |
| Lightning scope mixed public API and observability bridges. | Import/security/API foundation can be reviewed separately from callback/profiler/checkpoint/probe normalization. | Split Lightning into foundation/policies and observability/checkpoint/probe bridges. |
| Final docs and tier/restart closeout still need a broad validation pass. | Public contracts need examples, docs, and final checks after all integrations land. | Keep a final hardening phase. |

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `core-timeline-profile-records` | merged | `agent/stage-15-training-profiling-p1-core-timeline-profile-records` | [#95](https://github.com/samcantrill/rphys/pull/95) | `src/rphys/training/events.py`, `profiling.py`, `results.py`, package exports, unit/contract/package tests | Define timestamped events, append-only event logs, scalar spans, profile recorder basics, result attachment, and compatibility summaries. | Event/profile/result unit tests, Stage 12 contract tests, package import checks. | Per-rank event log, scalar span summary, unavailable profile evidence. |
| 2 | `probe-checkpoint-policy-contracts` | merged | `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts` | [#96](https://github.com/samcantrill/rphys/pull/96) | new or updated `src/rphys/training/probes.py`, `checkpoint.py`, `policies.py`, shared tests/docs | Define generic probes, model/data probe records, pipeline-stage hook names, checkpoint policies/catalogs, restart selectors, and precision/compile/kernel policy records. | Probe/checkpoint/policy unit and contract tests; primitive serialization checks. | Gradient probe record, batch NaN probe record, latest/best/rewind checkpoint selection. |
| 3 | `resource-monitoring-profile-persistence` | merged | `agent/stage-15-training-profiling-p3-resource-monitoring-profile-persistence` | [#97](https://github.com/samcantrill/rphys/pull/97) | resource profiler helpers, async writer contracts, fake sampler tests | Implement engine-neutral resource traces, fake CPU/GPU/disk/network probes, background thread/process sampler contracts, async profile writer contracts, and drop/backpressure evidence. | Fake resource probe tests, fake process/thread tests, async writer tests, package checks. | GPU idle trace, disk IO trace, dropped samples, writer flush lifecycle. |
| 4 | `native-engine-observability-checkpoints` | merged | `agent/stage-15-training-profiling-p4-native-engine-observability-checkpoints` | [#98](https://github.com/samcantrill/rphys/pull/98) | `src/rphys/training/backend.py`, `plan.py`, `checkpoint.py`, native integration tests | Wire Native setup/teardown, spans, event logs, probes, checkpoint save/restore/prune, restart selectors, async writer, and failure evidence. | Native unit/integration tests, checkpoint retention/catalog tests, fake probe tests. | Native whole-path profile, keep-last checkpoints, rewind two epochs, model/data probes. |
| 5 | `datapath-pipeline-probes-batch-evidence` | pending | `agent/stage-15-training-profiling-p5-datapath-pipeline-probes-batch-evidence` | pending | `src/rphys/datasources/datapath.py`, Stage 9 source/cache/prepared helpers, `src/rphys/ops/batch.py` tests/docs as needed | Add Stage 9 aligned pipeline-stage probe contexts, data-path benchmark/profile producers, data-quality probes, and BatchOperation equivalence evidence. | Data-path contract/integration tests, dataset-stage hook tests, BatchOperation tests, package import checks. | Process-cache-augment-process, cache/prepared-load-augment-process, queue starvation, batch NaNs. |
| 6 | `lightning-api-policy-foundation` | pending | `agent/stage-15-training-profiling-p6-lightning-api-policy-foundation` | pending | `src/rphys/training/lightning.py`, policy mapping tests, import/security tests | Add optional first-class Lightning public API, lazy import/security preflight, shared `TrainingEngine` path, Lightning-native entrypoints, and precision/compile/kernel policy mapping. | Fake-Lightning API tests, policy tests, package import checks, optional installed-Lightning smoke when safe. | `Trainer(engine=LightningTrainingEngine)`, LightningModule/DataModule entrypoint, precision policy mapping. |
| 7 | `lightning-observability-checkpoint-bridges` | pending | `agent/stage-15-training-profiling-p7-lightning-observability-checkpoint-bridges` | pending | Lightning callback/profiler/checkpoint/probe bridges, fake-Lightning integration tests | Normalize Lightning callbacks, profiler hooks, ranks, checkpoints, retention, restart selectors, model/data probes, resource monitors, and async writer evidence into shared records. | Fake-Lightning bridge tests, checkpoint pruning/restart tests, model/data probe bridge tests, optional acceptance. | Lightning DDP-style rank attribution, best-k and keep-last retention, custom rphys probes under Lightning. |
| 8 | `tiers-docs-final-hardening` | pending | `agent/stage-15-training-profiling-p8-tiers-docs-final-hardening` | pending | tier/restart/docs/examples, package exports, final validation evidence | Add descriptive tiers/restart snapshots if not already complete, finalize docs/examples, and run broad validation. | Focused tests plus package/contract/integration/summary/lock/PR checks where feasible. | Debug/smoke/signal/comparison/full tiers, complete Native/Lightning/data-path examples. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None for implementation-plan drafting. | Stage 15 planning quality gate passed. | Proceed only after maintainer approves this implementation plan. | resolved |
| Lightning API/security may change. | Planning accepted risk; external dependency is unstable. | Recheck official Lightning docs and known unsafe versions before Phase 6 and Phase 7 code work and optional acceptance. | preflight required |
| Stage 14 synthetic fixtures may not be code-backed in this checkout. | Planning accepted assumption. | Before phases rely on Stage 14 support, verify target branch availability or use Stage 12/9 synthetic fixtures directly. | preflight required |

## Phase 1: Core Timeline And Profile Records

Status: merged
Slug: `core-timeline-profile-records`
Branch: `agent/stage-15-training-profiling-p1-core-timeline-profile-records`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p1-core-timeline-profile-records`
PR: [#95](https://github.com/samcantrill/rphys/pull/95)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: define the minimal shared timeline/profile substrate that every later phase targets.
- Files/modules owned: `src/rphys/training/events.py`, `src/rphys/training/profiling.py`, `src/rphys/training/results.py`, `src/rphys/training/__init__.py`, `tests/unit/rphys/training/test_events.py`, `tests/unit/rphys/training/test_profiling.py`, `tests/unit/rphys/training/test_results.py`, `tests/contracts/test_stage12_observability_contract.py`, `tests/package/test_import*.py`.
- Behavior implemented: additive lifecycle phases, timestamp/timeline alignment fields, append-only event-log records, primitive scalar span records, basic `TrainingProfile`, recorder basics, optional `TrainingResult.training_profile`, and compatibility with existing `TrainingResult.profiles` summaries. Phase 1 exposes event-log, span, decision, summary, and unavailable-evidence helpers only; concrete resource trace record types and `resource_traces` helpers are deferred to Phase 3 as additive public surface.
- Decisions applied: DD-15-1 and DD-15-2.
- Future-roadmap/reuse constraints: records are engine-neutral and primitive; no raw framework timeline, tensor, profiler object, callback internals, optimizer state, checkpoint payload, or data-path object enters core profile records.
- Examples or demos covered: schema-only examples for timestamped event logs, scalar spans, unavailable spans, per-rank timeline metadata, and compatibility summaries.
- Out of scope: probe records, checkpoint catalogs, resource traces, native loop wiring, Lightning adapter, data-path producers, real system/GPU probe implementation.
- Dependencies: approved planning gate and current Stage 12 event/profile/result code.

### Tasks

- Extend `TrainingEventPhase` additively and preserve Stage 12 phase values.
- Add event timestamp/timeline fields or equivalent primitive metadata with validation and serialization coverage.
- Add append-only event-log records with sequence ids, run ids, timeline ids, process ids, node ids, local ranks, global ranks, and clock-origin metadata.
- Add scalar span and unavailable-span records with nonnegative timing, overhead, synchronization notes, and primitive metadata.
- Add `TrainingProfile` with stable rphys-facing inspection helpers for events, scalar spans, decisions, summaries, and unavailable probes. Do not expose concrete resource trace fields or trace accessors in Phase 1; Phase 3 adds `ResourceTrace` and resource-trace helpers additively.
- Add optional `TrainingResult.training_profile` while preserving `TrainingResult.profiles` compatibility summaries.
- Update package exports intentionally and keep base imports dependency-light.
- Add unit, contract, and package tests for validation, primitive serialization, import boundaries, and backwards compatibility.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_events.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_results.py` | Validate shared record construction, invalid inputs, serialization, timestamps, event logs, span summaries, rank/process metadata, and result attachment. | yes |
| `uv run pytest tests/contracts/test_stage12_observability_contract.py` plus new Stage 15 contract tests if added | Prove Stage 12 compatibility and Stage 15 observability contract. | yes |
| `make test-package` | Prove no heavy imports or accidental public exports. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: old and new event phases validate; `TrainingProfile` contains timestamped event logs, scalar spans, unavailable span evidence, rank/process metadata, and compatibility summaries without claiming a resource trace schema before Phase 3.
- Design-decision evidence: DD-15-1 and DD-15-2 are implemented without breaking Stage 12 observers.
- Future-roadmap/reuse evidence: no backend-specific public profile family exists.
- Example/demo evidence: fake profile examples show event/span alignment and unavailable timing evidence at schema level.
- Documentation evidence: docstrings explain units, timestamps, timeline IDs, sample cadence, dropped samples, and unavailable/unsupported/ambiguous status.
- Scientific contract evidence: timing values are nonnegative, sample ordering is explicit, and synchronization caveats are recorded.

### Phase Workflow State

- Phase execution plan: complete in
  `docs/roadmap/stage-15/phases/core-timeline-profile-records.md`
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped record-shape refinements
- PR review budget: schema/API review
- Blocker-resolution budget: stop and reopen planning only if profile data cannot stay primitive or engine-neutral
- Pre-submit blocker gate: no heavy imports, no raw framework payloads, no breaking Stage 12 event values
- Merge record: recorded below

### Risks And Stop Conditions

- Risks: profile schema breadth, timestamp semantics churn, result-schema compatibility, and hidden import regressions.
- Stop conditions: implementation requires raw backend timelines, framework objects in public records, or a non-additive event migration.
- Assumptions: provisional additive records can cover native, Lightning, future engines, and data-path producers without a registry.

### Completion Summary

- Implementation: complete in PR #95; added additive event phases and
  timestamp/timeline metadata, append-only event logs, scalar spans,
  unavailable evidence, `TrainingProfile`/recorder, and optional
  `TrainingResult.training_profile`.
- Validation: targeted unit/contract/package checks passed; `uv lock --check`,
  `make test-summary`, `make validate-pr`, and `git diff --check` passed.
- PR: [#95](https://github.com/samcantrill/rphys/pull/95) opened against
  `develop` and merged.
- Merge: merged to `develop` on 2026-05-18 with squash commit
  `4af785a40c5e0fb7791afe5a2b897fb50d53ad13`.
- Follow-up: Phase 2 owns probe/checkpoint/policy contracts; Phase 3 owns
  concrete resource trace records and profile persistence.

### Merge Record

## Merge Facts

- Phase: Phase 1, `core-timeline-profile-records`
- Branch: `agent/stage-15-training-profiling-p1-core-timeline-profile-records`
- PR: [#95](https://github.com/samcantrill/rphys/pull/95)
- Base branch: `develop`
- Merge command: `gh pr merge 95 --squash --delete-branch --subject "Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 1: Core Timeline And Profile Records"`
- Merge result: merged; GitHub reported no CI checks for the branch, with
  local `make validate-pr` and `make test-summary` passing before merge.
- Merge commit: `4af785a40c5e0fb7791afe5a2b897fb50d53ad13`
- Branch cleanup: local branch and remote branch deleted after merge.
- Worktree cleanup: Phase 1 worktree removed and `git worktree prune` completed.

## Completion Summary

- Behavior implemented: additive event phases and timeline metadata,
  append-only event logs, scalar spans, unavailable evidence, immutable
  primitive-inspection-friendly profile mappings, `TrainingProfile` recorder,
  and optional `TrainingResult.training_profile`.
- Tests and validation: targeted event/profile/result unit tests passed
  (18 passed); targeted Stage 12/15 observability/result/profile contracts
  passed (10 passed); `make test-package` passed (72 passed);
  `uv lock --check`, `make test-summary` (1043 passed), `make validate-pr`,
  and `git diff --check` passed.
- Documentation: phase execution plan and PR body artifacts were added under
  `docs/roadmap/stage-15/phases/`.
- Scientific contract implications: timing values reject non-finite/negative
  values; event-log ordering is explicit through sequence ids; timestamp and
  clock metadata remain descriptive and do not claim cross-process global
  ordering; no raw framework/resource/probe/checkpoint payloads were added.
- Follow-up notes for later phases: Phase 2 adds probe/checkpoint/policy
  contracts; Phase 3 adds concrete resource traces/profile persistence.

## Implementation Plan Update

- Phase status: `merged`
- Completion summary recorded: yes
- Validation evidence recorded: yes
- Remaining blockers: none for Phase 1; Phase 6/7 Lightning and fixture
  preflights remain phase-local.
- Metadata commit: direct `develop` metadata commits recorded merge and cleanup.

## Phase 2: Probe, Checkpoint, Pipeline, And Policy Contracts

Status: merged
Slug: `probe-checkpoint-policy-contracts`
Branch: `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
PR: [#96](https://github.com/samcantrill/rphys/pull/96)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: define engine-neutral contracts for probes, checkpoint catalogs/restart selection, data-pipeline hook stages, and optimization policies before wiring any engine.
- Files/modules owned: new or updated `src/rphys/training/probes.py`, `src/rphys/training/checkpoint.py`, `src/rphys/training/policies.py`, selected package exports, probe/checkpoint/policy unit and contract tests.
- Behavior implemented: `Probe`, `ProbePolicy`, `ProbeHookPoint`, model/data probe output records, pipeline-stage names, `CheckpointPolicy`, `CheckpointRef`, `CheckpointCatalog`, restart selectors, checkpoint save/restore/prune result records, and primitive precision/compile/kernel policy records.
- Decisions applied: DD-15-3, DD-15-5, and the expanded probe/checkpoint refinements.
- Future-roadmap/reuse constraints: probes and checkpoint selectors are engine-neutral records; engines provide hook contexts and execution bridges. rphys records checkpoint evidence but does not become an artifact store.
- Examples or demos covered: gradient norm probe record, batch NaN probe record, pre-cache/post-cache stage record, keep-last retention, best metric selection, rewind two epochs, unsupported policy evidence.
- Out of scope: native loop wiring, Lightning adapter, real checkpoint writer, real tensor inspection, resource sampler processes, data-path producers.
- Dependencies: Phase 1.

### Tasks

- Add generic probe records with cadence, selectors, hook point, attribution, overhead, unavailable/unsupported evidence, and failure policy.
- Add model-analysis records for parameter, gradient, update, activation, NaN/Inf, zero fraction, and selector-level summaries without raw tensor capture by default.
- Add data-analysis records for field presence, masks, labels/targets, NaN/Inf, shape, dtype, device, value distributions, provenance, and pre/post-device-transfer evidence.
- Add stable data-pipeline stage names over Stage 9 `SampleSource`, cache, prepared, streaming, loader, collation, augmentation, processing, and device-transfer boundaries.
- Add checkpoint catalog, retention, prune, restart selector, and selection evidence records for latest, best, rewind epoch/step, final, failure, before/after timestamp, and explicit ref.
- Add precision, compile, and kernel policy records with requested/applied/fallback/unsupported state.
- Add serialization, invalid input, and import-boundary tests.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_probes.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_policies.py` | Validate probe, checkpoint, restart, and policy records. | yes |
| New Stage 15 contract tests for probe/checkpoint/pipeline policy records | Validate primitive serialization and stable hook/stage names. | yes |
| `make test-package` | Prove new public contracts stay import-light. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: generic probes, checkpoint selectors, data-pipeline stages, and policies validate independently of Native or Lightning.
- Design-decision evidence: checkpoint/restart remains catalog and hook based, not artifact-store based.
- Future-roadmap/reuse evidence: Native, Lightning, and future engines can invoke the same probe and checkpoint policy records.
- Example/demo evidence: fake records show gradient analysis, batch-quality diagnostics, pre/post-cache probes, best/latest/rewind checkpoint selection, and unsupported policies.
- Documentation evidence: docstrings explain hook points, selectors, cadence, stage names, retention semantics, and policy fallback.
- Scientific contract evidence: raw tensor/batch capture is explicitly out of default behavior.

### Phase Workflow State

- Phase execution plan: complete in
  `docs/roadmap/stage-15/phases/probe-checkpoint-policy-contracts.md`
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped
  post-implementation and PR-review blocker refinements
- PR review budget: completed; automated review blockers resolved
- Blocker-resolution budget: 2/3 used for Phase 2 contract refinements
- Pre-submit blocker gate: passed; no default artifact store, no mandatory
  monitor process, no hidden datasource import
- Merge record: recorded below

### Risks And Stop Conditions

- Risks: selector/cadence ambiguity, checkpoint-selection ordering, policy fallback drift, and hook interface ambiguity.
- Stop conditions: checkpoint/restart contracts require framework-specific serialization in core, or probe records require raw tensor/batch payload capture by default.
- Assumptions: fake probe records and fake checkpointers can validate contracts without optional dependencies.

### Completion Summary

- Implementation: complete in PR #96; added dependency-light probe,
  checkpoint, restart-selection, pipeline-stage, and optimization-policy
  records with public exports and primitive/dataclass inspection tests.
- Validation: targeted Phase 2 unit/contract/package checks passed;
  `make test-package`, `uv lock --check`, `git diff --check`,
  `make test-summary`, and `make validate-pr` passed.
- PR: [#96](https://github.com/samcantrill/rphys/pull/96) opened against
  `develop` and merged.
- Merge: merged to `develop` on 2026-05-18 with squash commit
  `5f1c65b01e70965c5798c3b8f30fe1b7c97fa55b`.
- Follow-up: Phase 3 owns concrete resource traces and profile persistence;
  Phase 4 owns Native loop/checkpoint/probe wiring.

### Merge Record

## Merge Facts

- Phase: Phase 2, `probe-checkpoint-policy-contracts`
- Branch: `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- PR: [#96](https://github.com/samcantrill/rphys/pull/96)
- Base branch: `develop`
- Merge command: `gh pr merge 96 --squash --delete-branch --subject "Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 2: Probe, Checkpoint, Pipeline, And Policy Contracts"`
- Merge result: merged; GitHub reported no CI checks for the branch, with
  local `make validate-pr` and `make test-summary` passing before merge.
- Merge commit: `5f1c65b01e70965c5798c3b8f30fe1b7c97fa55b`
- Branch cleanup: local and remote Phase 2 branches deleted after merge.
- Worktree cleanup: Phase 2 worktree removed and `git worktree prune` completed.

## Completion Summary

- Behavior implemented: provisional engine-neutral probe contracts, model/data
  diagnostic summaries, Stage 9-aligned pipeline stage strings, checkpoint
  refs/catalog selectors, save/restore/prune evidence, restart selection
  semantics, and precision/compile/kernel policy records.
- Tests and validation: targeted Stage 15 profile/probe/checkpoint/policy
  checks passed (27 passed before PR); focused post-review checks passed (94
  passed); `make test-package` passed (72 passed); `uv lock --check`,
  `git diff --check`, `make test-summary`, and `make validate-pr` passed.
  Final `make validate-pr` reported package 72, unit 779, contract 187, and
  integration 30 tests passing; e2e and acceptance suites were not present.
- Documentation: phase execution plan and PR body artifacts were added under
  `docs/roadmap/stage-15/phases/`.
- Scientific contract implications: probe and checkpoint records remain
  primitive and dataclass-inspectable; checkpoint selection ordering is
  deterministic; disabled checkpoint policies are explicit no-op records; no
  checkpoint IO, artifact store, raw tensor/batch payload, datasource runtime
  import, Native wiring, or Lightning wiring was added.
- Follow-up notes for later phases: Phase 3 adds resource traces/profile
  persistence; Phase 4 invokes these records from Native checkpoint/probe
  hooks; Phase 5 maps Stage 9 producers to the locked pipeline-stage strings.

## Implementation Plan Update

- Phase status: `merged`
- Completion summary recorded: yes
- Validation evidence recorded: yes
- Remaining blockers: none for Phase 2; Phase 6/7 Lightning and fixture
  preflights remain phase-local.
- Metadata commit: direct `develop` metadata commits recorded merge and cleanup.

## Phase 3: Resource Monitoring And Profile Persistence

Status: merged
Slug: `resource-monitoring-profile-persistence`
Branch: `agent/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`
PR: [#97](https://github.com/samcantrill/rphys/pull/97)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement reusable resource trace records, fake resource profilers, monitor lifecycle records, and asynchronous profile persistence contracts.
- Files/modules owned: `src/rphys/training/profiling.py` or focused helpers, async writer/profiler tests, package/import tests.
- Behavior implemented: `ResourceSample`, `ResourceTrace`, resource metric taxonomy, fake GPU/CPU/memory/disk/network probes, sampler execution modes, background thread/process lifecycle evidence, bounded buffering, dropped samples, backpressure, clock alignment, and async writer flush/failure records.
- Decisions applied: DD-15-2 and expanded resource-monitoring refinements.
- Future-roadmap/reuse constraints: resource profilers are engine-neutral and optional; no psutil, NVML, torch, CUDA, Lightning, network, or GPU dependency in default imports/tests.
- Examples or demos covered: GPU idle due to data queue starvation, disk IO pressure, memory pressure, unavailable probe, dropped samples, async flush lifecycle.
- Out of scope: Native wiring, Lightning wiring, real hardware dependency, daemon/scheduler behavior, artifact store.
- Dependencies: Phases 1-2.

### Tasks

- Add resource sample/trace records with metric kind, unit, value, timestamp, device/process/rank attribution, sample cadence, source probe id, and unavailable/ambiguous status.
- Add resource probe protocols and fake probe implementations for deterministic CPU-only tests.
- Add fake background thread/process sampler contracts with start/stop/failure/backpressure/orphan-cleanup evidence.
- Add async profile writer contracts with bounded buffers, flush cadence, step/epoch/run flush points, failure records, and disabled/no-op fast path.
- Add import-boundary tests that optional system/GPU profilers remain lazy.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Focused resource/profiling unit tests | Validate resource traces, fake probes, background samplers, dropped samples, and async writer records. | yes |
| `make test-package` | Validate optional probe dependencies stay lazy. | yes |
| Optional resource-probe acceptance marker if implemented | Validate real probes only when safe and installed. | no |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: fake resource profilers emit timestamped traces and unavailable/dropped/backpressure evidence.
- Design-decision evidence: monitor processes remain optional, run-scoped, bounded, and lifecycle-bound.
- Future-roadmap/reuse evidence: Native, Lightning, and future engines can start/stop the same resource monitor components.
- Example/demo evidence: fake traces cover GPU idle, disk pressure, memory pressure, unavailable probes, and async flush.
- Documentation evidence: metric kinds, units, sampling cadence, overhead, clock alignment, and probe health are documented.
- Scientific contract evidence: no machine-speed thresholds and no hidden optional dependencies.
- Merge evidence: PR #97 squash-merged to `develop` on 2026-05-18 at
  `d0569b060d5ab4b1b5a81e13d98ea20ba945bdb6` after review blocker
  resolution.
- Validation evidence: `make test-package` passed (72 tests), `make test-unit`
  passed (788 tests), `make test-contract` passed (187 tests),
  `make test-summary` passed (package 72, unit 788, contract 187,
  integration 30; e2e/acceptance not present), `make validate-pr` passed,
  `uv lock --check` passed, and `git diff --check` passed.

## Phase 4: Native Engine Observability And Checkpoints

Status: merged
Slug: `native-engine-observability-checkpoints`
Branch: `agent/stage-15-training-profiling-p4-native-engine-observability-checkpoints`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p4-native-engine-observability-checkpoints`
PR: [#98](https://github.com/samcantrill/rphys/pull/98)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: make Native the reference integration for the shared observability, probe, resource, checkpoint, and restart contracts.
- Files/modules owned: `src/rphys/training/backend.py`, `src/rphys/training/plan.py`, `src/rphys/training/results.py`, native unit/integration tests.
- Behavior implemented: native setup/teardown, event logs, scalar spans, data wait, device transfer, learner step, objective validation, backward, optimizer, scheduler, validation, callbacks, profile summary, resource monitor lifecycle, async writer flush, checkpoint save/restore/prune, catalog updates, restart selection, model probes, data probes, and teardown-after-failure evidence.
- Decisions applied: DD-15-1 through DD-15-3 and expanded probe/checkpoint refinements.
- Future-roadmap/reuse constraints: Native proves the shared records without owning artifact lifecycle, generic serialization, workflow scheduling, or storage backends.
- Examples or demos covered: native whole-path profile, callback failure, keep-last retention, latest/best/rewind resume, gradient/update norm probe, batch quality probe, fake monitor process.
- Out of scope: Lightning, real GPU/system probes, default checkpoint writer, artifact store, scheduler/runtime.
- Dependencies: Phases 1-3.

### Tasks

- Extend `TrainingPlan` only with explicit typed hooks/policies; avoid generic `engine_config`.
- Wrap native loop regions with recorder spans and timestamped events.
- Start/stop resource monitors and async writers around run setup/teardown/failure.
- Invoke model/data probes at native-owned hook points with fake tests.
- Add structural checkpointer hook/protocol support with save/restore/prune and catalog update evidence.
- Resolve restart selectors against checkpoint catalogs before native execution.
- Preserve fail-loud observer behavior and best-effort teardown after setup starts.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_checkpoint.py` | Validate native wiring, checkpoint hooks, restart selectors, and failure behavior. | yes |
| Native Stage 15 integration tests | Validate synthetic native success/failure, profile attachment, fake monitors, async writer, probes, and checkpoint/resume evidence. | yes |
| `make test-package` | Prove native training core stays import-light. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: native `Trainer.fit` returns `TrainingResult.training_profile` with lifecycle events, spans, resource traces, model/data probes, checkpoint catalog/retention/restart evidence, and teardown-after-failure evidence.
- Design-decision evidence: Native uses shared contracts rather than native-only profile/checkpoint families.
- Future-roadmap/reuse evidence: future engines can match records without copying native internals.
- Example/demo evidence: native examples show data wait, transfer, checkpoint stall, rewind resume, model probes, data probes, and unavailable monitor cases.
- Documentation evidence: Native docs explain owned hook points and checkpoint serialization boundary.
- Scientific contract evidence: profiling does not change learner semantics or output-spec validation.
- Merge evidence: PR #98 squash-merged to `develop` on 2026-05-18 at
  `1e8a780ce2b798b6cc90a2d920529e7f3f2b31e2` after automated review blocker
  resolution.
- Validation evidence: focused Phase 4 suite passed (63 tests),
  `make test-package` passed (72 tests), `make test-unit` passed (794 tests),
  `make test-contract` passed (187 tests), `make test-integration` passed
  (31 tests), `make test-summary` passed (package 72, unit 794, contract 187,
  integration 31; e2e/acceptance not present), `make validate-pr` passed,
  `uv lock --check` passed, and `git diff --check` passed.

## Phase 5: Data-Path Pipeline Probes And Batch Evidence

Status: pending
Slug: `datapath-pipeline-probes-batch-evidence`
Branch: `agent/stage-15-training-profiling-p5-datapath-pipeline-probes-batch-evidence`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p5-datapath-pipeline-probes-batch-evidence`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: extend diagnosis beyond the training loop using Stage 9 source/cache/prepared/data-path contracts and existing BatchOperation evidence.
- Files/modules owned: `src/rphys/datasources/datapath.py` or sibling helpers, Stage 9 source/cache/prepared tests, `src/rphys/ops/batch.py` tests/docs as needed.
- Behavior implemented: stable pipeline-stage probe contexts, synthetic data-path profile/benchmark producers, reserved measurement keys, fake data probes, IO/decode/cache/prepared/augment/collate/queue/device-transfer evidence, and BatchOperation equivalence/replay/provenance validation.
- Decisions applied: DD-15-6 and DD-15-7.
- Future-roadmap/reuse constraints: no competing dataset abstraction, no storage backend, no implicit cache, no speed thresholds.
- Examples or demos covered: `Process -> Cache -> Augment -> Process`, `Load from cache/prepared -> Augment -> Process`, data queue starvation, IO/decode/collate bottleneck, batch NaNs, mask issues, BatchOperation equivalence.
- Out of scope: concrete optimized storage backend, raw-data benchmark, auto-vectorizer, backend execution planner.
- Dependencies: Phases 1-3; can proceed in parallel with Phase 4 after shared contracts merge.

### Tasks

- Add stable data-pipeline stage names and hook context records over Stage 9 `SampleSource`, `CachedSampleSource`, `PreparedSampleSource`, `StreamingReadPlan`, and `DataLoaderState` evidence.
- Add data-path profiling helpers that output existing `DataPathProfile`/`DataPathBenchmark` compatible evidence.
- Define reserved measurement keys and units for decode, collate, queue, worker, disk, network, bytes, throughput, device transfer, synchronization, and unavailable evidence.
- Add fake data probes for NaN/Inf detection, missing fields, mask validity, label distribution, shape/dtype/device drift, and provenance anomalies.
- Add examples for pre-cache/post-cache/pre-augmentation/post-augmentation/final-processing/collation/device-transfer probe placement.
- Add BatchOperation equivalence/replay/provenance/mask/alignment/dtype/device validation examples.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/contracts/test_data_path_records_contract.py` | Validate data-path record compatibility and serialization. | yes |
| `uv run pytest tests/integration/test_stage9_data_path_flow.py` or new Stage 15 data-path tests | Validate synthetic pipeline-stage and profile/benchmark producers. | yes |
| Focused BatchOperation contract/integration tests | Validate scientific equivalence and failure behavior. | yes |
| `make test-package` | Validate datasource/batch additions do not introduce heavy imports or training-core dependencies. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: data-path benchmarks and probes identify source/cache/prepared/decode/collate/queue/disk/network/throughput evidence, pipeline-stage provenance, and data-quality issues.
- Design-decision evidence: Stage 15 reuses Stage 9 descriptors rather than adding a competing dataset abstraction.
- Future-roadmap/reuse evidence: future storage adapters can emit comparable stage evidence.
- Example/demo evidence: examples cover both process-cache and cache/prepared-load flows.
- Documentation evidence: stage names, reserved keys, units, and attribution limitations are documented.
- Scientific contract evidence: BatchOperation evidence preserves masks, alignment, dtype/device, provenance, and replay semantics.

## Phase 6: Lightning API And Policy Foundation

Status: pending
Slug: `lightning-api-policy-foundation`
Branch: `agent/stage-15-training-profiling-p6-lightning-api-policy-foundation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p6-lightning-api-policy-foundation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add the optional public Lightning surface and policy mapping without yet taking on the full observability bridge.
- Files/modules owned: `src/rphys/training/lightning.py`, `src/rphys/training/policies.py` refinements if needed, fake-Lightning tests, import/security tests.
- Behavior implemented: lazy import/security preflight, `LightningTrainingEngine`, shared `Trainer`/`TrainingEngine` path for rphys `Learner`/`TrainingPlan`, LightningModule/DataModule or dataloader entrypoints, trainer kwargs boundary, precision/compile/kernel policy mapping, absent/unsafe dependency diagnostics.
- Decisions applied: DD-15-4 and DD-15-5.
- Future-roadmap/reuse constraints: Lightning-specific inputs stay isolated to `rphys.training.lightning`; outputs stay shared `TrainingResult`/`TrainingProfile` records.
- Examples or demos covered: `Trainer(engine=LightningTrainingEngine)`, direct LightningModule/DataModule entrypoint, policy mapping, absent/unsafe dependency.
- Out of scope: full callback/profiler/checkpoint/probe bridge, full distributed/private-state parity, base Lightning dependency.
- Dependencies: Phases 1-2; refresh official Lightning docs/security before code work.

### Tasks

- Add Lightning package/version preflight and unsafe/absent dependency diagnostics.
- Implement optional `LightningTrainingEngine` for the shared engine path.
- Implement explicit Lightning-native public entrypoints under `rphys.training.lightning`.
- Map precision, compile, and kernel policies to public Lightning settings where available and record unsupported/fallback state.
- Add package/import checks proving base `rphys.training` imports do not load Lightning, torch, CUDA/NVML, or system profilers.
- Add fake-Lightning tests for public API shape, learner-wrapper path, Lightning-native path, policy mapping, trainer kwargs boundary, and dependency diagnostics.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Fake-Lightning focused tests | Validate API shape without installing Lightning. | yes |
| `uv run pytest tests/unit/rphys/training/test_policies.py` | Validate policy mapping and unsupported/fallback diagnostics. | yes |
| `make test-package` | Validate optional imports remain isolated. | yes |
| Optional installed-Lightning smoke when safe | Validate against current public Lightning APIs. | no |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: Lightning API foundation can run fake tests and returns shared rphys records.
- Design-decision evidence: Lightning remains optional/import-gated and does not create Lightning-specific output families.
- Future-roadmap/reuse evidence: future engine adapters can follow the same optional-module pattern.
- Example/demo evidence: examples show rphys learner path, Lightning-native path, and policy mapping.
- Documentation evidence: docs explain dependency/security preflight and unsupported boundaries.
- Scientific contract evidence: precision/compile/kernel policies record requested/applied/fallback state.

## Phase 7: Lightning Observability, Checkpoint, And Probe Bridges

Status: pending
Slug: `lightning-observability-checkpoint-bridges`
Branch: `agent/stage-15-training-profiling-p7-lightning-observability-checkpoint-bridges`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p7-lightning-observability-checkpoint-bridges`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: translate Lightning lifecycle, profiler, checkpoint, rank, model/data probe, resource monitor, and async writer behavior into shared rphys records.
- Files/modules owned: `src/rphys/training/lightning.py` bridge internals, fake-Lightning integration tests, optional acceptance tests.
- Behavior implemented: Lightning callback/profiler bridge, event-log normalization, rank/device attribution, resource monitor lifecycle, checkpoint retention/pruning mapping, restart selector to `ckpt_path` behavior, custom rphys profiler/probe composition, model/data probe bridge, async writer interaction.
- Decisions applied: DD-15-4 plus expanded observability/checkpoint/probe refinements.
- Future-roadmap/reuse constraints: reuse shared rphys records; do not expose raw Lightning trainer state or private callback internals as public contract.
- Examples or demos covered: DDP-style rank attribution, best-k checkpoint mapping, keep-last recency pruning bridge, latest/best/rewind resume, gradient probes, data probes, resource probes under Lightning.
- Out of scope: base dependency, full distributed/private-state parity, private trainer-state parsing.
- Dependencies: Phases 1-3 and 6.

### Tasks

- Map Lightning callbacks/profiler/checkpoints/`ckpt_path` into shared rphys event logs, span records, resource traces, checkpoint records, and policy records.
- Ensure custom rphys resource profilers can run alongside Lightning DDP/precision/torchmetrics behavior with rank-aware attribution.
- Map `CheckpointPolicy` best-k and periodic schedules to public Lightning `ModelCheckpoint` settings where possible.
- Add rphys retention/pruning bridge for recency policies that Lightning does not provide directly.
- Resolve restart policies against a checkpoint catalog and pass the selected ref through public Lightning resume behavior.
- Add model-analysis bridge coverage for gradient and parameter statistics at public backward/optimizer hooks.
- Add data-analysis bridge coverage for batch quality and post-transfer statistics at public batch lifecycle hooks or rphys adapter-owned normalization points.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Fake-Lightning bridge tests | Validate callback/profile/checkpoint/probe/resource mapping without installing Lightning. | yes |
| Optional installed-Lightning acceptance when safe | Validate against current Lightning public APIs. | no |
| `make test-package` | Validate import boundaries remain intact. | yes |
| `git diff --check` | Catch whitespace issues. | yes |

### Acceptance Evidence

- Behavior evidence: Lightning paths return shared rphys results/profiles/event logs/checkpoints/policies with custom profilers, checkpoint retention/catalog/restart selection, model probes, and data probes.
- Design-decision evidence: Lightning-specific behavior is normalized into shared records.
- Future-roadmap/reuse evidence: future adapters can bridge framework callbacks the same way.
- Example/demo evidence: fake examples cover rank attribution, recency pruning, `ckpt_path`, probes, resource monitors, and async writer flush.
- Documentation evidence: docs explain supported public hooks and unsupported private/distributed boundaries.
- Scientific contract evidence: no raw Lightning timelines, trainer internals, tensors, or checkpoint payloads enter public records.

## Phase 8: Tiers, Documentation, And Final Hardening

Status: pending
Slug: `tiers-docs-final-hardening`
Branch: `agent/stage-15-training-profiling-p8-tiers-docs-final-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p8-tiers-docs-final-hardening`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: close the public contract with descriptive tiers/restart snapshots, docs, examples, import/security checks, and broad validation.
- Files/modules owned: tier/restart record modules if still needed, docs/docstrings/examples touched by prior phases, package/export checks, final validation artifacts.
- Behavior implemented: `ExperimentTierSpec` or equivalent descriptive tier records, restart snapshots linked to checkpoints/profile/data-path evidence, docs for all public records and examples, broad validation evidence, revisit triggers.
- Decisions applied: DD-15-8 plus final obligations from all prior phase decisions.
- Future-roadmap/reuse constraints: tiers are descriptive evidence only; downstream/`loom` may orchestrate using them, but rphys does not schedule work or manage artifacts.
- Examples or demos covered: debug/smoke/signal/comparison/full tier descriptors and complete Native/Lightning/data-path examples.
- Out of scope: workflow scheduler, cost dashboard, artifact lifecycle, alternate fake execution path, new behavior beyond accepted scope.
- Dependencies: Phases 1-7.

### Tasks

- Add descriptive tier/restart records if not completed by earlier checkpoint work.
- Link restart evidence to checkpoint refs, loader/materialization fingerprints, profile summaries, completion markers, and compatibility notes.
- Finalize docs/docstrings for event logs, spans, resource traces, probes, data pipeline stages, checkpoint catalog/restart/retention, policies, Native/Lightning bridges, optional dependencies, and Stage 9/12/13 reuse.
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
- Example/demo evidence: public examples cover Native, Lightning, data-path, dataset pipeline stages, resource blind spots, checkpoint/resume/retention/rewind, model/data probes, and tiers.
- Documentation evidence: public records document units, timestamps, event-log semantics, probe semantics, dataset-stage semantics, rank/device naming, monitor lifecycle, async writer behavior, checkpoint catalog/restart/retention behavior, engine-neutral profiler reuse, optional dependency behavior, and unsupported/unavailable cases.
- Scientific contract evidence: no hidden synchronization, no speed thresholds, no raw timelines, no opaque checkpoint payloads, and no altered BatchOperation meaning.

## Cross-Phase Validation

- Full relevant test command: run phase-focused `uv run pytest ...` first, then broaden to `make test-package`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` as scope allows.
- Docs/template checks: ensure all public/provisional records have docstrings covering units, timestamps, sample cadence, resource attribution, unavailable/unsupported/ambiguous status, checkpoint ownership, and optional dependency behavior.
- Scientific/workflow contract checks: no hidden synchronization, no raw framework timeline payloads, no workflow runtime, no artifact store, no speed thresholds, no concrete storage backend, no public helper registry, and no engine-specific output family.
- Example/demo checks: native whole-path profile, Lightning parity, checkpoint/resume/rewind, policy mapping, data-path bottleneck, dataset pipeline-stage probes, optional monitor-process probe, metric blind-spot examples, BatchOperation equivalence, and tier/restart compatibility.
- Manual review focus: import boundaries, provisional public schema breadth, resource monitor lifecycle, checkpoint hook/catalog boundary, restart selection semantics, Lightning adapter isolation, and data-path attribution clarity.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Original five phases became too broad after scope expansion. | concern | Rebalanced into eight phases: core timeline/profile records; probe/checkpoint/policy contracts; resource monitoring/profile persistence; Native integration; data-path/pipeline probes; Lightning API/policy foundation; Lightning observability/checkpoint/probe bridges; final hardening. | resolved in draft |
| Phase 1 trace/profile boundary was ambiguous before `ResourceTrace` exists. | blocker | Phase 1 now explicitly exposes only event-log, scalar-span, decision, summary, and unavailable-evidence helpers; concrete resource trace records and `resource_traces` helpers are deferred to Phase 3 as additive public surface. | resolved by refinement |
| Phase 5 missed package/import-boundary validation despite touching datasource and batch surfaces. | concern | Added required `make test-package` validation and explicit attention to avoiding heavy imports or training-core dependencies. | resolved by refinement |
| Phase 2 copied native/resource workflow wording into contract-only scope. | note | Reworded the PR review budget, risks, and stop conditions around probe/checkpoint/policy contract ownership. | resolved by refinement |
| Resource monitor process support is included without daemon/runtime ownership. | note | Phase 3 validates fake lifecycle and async writer behavior; Phase 4 and Phase 7 integrate it through Native and Lightning; all phases keep monitor process optional and run-scoped. | recorded |
| Lightning acceptance depends on current upstream API/security state. | concern | Phase 6 has a required preflight and optional real acceptance only when dependency is installed and safe; Phase 7 extends acceptance to observability bridges. | open preflight |
| Stage 14 synthetic fixture availability is not assumed. | concern | Phase work can use Stage 9/12 synthetic flows unless Stage 14 fixtures are present in the target branch. | open preflight |
| Dataset/data-pipeline probe hooks must not create a competing dataset interface. | concern | Phase 5 anchors stage hooks to Stage 9 `SampleSource`, cache, prepared, streaming, loader, and data-path records. | recorded |

Gate result:

- Status: passed after startup quality-gate refinement and confirmation review.
- Review evidence: manager re-review on 2026-05-18 after expanded probe, checkpoint, restart, dataset-stage, resource-monitoring, async persistence, and Lightning bridge requirements; startup quality-gate review on 2026-05-18 found one Phase 1 blocker and two nonblocking plan concerns; narrow refinement completed; confirmation review found no remaining blockers.
- Accepted risks: schema may need additive revision after Native/Lightning pressure; optional real probes and installed-Lightning acceptance may be unavailable locally; resource attribution may be ambiguous for system-wide probes; dataset-stage hooks may expose gaps in Stage 9 evidence; checkpoint catalogs may need additive fields after real backend pressure.
- Revisit triggers: Lightning security/API changes; profile schema cannot represent a material metric without opaque payloads; resource monitoring needs daemon/scheduler semantics; data-path reserved keys cannot support attribution; checkpoint hooks require core-owned serialization; dataset pipeline stages require a new concrete dataset abstraction.

## Final Approval

- Approval status: maintainer requested implementation on 2026-05-18; startup workflow confirmation review passed.
- Approved scope: eight-phase Stage 15 implementation plan.
- Accepted risks: schema may need additive revision after Native/Lightning pressure; optional real probes and installed-Lightning acceptance may be unavailable locally; resource attribution may be ambiguous for system-wide probes; dataset-stage hooks may expose gaps in Stage 9 evidence; checkpoint catalogs may need additive fields after real backend pressure.
- Deferred items: concrete optimized storage backend, workflow runtime, artifact store, cost dashboard, automatic tuning, real dataset benchmarks, mandatory hardware acceptance, and full distributed/private-state Lightning parity.

## Startup Quality-Gate Refinement Summary

### Source Review

- Review prompt: `.codex/prompts/implementation-plan-review.md`
- Review date/round: 2026-05-18 startup quality gate
- Blockers addressed: Phase 1 `TrainingProfile` trace/resource-trace boundary.

### Changes

- Phase scope: Phase 1 now defers concrete resource trace record types and `resource_traces` helpers to Phase 3; Phase 2 contract wording now matches probe/checkpoint/policy ownership.
- Acceptance criteria: Phase 1 evidence must not claim a resource trace schema before Phase 3.
- Validation: Phase 5 now requires `make test-package` for datasource/batch import-boundary coverage.
- Scientific contract obligations: raw tensors, raw batches, opaque framework timelines, and resource-monitor scheduler semantics remain out of scope.
- Risks/debt/revisit triggers: no new debt introduced; existing revisit triggers remain.

### Remaining Items

- Blockers: none known after confirmation review.
- Accepted risks: optional Lightning/security and Stage 14 fixture preflights remain phase-local requirements.
- Questions for manager: none.

### Confirmation

- Recommended confirmation review focus: verify the Phase 1 trace/resource-trace boundary is implementation-ready and that the Phase 5 validation and Phase 2 wording updates close the review findings.
- Ready for phase implementation: yes.
