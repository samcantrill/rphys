# Phase 1 Execution Plan: Core Timeline And Profile Records

## Metadata

- Status: final phase execution plan; expanded-path refinement completed; ready
  for implementation
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Core Timeline And Profile Records
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 1: Core Timeline And Profile Records`
- Branch: `agent/stage-15-training-profiling-p1-core-timeline-profile-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p1-core-timeline-profile-records`
- Phase execution plan path: `docs/roadmap/stage-15/phases/core-timeline-profile-records.md`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Planning document: `docs/roadmap/stage-15/planning.md`
- Source phase: `docs/roadmap/stage-15/implementation-plan.md`, `## Phase 1: Core Timeline And Profile Records`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation plan approved; expanded-path refinement
  completed for public provisional schema, primitive serialization, Stage 12
  compatibility, import-boundary, timestamp/timeline, result compatibility, and
  Phase 3 resource-trace boundary risks
- Draft pass: complete
- Refine pass: complete; limited to the assigned expanded-path triggers, with
  phase implementation refinement and PR review budgets left unused
- Setup limitations: existing manager-created worktree was verified instead of
  creating a new branch/worktree; no push or PR action was performed in this
  planning pass
- Blockers: none

## Objective

Define the minimal, dependency-light timeline and profile substrate that native,
Lightning, future engines, and later data-path profilers can populate through
shared rphys records. This phase locks additive Stage 12 event compatibility,
timestamp/timeline evidence, append-only event logs, scalar span and
unavailable evidence, a basic `TrainingProfile` aggregate and recorder, and an
optional `TrainingResult.training_profile` attachment without implementing
resource traces, probes, checkpoints, policies, native loop wiring, Lightning,
or data-path producers.

## Full-Plan Context

Phase 1 is the shared public output target for the rest of Stage 15. Phase 2
adds probe, checkpoint, restart, and policy contracts on top of these records.
Phase 3 adds concrete resource trace record types, background monitoring, and
profile persistence. Phase 4 wires native engine observability. Phase 5 aligns
data-path pipeline probes with Stage 9 records. Phases 6 and 7 add optional
Lightning API and observability bridges. Phase 8 closes docs, tiers, and broad
validation.

The executor must keep this phase schema-only and import-light. Any need for
resource time-series helpers, checkpoint refs/catalogs, probe protocols,
policy records, async writers, native instrumentation, Lightning imports, or
data-path source imports is a stop condition or future-phase note, not Phase 1
implementation scope.

## Source Phase Summary

- Goal: define the minimal shared timeline/profile substrate that every later
  Stage 15 phase targets.
- Required scope: `src/rphys/training/events.py`,
  `src/rphys/training/profiling.py`, `src/rphys/training/results.py`,
  `src/rphys/training/__init__.py`, event/profiling/result unit tests, Stage 12
  observability contract tests, and package import/export tests.
- Required checkpoints: preserve existing Stage 12 phase values and observer
  behavior; add timestamp/timeline and rank/process metadata; add append-only
  event logs; add scalar span/unavailable records; add basic
  `TrainingProfile` and `TrainingProfileRecorder`; add optional
  `TrainingResult.training_profile`; keep `TrainingResult.profiles` summaries
  compatible.
