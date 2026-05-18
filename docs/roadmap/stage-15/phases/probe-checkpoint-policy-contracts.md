# Phase 2 Execution Plan: Probe, Checkpoint, Pipeline, And Policy Contracts

## Metadata

- Status: final phase execution plan; expanded-path refinement completed; ready
  for implementation
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Probe, Checkpoint, Pipeline, And Policy Contracts
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 2: Probe, Checkpoint, Pipeline, And Policy Contracts`
- Branch: `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- Phase execution plan path: `docs/roadmap/stage-15/phases/probe-checkpoint-policy-contracts.md`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Planning document: `docs/roadmap/stage-15/planning.md`
- Source phase: `docs/roadmap/stage-15/implementation-plan.md`, `## Phase 2: Probe, Checkpoint, Pipeline, And Policy Contracts`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation plan approved; expanded-path detail covers
  public provisional probe/checkpoint/restart/policy schema, primitive
  serialization and dataclass inspection, Stage 15 Phase 1 compatibility,
  import boundaries, checkpoint catalog and restart selector semantics,
  pipeline-stage naming over Stage 9, precision/compile/kernel fallback
  evidence, and explicit future-phase exclusions
- Draft pass: complete
- Refine pass: complete; limited to the assigned expanded-path triggers
- Setup limitations: existing manager-created worktree was verified instead of
  creating a new branch/worktree; no fetch, push, or PR action was performed in
  this planning pass
- Blockers: none

## Objective

Define dependency-light, engine-neutral contracts for training probes,
checkpoint catalogs and restart selection, pipeline-stage hook names, and
precision/compile/kernel policies before any engine, Lightning, resource
sampler, checkpoint writer, or data-path producer is wired. The phase should
produce public provisional records that are primitive- and
dataclass-inspection-friendly, validated, import-light, and specific enough for
later phases to invoke without redesign.

## Full-Plan Context

Phase 1 has already added timestamped training events, event logs, scalar spans,
unavailable evidence, `TrainingProfile`, and optional result profile
attachment. Phase 2 defines the policy and diagnostic records that later phases
will populate. Phase 3 adds resource traces and profile persistence; Phase 4
wires Native observability and checkpoint hooks; Phase 5 connects Stage 9
data-path producers and batch evidence; Phase 6 maps optimization policies into
the optional Lightning API foundation; Phase 7 bridges Lightning callbacks,
checkpoints, probes, and resources; Phase 8 finalizes docs, tiers, and broad
validation.

This phase must stay contract-only. It should make later wiring possible, but
it must not perform tensor inspection, checkpoint IO, native loop integration,
Lightning integration, resource sampling, profile persistence, data-path
benchmark production, or datasource runtime changes.

The Phase 2 records should reference Phase 1 run/timeline/event/profile
identifiers by value only. They must preserve the Phase 1 `TrainingEvent`,
`TrainingEventLog`, `TrainingProfile`, and `TrainingResult.training_profile`
contracts and must not add Phase 3 resource-trace/profile-persistence
containers, Native execution hooks, Lightning adapter behavior, or Stage 9
datasource imports to those core records.

## Source Phase Summary

- Goal: define engine-neutral contracts for probes, checkpoint
  catalogs/restart selection, data-pipeline hook stages, and optimization
  policies before wiring any engine.
- Required scope: new or updated `src/rphys/training/probes.py`,
  `src/rphys/training/checkpoint.py`, `src/rphys/training/policies.py`,
  selected package exports, and probe/checkpoint/policy unit and contract tests.
- Required checkpoints: add generic probe records and policies; add model and
  data probe output records; lock stable pipeline-stage names aligned to Stage
  9; add checkpoint policies, refs, catalogs, save/restore/prune result
  evidence, restart selectors, and selection evidence; add primitive
  precision, compile, and kernel policy records.