- Acceptance criteria: old and new events validate; profile evidence remains
  primitive and serialization-friendly without defining a durable file/JSON
  format; `TrainingProfile` can expose event logs, scalar spans, unavailable
  evidence, decisions/summaries, and compatibility summaries without resource
  trace helpers; package imports remain lightweight and do not expose concrete
  resource traces before Phase 3.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/training/events.py` currently defines the Stage 12
  `TrainingEventPhase`, `TrainingEvent`, observe-only `TrainingEventSink`,
  `TrainingCallback`, and fail-loud `emit_training_event` fanout. The current
  event record carries phase, mode, status, loop indexes, split, primitive
  metadata, and primitive provenance.
- Existing profile/result shape: `src/rphys/training/profiling.py` currently
  defines `ProfileSpanSummary`, `UnavailableProfileProbe`, and
  `TrainingProfiler`; `src/rphys/training/results.py` keeps
  `TrainingResult.profiles` as summary-only `ProfileSummary` records and has no
  rich aggregate attachment.
- Existing tests or harness behavior: unit tests cover event coercion,
  observer-only fanout, span/unavailable validation, and primitive result
  summaries. `tests/contracts/test_stage12_observability_contract.py` protects
  Stage 12 observability behavior. `tests/package/test_import.py` pins training
  exports and module `__all__`; `tests/package/test_import_boundaries.py`
  forbids training imports from loading datasources, Lightning, torch, JAX,
  plotting, dataframe, video, logging, and test-support stacks.
- Import-boundary or dependency constraints: training core may depend on
  standard-library modules and existing lightweight rphys training/learning
  helpers only. Do not import `rphys.datasources`, `torch`, `lightning`,
  `numpy`, `pandas`, `scipy`, system profiler libraries, or test-support
  modules from base training modules.

## Phase Isolation State

- Control checkout dirty-state review: reviewed `/home/samcantrill/work/rphys`;
  it was clean on `develop...origin/develop`.
- Dedicated branch/worktree status: verified clean worktree at
  `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p1-core-timeline-profile-records`
  on `agent/stage-15-training-profiling-p1-core-timeline-profile-records`.
- Current `develop` base: worktree `HEAD` and `origin/develop` both resolved to
  `e37fef073f98adc1489c3ff8c653da53933aea40`; `origin/develop` is an ancestor
  of `HEAD`.
- Earlier phase dependency status: none; this is Stage 15 Phase 1.
- Push/PR infrastructure status: not exercised during this plan-only pass; the
  implementation workflow should verify `gh auth status` before opening the PR.
- Stop condition if isolation cannot be maintained: stop before editing product
  code if the branch diverges from `develop`, the worktree is dirty with
  unrelated edits, or another Stage 15 phase starts writing into this worktree.

## In-Scope Work

- Extend `TrainingEventPhase` additively while preserving all Stage 12 enum
  values: `loop_started`, `step_started`, `step_completed`, `loop_completed`,
  `loop_failed`, and `external_summary`.
- Add primitive timestamp/timeline fields to `TrainingEvent` or an equivalent
  public event record shape: run id, timeline id, optional sequence id,
  timestamp, clock name/origin evidence, process id, node id, local rank,
  global rank, and device id where relevant.
- Add append-only `TrainingEventLog` or equivalent event-log record with stable
  sequence ordering, immutable read access, primitive serialization-friendly
  data, and validation for duplicate/out-of-order sequence ids.
- Define the Phase 1 primitive serialization boundary explicitly in code and
  tests: records must be convertible to nested Python primitives and tuples by
  standard-library/dataclass-style inspection, but this phase must not add a
  profile codec, persistence format, schema-versioned export format, or writer.
- Add scalar profile span records with nonnegative timing, optional start/end
  timestamp evidence, overhead, synchronization notes, rank/process/timeline
  attribution, primitive metadata, and primitive provenance.
- Add unavailable profile evidence that can represent absent optional probes or
  deliberately unavailable spans without hiding the reason, overhead, or
  attribution.
- Add a basic provisional `TrainingProfile` aggregate with stable rphys-facing
  inspection helpers for event logs, scalar spans, decisions, summaries, and
  unavailable evidence only.
- Add a basic `TrainingProfileRecorder` that can append events, record scalar
  spans/unavailable evidence, use an injectable monotonic clock for deterministic
  tests, and return a frozen/inspection-safe `TrainingProfile`.
- Add optional `TrainingResult.training_profile` while keeping existing
  `TrainingResult.profiles` callers and summary records compatible.
- Update `src/rphys/training/__init__.py` and package import tests for only
  code-backed public names introduced in this phase.

## Out-of-Scope Work

- Concrete `ResourceTrace`, `ResourceSample`, `resource_traces`,
  `add_resource_trace`, empty resource-trace placeholder fields/properties,
  GPU/CPU/disk network/framework trace schemas, fake resource samplers,
  background processes/threads, async writers, dropped-sample queues, and
  persistence lifecycle. Those are Phase 3.
- Probe protocols, model/data probe records, pipeline-stage hook names,
  checkpoint policies/catalogs, restart selectors, precision/compile/kernel
  policy records, and checkpoint result/ref records. Those are Phase 2 and
  later.
- Native engine setup/teardown/data-wait/device-transfer/checkpoint/profile
  wiring, learner loop changes, callback failure ordering changes, checkpoint
  hooks, or backend integration. Those are Phase 4.
- Optional Lightning modules, Lightning callbacks/profilers/checkpoints,
  public Lightning entrypoints, imports, security preflight, fake-Lightning
  tests, or distributed-rank bridge behavior. Those are Phases 6 and 7.
- Data-path benchmark/profiling producers, Stage 9 source/cache/prepared hooks,
  `BatchOperation` optimization/equivalence additions, real dataset fixtures,
  or datasource imports from training core. Those are Phase 5.
- Workflow runtime, schedulers, artifact stores, default checkpoint writers,
  dashboards, performance thresholds, or machine-speed claims.

## Assumptions

- Existing Stage 12 public event phases and result/profile summaries are
  already code-backed API and must continue to pass current tests unchanged.
- A provisional public schema is acceptable when additive, primitive,
  serializable by standard Python/dataclass inspection, and tested for invalid
  values and absent optional evidence.
- Primitive serializable means nested strings, numbers, booleans, `None`,
  tuples, and primitive mappings only. It does not imply a stable JSON schema,
  file format, profile artifact, pickle contract, or automatic writer.
- Stage 12 compatibility includes constructor call patterns, existing enum
  values, observer/callback fanout behavior, and the existing
  `TrainingResult.profiles` summary meaning.
- Default tests stay CPU-only, synthetic, deterministic, and dependency-light.
- The recorder may use standard-library timing only and must allow a fake clock
  in unit tests; it must not synchronize devices or import optional runtime
  stacks.
- Phase 3 will add resource trace records additively, so Phase 1 must leave a
  clear aggregate extension point without exposing a placeholder trace family.

## Scope Contract

Public behavior:

- The Phase 1 schema is public and provisional: every exported name and helper
  must be code-backed, tested, and documented enough for downstream
  inspection, but future growth must remain additive. Do not export placeholder
  classes, protocols, fields, or accessors for Phase 2/3 concepts.
- `TrainingEventPhase.coerce` must continue accepting existing Stage 12 values
  and must reject unsupported values with `RemotePhysTrainingError` context. No
  Stage 12 phase value may be renamed, removed, repurposed, or made invalid.
  New phase values must be additive and coarse. Required additions should cover
  setup, teardown, data wait, device transfer, validation, checkpoint,
  profiling/summary, and generic stage evidence without turning callbacks into
  loop-control APIs.
- `TrainingEvent` must remain an observe-only primitive record. Sinks record and
  callbacks react through the existing structural protocols; callback return
  values are ignored and observer errors remain fail-loud.
- Timestamp and clock fields must not claim global ordering across processes or
  devices. Per-log ordering is represented by sequence ids; per-run grouping is
  represented by run ids and timeline ids; any cross-process merge requires
  explicit clock-origin metadata and remains descriptive evidence, not a merge
  algorithm. Missing timestamp evidence means "not recorded", never zero.
- Event logs are append-only evidence. Public access must not expose a mutable
  sequence that lets callers reorder or replace prior events. Appends must
  preserve sequence order and reject duplicate or decreasing sequence ids.
- Scalar spans represent code-region duration evidence, not resource time
  series. They may include start/end timestamps and duration/overhead fields,
  but they must not expose resource trace/sample helpers.
- Unavailable evidence is first-class. Missing optional timing/probe evidence
  must carry a non-empty reason and primitive attribution rather than silently
  disappearing.
- `TrainingProfile` is a provisional aggregate and must expose stable
  inspection helpers for Phase 1 evidence: event logs/events, scalar spans,
  unavailable evidence, decisions, summaries, and summary projection for
  `TrainingResult.profiles` compatibility. It must not define `resource_traces`,
  resource-trace mutation helpers, or concrete trace/sample record types in
  this phase, including empty placeholders that would imply Phase 3 schema.
- `TrainingResult.training_profile` is optional, defaults to `None`, validates
  type, and preserves all existing constructor call patterns and existing
  `profiles=` behavior. Existing `profiles` summaries remain tuple-like
  summary evidence; if summaries are derived from `training_profile`, the rule
  must be deterministic, explicit, and tested without changing callers that
  still pass summaries directly.

Module boundaries:

- `events.py` owns event phases, event records, event logs, sinks, callbacks,
  and event fanout helpers.
- `profiling.py` owns scalar spans, unavailable profile evidence, profile
  aggregate, and recorder basics.
- `results.py` owns result summaries and the optional `training_profile`
  attachment. Avoid import cycles; if result summary projection needs
  `ProfileSummary`, keep the projection in `results.py` or another acyclic
  location rather than making `profiling.py` import result classes.
- `__init__.py` re-exports only implemented, tested names from the owned
  training modules.
- No Phase 1 module may import Phase 2/3/4/5/6 concepts to satisfy type hints
  or convenience helpers. Keep probe, checkpoint, policy, resource monitoring,
  native backend, Lightning, datasource, and optional framework imports out of
  the Phase 1 core modules.

Data shapes:

- Public records must use immutable dataclass-like shapes or otherwise provide
  immutable/frozen read behavior consistent with current Stage 12 records.
- Metadata/provenance must remain primitive mappings using the existing
  validation policy: non-empty string keys and primitive values only.
- Serialization-friendly coverage must prove records do not contain live
  clocks, callbacks, profiler objects, framework/backend objects, raw tensors,
  open handles, mutable metadata mappings, or datasource/data-path objects.
- Indexes, sequence ids, process ids, ranks, counts, and durations must reject
  booleans and negative values.
- Optional identifiers such as `run_id`, `timeline_id`, `node_id`,
  `clock_name`, `device_id`, `span_name`, `stage_name`, `engine`, `backend`,
  and `probe_name` must be non-empty strings when provided.

Error behavior and edge cases:

- Invalid phase, mode, timestamp, duration, rank, sequence id, metadata,
  provenance, span status/name, unavailable reason, or result attachment type
  must fail with `RemotePhysTrainingError` and useful owner/field context.
- Empty event logs and empty profiles are valid.
- Spans with unavailable duration are valid only when status/reason evidence
  explains unavailability through the explicit unavailable record path or
  tested status semantics.
- Wall-clock timestamps, monotonic timestamps, and clock-origin fields must be
  optional; absence means "not recorded", not zero.
- `TrainingProfileRecorder` must return a profile that remains stable after
  later recorder appends.

## Scientific Contract Notes

- Sampling and temporal alignment: Phase 1 records timestamp and clock-origin
  evidence only. It must distinguish monotonic/per-process ordering from
  wall-clock or cross-process ordering and avoid claims that ranks, nodes, or
  devices are globally synchronized. Sequence ids order events only within the
  owning log/timeline unless a later phase records stronger clock-alignment
  evidence.
- Field roles, locators, schemas, and provenance: training profile fields are
  diagnostic evidence, not data-field locators or dataset schemas. Provenance
  should identify run, engine/backend, process/rank/device, clock origin, and
  recorder/probe source where known.
- Masking, filtering, normalization, and aggregation order: no physiological
  signal masking/filtering/normalization is performed in this phase. Any
  profile summaries are diagnostic aggregations over spans/events and must not
  alter learner outputs or metrics.
- Subject identity, splits, leakage, and grouping: no subject or split
  assignment logic is introduced. Existing `split` evidence remains optional
  event context only; no profile aggregation may imply subject-level or
  dataset-level statistics.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: no signal arrays or sample slices are processed. Invalid
  numeric timing/rank/count fields fail fast; missing optional profile evidence
  is represented by explicit unavailable records.

## Design Impact

- Maintainability: keeps Stage 15 shared evidence in small training modules
  instead of duplicating engine-specific event/profile/result families.
- Extensibility: later phases can add resource traces, probes, checkpoints,
  native/Lightning wiring, and data-path producers additively against the same
  `TrainingProfile` target.
- Lightweight import policy: base training imports remain standard-library and
  existing lightweight rphys-only; no optional framework, array, plotting,
  datasource, system-profiler, or test-support imports enter training core.
- Source-tree boundaries: training core records stay under `src/rphys/training`;
  data-path profiling remains in datasource/data-path phases; workflow,
  artifacts, sweeps, and orchestration remain downstream or in `loom`.

## Future Compatibility

- Phase 3 must be able to add resource trace records and resource trace
  inspection helpers without changing Phase 1 event/span/result semantics. It
  must add those names as new public surface rather than filling Phase 1
  placeholders.
- Native and Lightning engines must be able to populate the same event log and
  profile aggregate without exposing backend-private callback/profiler state.
- Downstream consumers should find detailed evidence through
  `TrainingResult.training_profile` and summary evidence through
  `TrainingResult.profiles`, without branching on engine family.
- Additional lifecycle phases may be added later only as additive enum values
  when native/Lightning parity proves they are necessary.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add a second Stage 15 event family separate from `TrainingEvent`. | Breaks Stage 12 compatibility and creates duplicate observer APIs for future engines. |
| Collapse existing `loop_started`, `step_started`, `step_completed`, `loop_completed`, and `loop_failed` values into status-only semantics. | Existing values are code-backed public API and must remain valid. |
| Store detailed profile evidence only in `TrainingResult.metadata`. | Hides schema, weakens validation, and makes downstream profile consumers parse ad hoc keys. |
| Expose raw Lightning, torch, profiler, callback, optimizer, or framework timeline objects. | Violates dependency-light and engine-neutral public-result contracts. |
| Add concrete resource trace/sample records in Phase 1. | Phase 3 owns resource monitoring, persistence, dropped samples, and trace helpers. |
| Add checkpoint/probe/policy records now. | Phase 2 owns those contracts and their validation. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| `TrainingProfile` is provisional and initially lacks resource trace helpers. | Keeps Phase 1 reviewable and prevents placeholder trace APIs before Phase 3 lifecycle/failure behavior is designed. | Phase 3 adds resource traces or proves the aggregate cannot extend additively. |
| Native engine will still emit only Stage 12 summaries until Phase 4. | This phase is schema-only and must not mix public record design with loop instrumentation. | Phase 4 native wiring begins. |
| No persistence or async writer behavior exists yet. | Phase 3 owns profile persistence and backpressure/dropped-sample evidence. | Resource monitoring or writer implementation begins. |
| Clock alignment remains descriptive, not a merge algorithm. | Cross-process clock synchronization is backend/runtime-specific and should not be faked in core records. | Native/Lightning distributed tests need stronger merge semantics. |

## Reviewability

- Expected PR size and shape: moderate schema/test PR touching four training
  modules plus focused unit, contract, and package tests. No backend, data-path,
  Lightning, checkpoint, policy, or resource-monitor implementation changes.
- Files and areas to inspect: `src/rphys/training/events.py`,
  `src/rphys/training/profiling.py`, `src/rphys/training/results.py`,
  `src/rphys/training/__init__.py`, `tests/unit/rphys/training/test_events.py`,
  `tests/unit/rphys/training/test_profiling.py`,
  `tests/unit/rphys/training/test_results.py`,
  `tests/contracts/test_stage12_observability_contract.py`,
  any new Stage 15 profile/event contract test, and
  `tests/package/test_import.py` / `tests/package/test_import_boundaries.py`.
- Scope-control checks: `git diff --stat` should not show edits to
  `backend.py`, `plan.py`, datasource modules, ops modules, Lightning modules,
  checkpoint/policy/probe modules, docs outside necessary API references, or
  dependency/lock files. Public export diffs should show Phase 1 event/log,
  scalar-span, unavailable-evidence, profile, recorder, and result attachment
  names only, with no `ResourceTrace`, `ResourceSample`, `resource_traces`,
  probe, checkpoint, policy, Lightning, or datasource entrypoints.

## Implementation Steps

1. Extend event records and event logs. Preserve Stage 12 phase values and
   observer behavior, add additive lifecycle phases plus timestamp/timeline and
   rank/process/device attribution, then add append-only event-log validation
   and immutable read behavior.
2. Add scalar profile evidence and recorder basics. Keep existing
   `ProfileSpanSummary` and `UnavailableProfileProbe` compatibility, introduce
   richer scalar span/unavailable evidence plus `TrainingProfile` and
   `TrainingProfileRecorder`, and ensure the recorder uses injectable timing
   without hidden synchronization.
3. Attach detailed profile evidence to results. Add optional
   `TrainingResult.training_profile`, preserve current summary-only constructor
   behavior, define deterministic summary compatibility, and avoid
   profiling/results import cycles.
4. Update public exports intentionally. Add only code-backed Phase 1 names to
   module `__all__` and `rphys.training.__all__`; keep package import-boundary
   tests explicit that no resource trace, probe, checkpoint, policy, Lightning,
   datasource, or heavy optional dependency appears.
5. Add focused validation coverage. Expand event/profiling/result unit tests,
   Stage 12 observability contract tests, and package tests for valid/invalid
   schema, serialization-friendly primitive data, backward compatibility,
   unavailable evidence, and no out-of-scope exports.
6. Run scope and compatibility checks. Verify the diff is limited to Phase 1
   owned files/tests, current Stage 12 contracts still pass, and no future-phase
   placeholder APIs leaked into public surface.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`;
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: update training export expectations
  for Phase 1 names only; assert new modules/classes are code-backed; assert
  base training imports still do not load datasources, Lightning,
  PyTorch/JAX/torchmetrics, plotting, array/dataframe, video, logging,
  system-profiler, or `tests.support` modules; assert `ResourceTrace`,
  `ResourceSample`, `resource_traces`, probe, checkpoint, and policy names are
  not exported in Phase 1.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/training/test_events.py`;
  `tests/unit/rphys/training/test_profiling.py`;
  `tests/unit/rphys/training/test_results.py`
- Required assertions or deferral reason: additive event phase coercion,
  old-phase compatibility, timestamp/timeline/rank/process validation,
  append-only event-log sequence ordering and immutable reads, observer fanout
  order and ignored callback returns, scalar span nonnegative timing and
  synchronization/overhead notes, unavailable evidence reasons, recorder
  snapshot stability, profile inspection helpers, result attachment type
  validation, and `profiles` summary compatibility.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_stage12_observability_contract.py`;
  `tests/contracts/test_stage12_training_result_contract.py`; add
  `tests/contracts/test_stage15_training_profile_contract.py` if the contract
  surface is too broad for the existing Stage 12 files.