- Acceptance criteria: generic probes, checkpoint selectors, data-pipeline
  stages, and optimization policies validate independently of Native,
  Lightning, real checkpoint writers, real tensor inspection, resource sampler
  processes, or data-path producers; records remain primitive,
  dataclass-inspectable, Phase 1 compatible, and import-light.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/training/events.py`, `profiling.py`, `results.py`, and
  `__init__.py` now contain the Phase 1 observability substrate. No
  `src/rphys/training/probes.py`, `checkpoint.py`, or `policies.py` module
  exists yet in this worktree.
- Existing validation helpers: `src/rphys/training/_validation.py` provides
  primitive mapping, non-empty string, non-negative integer, positive integer,
  and tuple coercion helpers that should be reused where they fit.
- Existing checkpoint surface: `TrainingResult.checkpoint_id` is a primitive
  compatibility field only. Phase 2 should not replace it, make it a storage
  contract, or require `TrainingResult` changes unless a narrowly scoped
  additive compatibility helper is unavoidable.
- Existing Phase 1 inspection behavior: Stage 15 profile/event/result records
  are frozen dataclasses that are inspected with `dataclasses.asdict` in unit
  and contract tests. Phase 2 public records should follow that pattern or
  provide equally simple dataclass inspection; they must not require a custom
  serializer to expose primitive evidence.
- Existing data-path constraints: Stage 9 owns `SampleSource`,
  `IndexSampleSource`, `CachedSampleSource`, `PreparedSampleSource`,
  `StreamingReadPlan`, `DataLoaderState`, `DataPathProfile`, and
  `DataPathBenchmark`. Phase 2 should align string stage names to those
  concepts without importing `rphys.datasources` from base training modules.
- Existing tests or harness behavior: package tests pin public exports and
  import boundaries; unit tests mirror `src/rphys/training`; contract tests
  already include Stage 12 and Stage 15 observability/profile behavior plus
  Stage 9 data-path record compatibility.
- Import-boundary or dependency constraints: base `rphys.training` imports must
  not load `rphys.datasources`, Lightning, torch, JAX, CUDA/NVML, system
  profilers, numpy, pandas, scipy, plotting/video libraries, logging backends,
  or `tests.support`.

## Phase Isolation State

- Control checkout dirty-state review: reviewed `/home/samcantrill/work/rphys`;
  it was clean on `develop...origin/develop`.
- Dedicated branch/worktree status: verified clean worktree at
  `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
  on `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`.
- Current `develop` base: worktree `HEAD`, local `develop`, and
  `origin/develop` all resolved to
  `f523b9a08e5c6bd70dbd7552ad458cd41b4b7d58`.
- Earlier phase dependency status: Phase 1 is recorded as merged in
  `docs/roadmap/stage-15/implementation-plan.md`.
- Push/PR infrastructure status: not exercised during this plan-only pass; the
  implementation workflow should verify `gh auth status` before opening the
  PR.
- Stop condition if isolation cannot be maintained: stop before editing product
  code if this branch diverges from `develop`, the worktree is dirty with
  unrelated edits, or another Stage 15 phase starts writing into this worktree.

## In-Scope Work

- Add `src/rphys/training/probes.py` with engine-neutral probe contracts:
  structural probe protocol or callable shape, hook-point vocabulary, cadence
  records, selectors, attribution requirements, failure policy, unavailable or
  unsupported evidence, and primitive output records.
- Define generic hook points for engine-owned lifecycle regions without
  changing engine behavior. Required coverage includes setup, teardown,
  failure, epoch/step boundaries, data wait or batch fetch, pre/post device
  transfer, forward/objective/backward/optimizer/scheduler boundaries,
  validation, checkpoint, callback, and generic pipeline-stage evidence.
- Define stable pipeline-stage names for later Stage 9 integration. Required
  names include `indexed`, `pre_cache_processing`, `cache_lookup`,
  `cache_hit_load`, `cache_miss_source_read`, `cache_write`,
  `prepared_read`, `pre_augmentation`, `post_augmentation`,
  `post_processing`, `collate`, `pre_device_transfer`,
  `post_device_transfer`, and `learner_output_validation`.
- Ensure pipeline-stage records can represent both planned flows:
  `Process -> Cache -> Augment -> Process` and
  `Load from cache/prepared -> Augment -> Process`. Records should carry source
  versus cache versus prepared/materialized evidence through primitive
  fingerprints and metadata, not live datasource objects.
- Add model-analysis record types for parameter, gradient, update, activation,
  NaN/Inf, zero-fraction, saturation/clipping, selector, rank/device, cadence,
  aggregation, and unavailable evidence. These records store summaries only by
  default and must not capture raw tensors, optimizer state, modules, or
  framework objects.
- Add data-analysis record types for field presence, masks, labels/targets,
  NaN/Inf, shape, dtype, device, value distributions, provenance, stage,
  pre/post device-transfer context, and unavailable evidence. These records
  store primitive summaries only and must not capture `Sample`, `Batch`,
  `FieldRef`, dataloader, or dataset objects.
- Add `src/rphys/training/checkpoint.py` with checkpoint refs, policy records,
  catalog/index records, save/restore/prune result evidence, retention reasons,
  restart selectors, and deterministic selection results.
- Cover checkpoint cadence by step, epoch, elapsed time, metric, failure, and
  final checkpoint. Cover retention by recency, best metric, final/failure
  preservation, explicit keep/drop reasons, and unsupported policy evidence.
- Cover restart selection by latest completed, best by metric, N epochs back, N
  steps back, before/after timestamp, failure checkpoint, final checkpoint, and
  explicitly supplied checkpoint ref.
- Ensure checkpoint records describe where and why a checkpoint exists without
  owning artifact storage. Ref locators may be primitive path/URI/id strings,
  but this phase must not open files, write state, delete files, serialize
  backend payloads, or claim a default checkpoint format.
- Add `src/rphys/training/policies.py` with primitive precision, compile, and
  kernel policy records. Records should capture requested state, applied state,
  fallback state, unsupported reason, backend applicability, numerical
  equivalence expectations, and primitive provenance.
- Update selected package exports in `src/rphys/training/__init__.py` and
  package tests for only code-backed public names introduced by this phase.
- Add focused unit, contract, and package tests for validation, primitive
  serialization, dataclass inspection, deterministic selector behavior, public
  exports, Phase 1 compatibility, and import boundaries.

## Out-of-Scope Work

- Native loop wiring, probe invocation in `NativeTrainingEngine`, checkpoint
  save/restore/prune hooks, restart execution, callback ordering changes, or
  changes to learner semantics. Those are Phase 4 concerns.
- Optional Lightning module work, Lightning public API foundation, callback or
  profiler bridge implementation, Lightning checkpoint callback mapping,
  `ckpt_path` handling, or installed-Lightning validation. Those are Phase 6
  and Phase 7 concerns.
- Real checkpoint writers/readers/deleters, artifact stores, storage backends,
  generic workflow resume engines, file locks, cloud/object-store behavior, or
  opaque pickle/state serialization. Phase 2 records selectors and evidence
  only.
- Real tensor, module, optimizer, dataloader, `Sample`, `Batch`, or dataset
  inspection. Phase 2 defines records that later bridges can populate, not
  inspectors.
- Resource trace records, resource sampler processes, GPU/CPU/disk/network
  probes, background threads/processes, async profile writers, dropped-sample
  queues, or profile persistence. Those are Phase 3 concerns.
- Data-path benchmark/profile producers, Stage 9 source/cache/prepared runtime
  changes, BatchOperation equivalence additions, raw data fixtures, or
  datasource imports from training core. Those are Phase 5 concerns.
- Performance thresholds, hardware-specific checks, dashboards, schedulers,
  automatic tuning, or project/workflow orchestration.

## Assumptions

- Phase 2 public records are provisional but still code-backed, documented, and
  tested before export.
- Standard-library dataclasses, `StrEnum`, protocols, immutable tuples, and the
  existing training validation helpers are sufficient; no new runtime
  dependency is needed.
- Primitive serialization means records can be inspected or round-tripped
  through nested primitive values, primitive mappings, strings, numbers,
  booleans, `None`, and tuples/lists. It does not mean adding a profile writer,
  artifact schema, checkpoint file format, or JSON persistence backend.
- Dataclass inspection means public record fields are discoverable through
  standard dataclass tools such as `dataclasses.fields` or
  `dataclasses.asdict`, with primitive or nested dataclass leaves. Avoid
  properties-only records, dynamic `__getattr__`, opaque payload bags, and
  required custom serializers for basic inspection.
- Pipeline stage alignment can be represented as stable strings in training
  contracts. Contract tests may compare these names against Stage 9 record
  behavior, but production training modules must not import datasource modules.
- Checkpoint selection can be tested against synthetic `CheckpointRef` records
  and catalogs without a real writer.
- Precision, compile, and kernel policies are descriptive until an engine or
  adapter maps them. Native unsupported evidence and Lightning mapping belong
  to later phases.
- Default validation remains CPU-only, synthetic, deterministic,
  threshold-free, and optional-dependency-free.

## Scope Contract

Public behavior:

- Every exported Phase 2 name is provisional public API. It must be listed
  intentionally, tested, and documented with enough shape and failure behavior
  for downstream experiments to inspect it.
- Public provisional schema must be code-backed. Do not export placeholder
  names, aliases reserved for later phases, or records whose fields are not
  covered by validation and primitive/dataclass inspection tests.
- Probe contracts describe when and what to inspect; they do not inspect real
  tensors or batches in this phase. A probe implementation may be represented
  by an importable object/protocol, but execution is owned by later engine or
  data-path phases.
- Probe cadence must be explicit. Supported cadence evidence should include
  disabled/manual, every N steps, every N epochs, selected hook points, and
  time-based or metric/failure-triggered intent where representable without a
  scheduler. Invalid zero or negative cadence values fail loudly.