- Required assertions or deferral reason: Stage 12 observers and result
  contracts remain valid; Stage 15 profile/event records are primitive,
  engine-neutral, timestamp-aware, serialization-friendly, explicit about
  unavailable evidence, free of raw backend/framework objects, preserve direct
  `profiles=` summary compatibility, and contain no resource
  trace/checkpoint/probe/policy public schema before later phases.

### Integration Suite

- Status: deferred
- Expected paths: existing Stage 12 integration tests such as
  `tests/integration/test_stage12_fake_external_engine.py` only if the executor
  changes behavior that could affect external result normalization.
- Required assertions or deferral reason: Phase 1 is schema-only and does not
  wire native or external engines. Unit, contract, and package tests cover the
  public record compatibility required before Phase 4/7 integrations. If any
  backend or trainer behavior is touched, stop as out of scope or add a narrow
  Stage 12 compatibility integration run with manager-visible justification.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end training workflow is
  changed in Phase 1. Native whole-path and Lightning/data-path flows are later
  phases.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no optional real Lightning, GPU,
  system-resource, real dataset, or long-running behavior is implemented in
  Phase 1. Optional acceptance belongs to resource/Lightning phases and must
  report unavailable/unsafe dependencies explicitly when introduced.

## Risks

- Public provisional schema could become too broad before native and Lightning
  pressure-test it; keep additions primitive, additive, and clearly documented
  as provisional.