- Probe failure policy must be explicit. Supported outcomes should distinguish
  fail-loud behavior, record-and-continue unavailable evidence, unsupported
  evidence, and disabled/no-op behavior. Silent probe disappearance is not
  allowed.
- Hook-point and pipeline-stage vocabularies are stable strings for Stage 15
  integration. Adding names is allowed later, but renaming or repurposing the
  Phase 2 names should require a contract test change and migration note.
- Pipeline-stage names describe Stage 9 concepts by string and primitive
  fingerprints only. Training-core records may name source/cache/prepared,
  request, materialization, operation, split, worker, and rank evidence, but
  production `rphys.training` modules must not import `rphys.datasources` or
  hold `SampleSource`, `CachedSampleSource`, `PreparedSampleSource`,
  `StreamingReadPlan`, `DataLoaderState`, `DataPathProfile`, or
  `DataPathBenchmark` objects.
- Model probe records represent diagnostic summaries. Required attribution
  includes probe id/name, hook point, selector, statistic kind, aggregation,
  run/timeline/process/rank/device where known, and primitive provenance.
- Data probe records represent diagnostic summaries over batch/sample fields or
  pipeline stages. Required attribution includes stage, field/role/locator
  strings where known, shape/dtype/device summaries, split/worker/rank
  fingerprints where known, and primitive provenance.
- Checkpoint policies describe desired save, retention, and restart behavior.
  Engines or adapters perform IO later and return evidence records; the policy
  itself must not open, write, delete, or deserialize anything.
- `CheckpointRef` records identify logical checkpoint evidence with primitive
  locators, stream ids, run ids, epoch/step/timestamp/metric evidence, status,
  rank/process evidence, and provenance. A ref is not an artifact-store object
  and should not hold open handles or backend state.
- `CheckpointCatalog` or equivalent index records are immutable evidence and
  selector input. Catalog operations should be deterministic, must not mutate
  refs in place, and must not scan storage on their own.
- Restart selectors are records, not imperative commands. Resolving a selector
  against a catalog returns a selection/evidence record with the selected ref
  or explicit unavailable/unsupported/no-match reason.
- Catalog selectors must document their eligibility filters and ordering.
  Required examples are latest completed, best by metric, N epochs back, N
  steps back, before/after timestamp, failure checkpoint, final checkpoint, and
  explicit ref. Missing metrics, non-finite metric values, incomplete refs,
  ambiguous stream ids, empty catalogs, and ties must yield deterministic
  selection or explicit no-match/unsupported evidence.
- Restart selectors must record selector kind, requested anchor or metric,
  stream constraint where applicable, inclusive/exclusive timestamp or
  epoch/step behavior, selected checkpoint ref when available, and the
  no-match/fallback reason when unavailable. They must not execute a restart or
  pass engine-specific `ckpt_path`/restore arguments in this phase.
- Save, restore, and prune result records must distinguish attempted,
  completed, skipped, failed, unsupported, and unavailable outcomes with
  retention reason, failure message where relevant, and rank/process evidence.
- Precision, compile, and kernel policies are primitive records. They should
  capture requested values, applied values when known, fallback/unsupported
  state, backend applicability, equivalence or numerical-risk notes, and
  provenance without importing torch, Lightning, CUDA, JAX, Triton, numpy, or
  any compiler/runtime package.

Module boundaries:

- `probes.py` owns probe protocols, hook points, pipeline-stage names, cadence,
  selectors, probe policies, model probe records, data probe records, and
  unavailable/unsupported probe evidence.
- `checkpoint.py` owns checkpoint refs, policies, catalogs, selectors,
  selection evidence, save/restore/prune evidence, retention reasons, and
  restart evidence.
- `policies.py` owns precision, compile, and kernel optimization policy
  records.
- `__init__.py` re-exports only implemented, tested public names. Avoid broad
  wildcard exports and avoid names reserved for later phases.
- Base training modules may import standard-library modules, existing
  lightweight `rphys.training` helpers, `rphys.learning` only where already
  acceptable, and `rphys.errors`. They may not import datasource, torch,
  Lightning, system profiler, plotting, dataframe, video, or test-support
  modules.

Data shapes:

- Records should use frozen dataclass-like or immutable tuple-backed shapes
  consistent with existing training records.
- New public records should be dataclass-inspectable in the same style as
  Phase 1 records, so tests can use `dataclasses.is_dataclass`,
  `dataclasses.fields`, or `dataclasses.asdict` without depending on private
  serializers.
- Primitive mappings must use non-empty string keys and primitive values.
  Nested payload summaries must be represented by explicit record fields or
  documented primitive containers, not arbitrary objects.
- Optional identifiers must be non-empty strings when provided. Counts,
  intervals, ranks, steps, epochs, sequence ids, and retention limits must
  reject booleans and negative values; required positive cadence values must
  reject zero.
- Floating durations, timestamps, metric values, norms, ratios, fractions, and
  thresholds must reject non-finite values unless a field explicitly represents
  missing/unavailable evidence with `None` plus a reason.
- Shape evidence should be a tuple of non-negative integers or symbolic
  strings. Dtype/device/field identifiers should be strings, not framework
  dtype/device objects.
- Metric direction for best-checkpoint selection must be explicit (`min` or
  `max`) and tie-breaking must be deterministic.
- Checkpoint catalog selection should define a stable tie-break order such as
  metric value, completion status, timestamp, epoch, step, sequence id, stream
  id, and ref id where those fields are available. The chosen order must be
  documented and tested rather than inferred from input list order alone.

Error behavior and edge cases:

- Invalid hook points, stages, cadence, selectors, retention rules, restart
  selectors, timestamps, metric values, ranks, mappings, locators, policy
  states, or unsupported policy values fail with `RemotePhysTrainingError` and
  useful owner/field context.
- Empty probe policy collections, empty checkpoint catalogs, disabled policies,
  and unavailable probes are valid when explicitly represented.
- Selecting from an empty or no-match catalog returns explicit no-match
  evidence or fails according to a documented selector policy; it must not
  choose an arbitrary path.
- Metric selection must define behavior for missing metric names, non-finite
  metric values, mixed directions, and ties.
- Rewind selectors must define whether epoch/step anchors are inclusive and how
  they behave when there is no checkpoint far enough back.
- Checkpoint prune evidence must record what was retained, what was pruned, and
  why. Failed or unsupported prune attempts must not be hidden.
- Policy fallback must be visible. A compile or precision policy that cannot be
  applied by a later backend must produce unsupported/fallback evidence rather
  than silently changing numerical behavior.

## Scientific Contract Notes

- Sampling and temporal alignment: probe records and checkpoint evidence may
  reference Phase 1 run ids, timeline ids, timestamps, sequence ids, process
  ids, ranks, and devices. They must not claim global clock synchronization or
  resource alignment beyond the primitive evidence recorded.
- Phase 1 compatibility: Phase 2 may add records that carry Phase 1
  identifiers and may add intentional package exports, but it must not rename
  Phase 1 event phases, alter `TrainingProfile` span/event inspection, require
  resource traces in `TrainingProfile`, or change `TrainingResult.profiles`
  compatibility behavior.
- Field roles, locators, schemas, and provenance: data probe records may carry
  field/role/locator strings, split, source, cache, prepared/materialized,
  request, operation, worker, and rank fingerprints. They must not introduce a
  competing dataset abstraction or require concrete Stage 9 object imports in
  training core.
- Masking, filtering, normalization, and aggregation order: this phase records
  diagnostic summaries only. If a probe record describes masks,
  distributions, norms, or aggregation, it must name the statistic and
  aggregation scope; it must not imply signal preprocessing, filtering, or
  learner output transformation occurred.
- Subject identity, splits, leakage, and grouping: data probe records should
  carry split/group/source provenance when known, but Phase 2 does not create
  splits or subject-level statistics. Any distribution summary must state its
  scope, such as per-batch, per-field, per-rank, per-step, or per-run.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: NaN/Inf/missing/invalid evidence is first-class in model
  and data probe records. Missing optional evidence is represented as
  unavailable/unsupported with a reason; invalid numeric policy or checkpoint
  values fail loudly.

## Design Impact

- Maintainability: separates probe, checkpoint, restart, and policy contracts
  into focused modules instead of expanding `profiling.py` or `results.py` into
  an engine integration layer.
- Extensibility: later native, Lightning, resource, and data-path phases can
  populate the same records through importable Python objects and explicit
  policy records without adding registries or engine-specific public result
  families.
- Lightweight import policy: keeps base training contracts free of optional
  framework, datasource, profiler, hardware, and test-support imports.
- Source-tree boundaries: leaves Stage 9 runtime/data-path code in
  `rphys.datasources`, Phase 3 resource monitoring in profiling/resource
  helpers, Native wiring in `backend.py`, and Lightning work under
  `rphys.training.lightning`.

## Future Compatibility

- Phase 3 can add resource samples/traces and async writer contracts that reuse
  probe ids, hook attribution, unavailable evidence, and policy fallback
  records without redefining probe records.
- Phase 4 can invoke probes and resolve checkpoint/restart policies inside the
  Native loop while returning save/restore/prune evidence from caller-provided
  hooks.