- Primitive serialization coverage could be overread as a persistence promise;
  keep tests focused on primitive record contents and explicitly defer codecs,
  schema versions, writers, and profile artifacts.
- Timestamp fields could imply impossible global ordering; tests and docstrings
  must distinguish per-timeline sequence order from cross-process clock
  alignment.
- Result/profile imports can create cycles if summary projection crosses
  module boundaries carelessly.
- Package export tests currently use Stage 12 names; updates must remain
  intentional and must not allow placeholder future-phase names.
- A recorder context-manager convenience can accidentally hide device
  synchronization or overhead. It must be explicit that Phase 1 timing is
  standard-library scalar timing only.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/training/test_events.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_results.py
uv run pytest tests/contracts/test_stage12_observability_contract.py tests/contracts/test_stage12_training_result_contract.py
uv run pytest tests/contracts/test_stage15_training_profile_contract.py
make test-package
```

If no new Stage 15 contract file is added, replace the third command with the
contract file that received the Stage 15 profile assertions.

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
uv lock --check
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: event/log schema first, profile/recorder schema
  second, result attachment third, exports/tests fourth, scope audit last.
- Tests to run with each slice: event unit tests after event/log changes;
  profiling unit tests after span/profile/recorder changes; results unit tests
  after `TrainingResult.training_profile`; contract and package tests after
  exports stabilize.
- Decisions the executor must not revisit: preserve Stage 12 event phases;
  keep callbacks observe-only and fail-loud; attach at most one optional rich
  aggregate as `TrainingResult.training_profile`; preserve `profiles`
  summaries; keep raw backend timelines and heavy imports out of training core;
  do not expose resource trace helpers or placeholders in Phase 1.
- Conditions that require stopping for the manager: inability to express Phase
  1 profile compatibility without concrete resource trace types or placeholders;
  need to change native backend behavior; need to add checkpoint, probe, policy,
  Lightning, or datasource imports; import cycle that requires moving records
  outside the owned modules; or any schema decision that would break existing
  Stage 12 callers.

## Refinement And Review Budget Status

- Phase execution plan refinement: completed on 2026-05-18 for the assigned
  expanded-path triggers
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: created in the verified dedicated Phase 1 worktree.
- Final phase execution plan: completed after expanded-path refinement on
  2026-05-18.
- Implementation summary: pending implementation phase.
- Implementation validation: pending implementation phase.
- Refinement summary: clarified the public provisional schema, primitive
  serialization boundary, Stage 12 compatibility obligations, import
  boundaries, timestamp/timeline semantics, result compatibility, and explicit
  Phase 3 ownership of concrete resource trace records and `resource_traces`
  helpers without changing scope.
- Pre-submit blocker gate: pending implementation phase.
- PR preparation: pending implementation phase.
- Automated review: pending implementation phase.
- Merge result: pending implementation phase.
- Cleanup: pending implementation phase.
- Remaining blockers: none for implementation start.