- Phase 5 can attach Stage 9 source/cache/prepared/materialization evidence to
  the Phase 2 pipeline-stage names without changing the training-core import
  graph.
- Phase 6 can map precision/compile/kernel policies to Lightning or native
  unsupported evidence while preserving the same public policy records.
- Phase 7 can translate Lightning callbacks, checkpoint hooks, and public
  profiler events into the same records without exposing raw Lightning state.
- Future engines can implement their own hook contexts and checkpointers as
  long as they produce these primitive rphys records.
- Future-phase exclusions are intentional review gates: Phase 3 owns resource
  traces and profile persistence; Phase 4 owns Native wiring and real
  checkpoint hook execution; Phase 5 owns data-path producers and Stage 9
  runtime integration; Phase 6 and Phase 7 own Lightning API and bridge
  behavior. Phase 2 should only leave primitive, provisional contracts for
  those phases to consume.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Put probe, checkpoint, restart, and policy records into `profiling.py` only. | It would make the profile module own unrelated checkpoint and optimization policy contracts and increase future merge pressure. |
| Import Stage 9 datasource classes into `rphys.training.probes` for pipeline stages. | Base training imports must remain lightweight and must not pull datasource/runtime modules into the training core. |
| Store raw tensors, batches, modules, optimizer state, or dataloaders in probe records. | Raw runtime objects are not primitive, are backend-specific, and would make summaries non-reproducible and hard to serialize. |
| Make `CheckpointCatalog` scan files or own an artifact store. | rphys records checkpoint evidence but does not own artifact storage, workflow runtime, or backend state serialization. |
| Encode Lightning or torch precision/compile options directly in core policies. | Core policies must be framework-neutral; mapping belongs to optional adapters. |
| Add a symbolic registry for probes or checkpoint selectors. | Importable Python objects and explicit records are sufficient; symbolic registries are premature unless a later public contract requires them. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Public schema remains provisional. | Later Native, Lightning, resource, and data-path wiring may reveal missing fields, but Phase 2 needs a shared contract before wiring. | Revisit only when a later phase cannot populate required evidence without breaking the schema. |
| Pipeline stages are string contracts before producer wiring. | Phase 5 owns real Stage 9 integration; Phase 2 only locks names and shape. | Revisit if Phase 5 finds a Stage 9 flow that cannot be represented by additive stage names. |
| Policy records are descriptive before backend mapping. | Native unsupported evidence and Lightning mapping are later phases. | Revisit during Phase 6/7 if public backend APIs require additional additive fields. |
| Checkpoint refs describe locators but not storage semantics. | Storage belongs to caller-provided hooks or downstream systems. | Revisit only if save/restore/prune evidence cannot be recorded without a narrower locator contract. |

## Reviewability

- Expected PR size and shape: moderate schema PR with three new focused
  training modules, selected `rphys.training` exports, and focused package,
  unit, and contract tests. No product-code wiring outside training contracts
  should be needed.
- Files and areas to inspect: `src/rphys/training/probes.py`,
  `src/rphys/training/checkpoint.py`, `src/rphys/training/policies.py`,
  `src/rphys/training/__init__.py`, `tests/unit/rphys/training/`,
  `tests/contracts/`, `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`, and any narrowly justified
  training validation-helper edits.
- Scope-control checks: no new imports of datasource or optional framework
  stacks from base training modules; no file IO in checkpoint records; no raw
  runtime objects in public records; no native loop, Lightning, resource, or
  data-path runtime wiring; no placeholder exports for later phases.

## Implementation Steps

1. Add lightweight validation helpers and probe contracts in `probes.py`,
   including hook points, cadence, selectors, failure policy, pipeline-stage
   names, unavailable evidence, and model/data probe records.
2. Add checkpoint refs, policies, catalog/index behavior, deterministic
   selection evidence, restart selectors, and save/restore/prune evidence in
   `checkpoint.py`.
3. Add precision, compile, and kernel policy records in `policies.py`, with
   requested/applied/fallback/unsupported state and numerical-risk/equivalence
   evidence.
4. Update package exports and package/import-boundary tests for only the
   implemented names and modules.
5. Add focused unit tests for validation, immutability, edge cases, selector
   ordering, unsupported/unavailable evidence, primitive record shape, and
   dataclass inspection.
6. Add contract tests for stable hook/stage names, primitive serialization or
   dataclass inspection, checkpoint selection examples, Phase 1 compatibility,
   and future-engine/data-path compatibility boundaries.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exported public names match
  `rphys.training.__all__`; `rphys.training.probes`,
  `rphys.training.checkpoint`, and `rphys.training.policies` import directly;
  lightweight imports do not load `rphys.datasources`, Lightning, torch, JAX,
  CUDA/NVML, numpy, pandas, scipy, plotting/video libraries, logging backends,
  or `tests.support`; adding Phase 2 modules does not force Stage 9
  datasource imports through `rphys.training`.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/training/test_probes.py`,
  `tests/unit/rphys/training/test_checkpoint.py`,
  `tests/unit/rphys/training/test_policies.py`
- Required assertions or deferral reason: validate construction, coercion,
  immutability, primitive mappings, invalid inputs, non-finite values, disabled
  and unavailable states, model/data record summaries, pipeline-stage values,
  checkpoint retention/selection ordering, restart selectors,
  save/restore/prune result states, dataclass inspection, and policy
  fallback/unsupported behavior.

### Contract Suite

- Status: required
- Expected paths: new Stage 15 contract tests such as
  `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`, plus any
  needed updates to `tests/contracts/test_stage15_training_profile_contract.py`
  or Stage 12 compatibility contracts if public exports interact with them.
- Required assertions or deferral reason: stable hook and pipeline-stage names;
  primitive serialization and dataclass-inspection shape; Phase 1
  profile/event/result compatibility; examples for gradient norm records,
  batch NaN records, pre-cache/post-cache stage records,
  keep-last retention, best metric selection, rewind by epoch/step, explicit
  unavailable/unsupported evidence, and no artifact-store or raw-runtime
  object behavior.

### Integration Suite

- Status: deferred for this phase
- Expected paths: Phase 4, Phase 5, and Phase 7 integration tests will consume
  these contracts through Native, data-path, and Lightning wiring.
- Required assertions or deferral reason: Phase 2 does not wire engines,
  checkpoint hooks, resource samplers, or data-path producers. Running
  integration tests is not required unless the executor touches integration
  surfaces unexpectedly; if touched, add focused synthetic integration coverage
  or stop for manager review.

### E2E Suite

- Status: deferred for this phase
- Expected paths: later Stage 15 public workflow examples after Native,
  data-path, Lightning, and docs hardening phases.
- Required assertions or deferral reason: no end-to-end training path changes
  are in scope. E2E coverage would be fake wiring and should wait for engine
  integration.

### Acceptance Suite

- Status: deferred for this phase
- Markers affected: none expected
- Required assertions or deferral reason: real hardware, installed Lightning,
  real checkpoint storage, real datasets, and long-running profiling checks are
  explicitly out of scope. Optional acceptance belongs to later Lightning,
  resource, and final-hardening phases.

## Risks

- Probe records could become too generic to guide later engines. Mitigation:
  lock concrete hook-point, stage, cadence, selector, failure-policy, and
  model/data summary fields with examples.
- Checkpoint selection could hide ambiguous ordering. Mitigation: require
  deterministic metric direction, timestamp/epoch/step tie-breaking, and
  explicit no-match evidence.
- Policy records could drift into backend-specific configuration bags.
  Mitigation: keep records primitive and framework-neutral, with adapter
  mapping deferred.
- Import boundaries could regress if pipeline stages reference Stage 9 classes
  directly. Mitigation: use string/fingerprint records in training core and
  package import-boundary tests.
- Public schema churn could affect later phases. Mitigation: mark provisional
  and keep future changes additive unless a manager-approved contract revision
  is needed.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/training/test_probes.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_policies.py
uv run pytest tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/contracts/test_stage15_training_profile_contract.py
make test-package
uv lock --check
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: start with `probes.py`, then `checkpoint.py`,
  then `policies.py`, then exports/package tests, then unit/contract tests.
- Tests to run with each slice: run the matching focused unit test after each
  module, run the Stage 15 contract test after public names stabilize, and run
  `make test-package` after export/import-boundary changes.
- Decisions the executor must not revisit: Phase 2 remains schema-only and
  engine-neutral; no raw tensor/batch capture; no checkpoint writer or artifact
  store; no datasource imports from training core; no Lightning/native/resource
  wiring; no profile persistence; no backend-specific public result family;
  Phase 1 event/profile/result compatibility remains additive.
- Conditions that require stopping for the manager: implementing the records
  requires raw runtime objects, a concrete checkpoint serialization format,
  file/storage IO, a registry, framework-specific policy fields, datasource
  imports in base training modules, or changes outside the assigned ownership
  surface beyond package exports and focused tests.

## Refinement And Review Budget Status

- Phase execution plan refinement: complete; unused PR review budget remains
- Phase implementation refinement: 1/3 used for post-implementation blocker
  cluster on public exports, disabled policies, metric-direction retention,
  unsupported probe evidence, finite primitive summaries, and checkpoint result
  provenance.
- PR review: unused
- Blocker resolution: 1/3 used

## Completion Notes

- Draft plan: complete in this file
- Final phase execution plan: complete in this file after expanded-path
  refinement
- Implementation summary: completed. Added dependency-light probe, checkpoint,
  and policy contracts with public exports; added unit coverage and contract
  validation for vocabularies, primitive dataclass inspection, deterministic
  checkpoint restart selection, and fallback/unsupported policy states.
- Implementation validation: completed. Ran
  `tests/unit/rphys/training/test_probes.py`,
  `tests/unit/rphys/training/test_checkpoint.py`,
  `tests/unit/rphys/training/test_policies.py`,
  `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`,
  `tests/contracts/test_stage15_training_profile_contract.py`,
  `make test-package`, `uv lock --check`, and `git diff --check`.
- Refinement summary: completed for public provisional schema, primitive
  serialization/dataclass inspection, Phase 1 compatibility, import
  boundaries, checkpoint catalog/restart selector semantics, Stage 9
  pipeline-stage naming, precision/compile/kernel fallback evidence, and
  explicit future-phase exclusions
- Pre-submit blocker gate: resolved for phase scope; remaining blockers: none.
- Post-implementation refinement summary: completed on 2026-05-18 for the
  assigned blocker cluster. Exported `CheckpointMetricDirection` intentionally;
  made disabled checkpoint save/prune policies constructible only as explicit
  no-op records; required `best_metric_direction` for `keep_best`; added
  `ProbeFailurePolicy.UNSUPPORTED`; rejected non-finite `ModelProbeSummary`
  primitive values; and added optional run/timeline/process/rank/device,
  metadata, and provenance evidence to checkpoint save/restore/prune result
  records.
- Post-implementation refinement validation: completed. Ran
  `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_probes.py tests/unit/rphys/training/test_policies.py tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py`
  (93 passed). `git diff --check` passed.
- PR preparation: complete; PR body artifact drafted at
  `docs/roadmap/stage-15/phases/probe-checkpoint-policy-contracts-pr-body.md`
  with local validation evidence from targeted checks, `make test-package`,
  `uv lock --check`, `git diff --check`, `make test-summary`, and
  `make validate-pr`.
- Automated review: pending implementation
- Merge result: pending implementation
- Cleanup: pending implementation
- Remaining blockers: none

## Phase Refinement Report: Probe And Checkpoint Contract Blockers

## Assigned Blocker

- Blocker: Phase 2 public checkpoint/probe contracts missed several accepted
  contract details: `CheckpointMetricDirection` was not exported, disabled
  checkpoint policies could not represent explicit no-op behavior, best
  retention did not require direction, unsupported probe evidence was not
  distinct from unavailable evidence, primitive model-summary values accepted
  non-finite floats, and checkpoint result records lacked rank/process and
  provenance evidence.
- Source: implementation refinement request on 2026-05-18 plus Phase 2 scope
  contract for primitive public exports, disabled policies, metric-direction
  significance, unavailable/unsupported evidence, finite diagnostic values,
  and rank/process evidence in save/restore/prune results.
- Scope: `src/rphys/training/checkpoint.py`, `src/rphys/training/probes.py`,
  package exports, focused unit/contract/package tests, and this phase artifact
  update only.
- Budget use: phase implementation refinement 1/3; blocker resolution 1/3.

## Resolution

- Changes made: exported `CheckpointMetricDirection`; allowed only explicit
  disabled no-op save/prune policies; required `best_metric_direction` with
  `keep_best`; added `ProbeFailurePolicy.UNSUPPORTED`; rejected non-finite
  `ModelProbeSummary.value` floats; and added optional run/timeline/process,
  node, rank, device, metadata, and provenance fields to checkpoint
  save/restore/prune result records.
- Tests or docs updated: checkpoint, probe, Stage 15 contract, and package
  export tests cover the refined public behavior and primitive evidence shape.
- Validation rerun: targeted Phase 2 unit/contract/package command passed with
  93 tests; final `git diff --check` evidence is recorded in the handoff.

## Result

- Blocker resolved: yes.
- Remaining blocker: none for this blocker cluster.
- Recommended next gate: commit refinement fix, then continue Phase 2 PR
  preparation/review.

## Files Changed

- `src/rphys/training/checkpoint.py`
- `src/rphys/training/probes.py`
- `src/rphys/training/__init__.py`
- `tests/unit/rphys/training/test_checkpoint.py`
- `tests/unit/rphys/training/test_probes.py`
- `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`
- `tests/package/test_import.py`
- `docs/roadmap/stage-15/phases/probe-checkpoint-policy-contracts.md`
