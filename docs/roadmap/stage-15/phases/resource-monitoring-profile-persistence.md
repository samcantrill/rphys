# Phase 3 Execution Plan: Resource Monitoring And Profile Persistence

## Metadata

- Status: final phase execution plan; expanded-path concerns addressed; ready
  for implementation
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Resource Monitoring And Profile Persistence
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 3: Resource Monitoring And Profile Persistence`
- Branch: `agent/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`
- Phase execution plan path: `docs/roadmap/stage-15/phases/resource-monitoring-profile-persistence.md`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Planning document: `docs/roadmap/stage-15/planning.md`
- Source phase: `docs/roadmap/stage-15/implementation-plan.md`, `## Phase 3: Resource Monitoring And Profile Persistence`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation plan approved; Phase 1 and Phase 2 are
  merged into `develop`; expanded-path detail covers resource sample/trace
  public schema, monitor lifecycle evidence, bounded buffering,
  backpressure/dropped samples, async writer contracts, import boundaries,
  primitive inspection, and explicit future-phase exclusions
- Draft pass: complete
- Refine pass: not needed; expanded-path risks are captured in this artifact
- Setup limitations: existing manager-created worktree and branch were verified
  instead of creating a new branch/worktree; no fetch, push, or PR action was
  performed in this planning pass
- Blockers: none

## Objective

Add the engine-neutral resource-monitoring and profile-persistence substrate
that later Native, Lightning, future-engine, and data-path producers can invoke:
typed resource sample/trace records, optional resource probe protocols with
deterministic fake probes, monitor lifecycle records for thread/process-style
samplers, bounded buffer/backpressure/drop evidence, and async profile writer
contracts. The implementation must keep default imports dependency-light and
must not wire any engine, real hardware probe, artifact store, scheduler, or
data-path producer.

## Full-Plan Context

Phase 1 added timestamped events, event logs, scalar spans, unavailable profile
evidence, `TrainingProfile`, `TrainingProfileRecorder`, and
`TrainingResult.training_profile`. Phase 2 added generic probe contracts,
model/data probe records, checkpoint catalogs/selectors, restart evidence, and
precision/compile/kernel policies. Phase 3 completes the shared profile schema
for timestamped resource behavior and profile persistence without invoking it
from an engine.

Phase 4 will start and stop these monitors from Native and attach their output
to real native runs. Phase 5 will use Stage 9 data-path producers and pipeline
stage records. Phases 6 and 7 will add optional Lightning API and bridge
behavior. Phase 8 closes docs and broad hardening. All of that remains out of
scope here.

## Source Phase Summary

- Goal: implement reusable resource trace records, fake resource profilers,
  monitor lifecycle records, and asynchronous profile persistence contracts.
- Required scope: `src/rphys/training/profiling.py` or focused training
  profiling helpers, async writer/profiler tests, package/import tests, and
  focused docs/docstrings.
- Required checkpoints: add `ResourceSample`, `ResourceTrace`, resource metric
  taxonomy, fake CPU/GPU/memory/disk/network probes, sampler execution modes,
  background thread/process lifecycle evidence, bounded buffering, dropped
  samples, backpressure, clock alignment, and async writer flush/failure
  records.
- Acceptance criteria: fake resource profilers emit timestamped traces and
  explicit unavailable/dropped/backpressure evidence; monitors stay optional,
  run-scoped, bounded, lifecycle-bound, dependency-light, and reusable by
  Native, Lightning, and future engines; async profile persistence is
  contract-only and does not become an artifact store.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/training/profiling.py` currently owns `ProfileSpanSummary`,
  `UnavailableProfileProbe`, `TrainingProfile`, `TrainingProfileRecorder`, and
  `TrainingProfiler`. Its docstring and tests still describe resource trace
  families as deferred from Phase 1.
- Phase 1 source state: `TrainingProfile` currently exposes event logs, scalar
  spans, unavailable spans, and decisions only. Phase 3 should add concrete
  resource-trace accessors and recorder methods additively rather than changing
  existing span/event behavior.
- Phase 2 source state: `src/rphys/training/probes.py` owns generic
  hook-driven model/data probe contracts and `UnavailableProbeEvidence`.
  Resource probes in this phase may reuse cadence/failure-policy concepts by
  value, but they must not depend on model tensors, batches, checkpoint IO, or
  engine hook invocation.
- Existing validation helpers: `src/rphys/training/_validation.py` provides
  primitive mapping and numeric/string coercion helpers used by current
  training records. Reuse these patterns for primitive dataclass records.
- Existing tests or harness behavior:
  `tests/unit/rphys/training/test_profiling.py`,
  `tests/contracts/test_stage15_training_profile_contract.py`, and
  `tests/package/test_import_boundaries.py` pin primitive inspection,
  no-placeholder Phase 1 behavior, and lightweight imports. Package import
  lists will need intentional updates for any exported Phase 3 names.
- Import-boundary or dependency constraints: base `rphys.training` and
  `rphys.training.profiling` must not import `psutil`, NVML, CUDA, torch,
  Lightning, numpy, pandas, scipy, plotting/video libraries, dataset SDKs,
  real network clients, or `tests.support`.

## Phase Isolation State

- Control checkout dirty-state review: reviewed `/home/samcantrill/work/rphys`;
  it was clean on `develop...origin/develop`.
- Dedicated branch/worktree status: verified clean worktree at
  `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`
  on `agent/stage-15-training-profiling-p3-resource-monitoring-profile-persistence`.
- Current `develop` base: worktree `HEAD` and `origin/develop` both resolved to
  `e7aab3e2965dbc89903a29178752e8efe2a8c1f6` during planning.
- Earlier phase dependency status: Phase 1 and Phase 2 are recorded as merged
  into `develop`; Phase 2 merge commit is recorded in the implementation plan.
- Push/PR infrastructure status: not exercised during this plan-only pass; the
  implementation workflow should verify `gh auth status` before opening the PR.
- Stop condition if isolation cannot be maintained: stop before editing product
  code if the branch diverges from `develop`, the worktree has unrelated local
  edits, or another Stage 15 phase writes into this worktree.

## In-Scope Work

- Add resource sample and grouped trace records with primitive fields for
  metric kind, metric name or series key, unit, numeric value when available,
  status, timestamp, sequence/sample index, sample interval or cadence,
  run/timeline ids, clock name/origin/alignment, process/node/rank/device
  attribution, source probe id, overhead/synchronization notes, metadata, and
  provenance.
- Add a resource metric taxonomy broad enough for accelerator utilization and
  memory, host CPU and memory, storage IO, network IO, data-loader queue or
  worker pressure, transfer/synchronization, framework/compiler activity,
  checkpoint/logging pressure, and probe health. The taxonomy must not encode
  machine-speed thresholds.
- Extend `TrainingProfile` and `TrainingProfileRecorder` additively with
  resource-trace inspection and recording helpers while preserving existing
  events/spans/unavailable/decision behavior and `TrainingResult.profiles`
  summary compatibility.
- Add resource probe protocols or structural contracts for optional resource
  producers. Required fake implementations must be deterministic, CPU-only, and
  dependency-free while emulating CPU, memory, GPU, disk, network, unavailable,
  ambiguous, and probe-health cases.
- Add monitor lifecycle records for run-scoped thread/process-style samplers:
  configured, started, sample emitted, unavailable, failed, stopped, flush
  requested/completed/failed, orphan cleanup attempted/completed/failed, and
  disabled/no-op evidence.
- Add bounded buffer/backpressure contracts that record capacity, enqueue/drop
  behavior, dropped-sample counts, oldest/newest drop policy or rejection
  policy, flush boundaries, and explicit evidence when writers or monitors fall
  behind.
- Add async profile writer contracts with a disabled/no-op fast path, bounded
  queueing, periodic flush cadence, explicit step/epoch/run flush points,
  failure records, retry/skip evidence if supported, and primitive writer
  result summaries. Writers must accept already-normalized profile records; they
  must not define a durable file format, storage backend, or artifact lifecycle.
- Add docs/docstrings for metric kinds, units, timestamp/clock alignment,
  sample cadence, overhead, synchronization, optional-probe availability,
  dropped samples, and the distinction between code spans and resource traces.
- Add focused unit, contract, package, and documentation-adjacent tests for all
  new public records and helpers.

## Out-of-Scope Work

- Native engine wiring, `TrainingPlan` lifecycle invocation, native monitor
  start/stop integration, native profile attachment beyond recorder-level unit
  behavior, and Native checkpoint/profile interaction. Those are Phase 4.
- Lightning module/API work, Lightning callbacks/profiler bridge behavior,
  Lightning rank extraction, installed-Lightning checks, and Lightning resource
  monitor lifecycle. Those are Phases 6 and 7.
- Real hardware or system dependencies, including `psutil`, NVML, CUDA, torch,
  Lightning, platform-specific disk/network libraries, real GPU probing, real
  network probing, and machine-speed or hardware-performance thresholds.
- Daemon, scheduler, long-lived service, job runner, multiprocessing manager,
  workflow runtime, or background monitor that outlives one training/profile
  run.
- Artifact stores, concrete storage backends, default filesystem writers,
  cloud/object-store behavior, schema-versioned profile files, JSONL/parquet
  codecs, file locks, or checkpoint payload serialization.
- Data-path producer wiring, Stage 9 datasource runtime changes, dataloader
  queue instrumentation, BatchOperation profiling, and real dataset fixtures.
  Those are Phase 5.
- Raw framework profiler timelines, tensor/module/batch objects, callback
  internals, optimizer state, or checkpoint payloads in public profile records.

## Assumptions

- Resource behavior is represented as timestamped traces; scalar span summaries
  remain the right shape for code-path durations such as data wait, forward,
  backward, optimizer, validation, callback, checkpoint, and writer flush time.
- Public resource records are provisional but code-backed, primitive,
  dataclass-inspectable, validated, and exported only when tested.
- Default tests use fake clocks, fake probes, fake monitor runners, and fake
  writers. Optional real system/GPU probes may be added in later phases or
  skipped acceptance checks, but they are not required for Phase 3 completion.
- A monitor thread or subprocess is a sampler execution mode, not a new
  runtime. Its public contract is lifecycle and trace evidence, not the
  implementation mechanism.
- Async persistence means nonblocking profile-record handoff and flush
  evidence. It does not imply a durable file format or storage backend.
- Cross-process and cross-device timestamp alignment is descriptive evidence.
  The implementation must not claim global ordering without explicit clock
  origin/alignment fields.

## Scope Contract

Public behavior:

- Every exported Phase 3 name is provisional public API and must be backed by
  validation and tests. Do not export aliases or placeholder classes for future
  real probes, writers, Native hooks, Lightning hooks, or storage backends.
- `ResourceSample` must represent one timestamped resource observation or one
  explicit unavailable/ambiguous/dropped/probe-health observation. Missing
  optional signals must carry a status and reason rather than silently
  disappearing.
- `ResourceTrace` must group samples from a coherent resource/probe/timeline
  series. It must preserve sample ordering, reject invalid or ambiguous sample
  ordering where the contract requires monotonic sequence/timestamps, and
  expose primitive inspection without a custom serializer.
- Metric kinds and units must be explicit. Values must reject booleans, NaNs,
  infinities, unsupported units, empty names, invalid timestamps, and negative
  durations/counts where those fields are semantically nonnegative.
- Dropped samples and backpressure are first-class evidence, not hidden logs.
  A bounded buffer must expose capacity, policy, accepted count, dropped count,
  and flush/failure state in profile records or writer results.
- Unavailable optional probes must be expressible through resource records and
  existing unavailable profile evidence. Missing dependencies, unsupported
  devices, permissions, disabled probes, and ambiguous attribution must be
  distinguishable.
- `TrainingProfile` must gain resource trace inspection without changing
  existing `events()`, `spans()`, `unavailable_probes()`,
  `as_profile_summaries()`, or current constructor behavior except for
  additive keyword-only inputs.
- Async writer contracts must be structural and dependency-free. A writer may
  be fake/in-memory in tests; it must not require file IO, background daemons,
  global registries, logging backends, or artifact stores.

Module boundaries:

- `profiling.py` should remain the public owner for resource records,
  `TrainingProfile` additions, recorder methods, and writer/monitor contracts
  unless a focused helper is needed to keep the module reviewable.
- Any focused helper must live under `src/rphys/training/`, use only
  dependency-light imports, and be re-exported from `rphys.training` only for
  code-backed public names.
- `probes.py` remains the owner of model/data hook probe records. Do not move
  Phase 2 contracts or make resource monitoring depend on concrete model/data
  probe implementations.
- `backend.py`, `plan.py`, `core.py`, `experimental.py`, `checkpoint.py`,
  `policies.py`, and datasource modules should not receive behavior changes in
  this phase except for narrow import/export or typing fallout that is proven
  necessary by tests.

Data shapes:

- Resource samples and traces must be frozen or immutable-in-practice
  dataclass-style records with tuple-backed collections and primitive mapping
  fields.
- Values are scalar primitive measurements or explicit no-value statuses, not
  tensors, arrays, file handles, framework profiler objects, device handles, or
  mutable batch/resource payloads.
- Attribution fields should include run id, timeline id, process id, node id,
  local rank, global rank, device id, resource id or mount/interface id where
  relevant, and source probe id, all optional unless required by a specific
  record constructor.
- Writer and monitor result records must be primitive and inspectable. They
  should be suitable for inclusion in `TrainingProfile` decisions, resource
  traces, unavailable evidence, or dedicated lifecycle collections without a
  serializer.

Error behavior:

- Invalid constructor inputs raise `RemotePhysTrainingError` with owner, field,
  expected, and actual context consistent with existing training records.
- Probe failures are represented by explicit failure/unavailable records unless
  the selected fake policy is fail-fast in unit tests. Runtime hooks are not in
  scope, so no engine exception handling should be added.
- Flush failures must produce writer failure records with dropped/retained
  counts and reason. They must not silently discard all evidence or raise from
  unrelated profile snapshot construction.
- Bounded buffers must define deterministic drop/reject behavior under
  overflow so tests can assert exact accepted and dropped records.

Scientific semantics:

- Resource traces are observational diagnostics. They do not imply training
  quality, physiological signal validity, statistical significance, or
  hardware performance thresholds.
- Samples must carry units and cadence/interval evidence so users can interpret
  utilization, bytes, rates, counts, memory, latency, queue depth, and probe
  health without guessing.
- Timestamp alignment must be documented as local monotonic or source-specific
  evidence. Cross-rank/process comparisons require clock-origin metadata and
  remain descriptive.
- Probe overhead and synchronization caveats must be recordable because probes
  can perturb timing, force synchronization, or miss samples.

Edge cases:

- Empty traces, unavailable-only traces, duplicated sequence ids, decreasing
  timestamps, invalid units, missing value with available status, present value
  with unavailable status, dropped-only buffers, disabled writer, writer failure
  during flush, monitor failure before first sample, monitor stop after failure,
  orphan cleanup evidence, and ambiguous device/rank attribution need focused
  tests or documented rejection.

## Scientific Contract Notes

- Sampling and temporal alignment: resource samples must use explicit
  monotonic/source timestamps, sequence evidence, cadence or interval metadata,
  and clock-origin/alignment fields. The phase must avoid claiming total global
  ordering across ranks, devices, processes, or external monitors.
- Field roles, locators, schemas, and provenance: resource metric kind, unit,
  value/status, source probe id, resource/device/process/rank attribution, and
  primitive provenance are core fields. Avoid putting required semantics only
  in unstructured metadata.
- Masking, filtering, normalization, and aggregation order: no physiological
  signal masking/filtering/normalization is performed. Any sample aggregation
  or summary must state its metric kind, unit, count, time range, and source
  trace provenance; it must not replace raw timestamped trace evidence.
- Subject identity, splits, leakage, and grouping: no subject/split labels or
  data grouping are produced in this phase. If metadata carries split/run
  labels for fake examples, they are primitive attribution only and must not
  imply dataset leakage analysis.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: numeric NaN/Inf values, invalid sampling intervals,
  missing available values, unsupported metric kinds, and invalid temporal
  ordering must fail loudly or become explicit unavailable/ambiguous evidence
  according to the record contract.

## Design Impact

- Maintainability: separating resource traces from scalar spans keeps code-path
  timing and system/device time series understandable, testable, and easier to
  extend without rewriting Phase 1 records.
- Extensibility: optional probes, monitors, and writers are structural
  contracts over primitive records, so Native, Lightning, future engines, and
  downstream projects can provide their own implementations without registry or
  daemon coupling.
- Lightweight import policy: default exports remain standard-library and
  rphys-lightweight only. Optional real probes must remain lazy and outside the
  base import path.
- Source-tree boundaries: training owns the shared profile schema; datasource
  producers, Native hooks, Lightning adapters, artifact stores, and workflow
  orchestration remain separate phase or downstream concerns.

## Future Compatibility

- Native Phase 4 should be able to start/stop any Phase 3 resource monitor,
  consume fake probes, flush an async writer at setup/step/epoch/run boundaries,
  and attach resource traces to `TrainingResult.training_profile` without
  changing record schemas.
- Lightning Phase 7 should normalize callback/profiler/resource evidence into
  the same trace and lifecycle records without Lightning-specific public
  profile families.
- Data-path Phase 5 should be able to emit resource and queue-pressure samples
  using the same metric taxonomy without importing datasources from training
  core.
- Optional real probe packages can be added later under lazy modules or
  downstream integrations if fake contracts prove the primitive schema.
- A durable profile file format may be added later as an adapter around the
  writer protocol, not as part of this phase's core contract.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Store resource readings as one scalar span or one value per step | Loses time-series behavior and cannot diagnose GPU idle, IO pressure, memory pressure, queue starvation, or missed samples. |
| Expose raw framework/system profiler objects | Breaks primitive inspection, imports optional dependencies, and creates engine-specific public profile families. |
| Add real `psutil`/NVML/CUDA probes in default scope | Violates dependency-light imports and makes CI hardware/permission dependent. |
| Make async persistence a concrete file/artifact writer | Expands into storage backend and artifact lifecycle scope reserved for future adapters or downstream repositories. |
| Add a daemon or scheduler for monitoring | Violates run-scoped profiling boundary and rphys/loom ownership split. |
| Hide overflow and writer failures in logs | Makes profile evidence incomplete and unreviewable; dropped/backpressure behavior must be testable data. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Only fake resource probes are required in default validation | Keeps Phase 3 deterministic, CPU-only, and dependency-light while locking public records. | A later optional-probe phase or downstream integration needs real probe acceptance. |
| Async writer has contracts and fake/in-memory behavior but no durable format | Avoids artifact-store and schema-version scope creep. | Users need a stable profile export format after Native/Lightning/data-path integrations prove the record schema. |
| Metric taxonomy is provisional and broad | Hardware and framework signals vary by backend, permission, driver, and runtime. | Tests or users need a metric kind that cannot be represented without ambiguous metadata. |
| Cross-process timestamp alignment remains descriptive | Correct global clock reconciliation is outside rphys core profiling. | A future distributed integration needs stronger clock-sync contracts. |

## Reviewability

- Expected PR size and shape: moderate training-profile schema PR with focused
  tests. Prefer record/protocol/fake-writer additions and package export
  updates over engine or datasource changes.
- Files and areas to inspect:
  `src/rphys/training/profiling.py`, any focused
  `src/rphys/training/*resource*` or `*profile*writer*` helper if introduced,
  `src/rphys/training/__init__.py`,
  `tests/unit/rphys/training/test_profiling.py`, new focused resource/writer
  unit tests if split, `tests/contracts/test_stage15_training_profile_contract.py`
  or a new Stage 15 resource contract test,
  `tests/package/test_import.py`, and
  `tests/package/test_import_boundaries.py`.
- Scope-control checks: no Native/Lightning/data-path behavior changes, no
  real optional profiler imports, no file/artifact backend, no daemon/scheduler
  semantics, no raw framework objects, no performance thresholds, and no
  exported unimplemented names.

## Implementation Steps

1. Add resource metric/status vocabulary and immutable resource sample/trace
   records with primitive validation, ordering rules, unavailable/ambiguous
   evidence, units, cadence, attribution, clock alignment, overhead, and
   provenance.
2. Extend `TrainingProfile` and `TrainingProfileRecorder` with resource trace
   storage, filtering, recording, and snapshot behavior while preserving
   existing event/span/unavailable/decision tests and summary compatibility.
3. Add resource probe and monitor contracts plus deterministic fake probes for
   CPU, memory, GPU, disk, network, unavailable, ambiguous, dropped, and
   probe-health scenarios.
4. Add bounded buffer and monitor lifecycle records for thread/process-style
   samplers, including deterministic overflow policy, backpressure, dropped
   sample counts, start/stop/failure/cleanup evidence, and disabled/no-op
   behavior.
5. Add async profile writer contracts and fake writer coverage for bounded
   queueing, periodic and step/epoch/run flush points, disabled fast path,
   flush success/failure records, retained/dropped counts, and failure reasons.
6. Update public exports, package/import-boundary tests, contracts, and concise
   docs/docstrings for metric taxonomy, units, sampling, alignment,
   synchronization, overhead, probe availability, and persistence boundaries.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: public exports include only
  implemented Phase 3 names; importing `rphys`, `rphys.training`, and
  `rphys.training.profiling` does not load `psutil`, NVML/CUDA, torch,
  Lightning, numpy, pandas, scipy, plotting/video stacks, real network clients,
  datasource runtime modules beyond existing allowed imports, or `tests.support`.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/training/test_profiling.py` and, if the
  implementation is split, focused tests such as
  `tests/unit/rphys/training/test_resource_monitoring.py` or
  `tests/unit/rphys/training/test_profile_writers.py`
- Required assertions or deferral reason: resource sample/trace construction,
  invalid values, units, statuses, ordering, primitive mappings, sample
  cadence, clock alignment, unavailable/ambiguous statuses, fake probes,
  monitor lifecycle records, bounded buffer overflow, dropped/backpressure
  evidence, async writer flush success/failure, disabled no-op behavior, and
  `TrainingProfileRecorder` snapshots with resource traces.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_stage15_training_profile_contract.py`
  or a new focused Stage 15 resource profile contract test
- Required assertions or deferral reason: public resource records remain
  dataclass/primitive-inspection friendly; `TrainingProfile` resource trace
  helpers are additive; existing Stage 15 event/span/profile behavior remains
  compatible; no raw framework timelines, device handles, tensors, batch
  objects, checkpoint payloads, writer backends, or mutable queues appear in
  public records.

### Integration Suite

- Status: deferred for engine/data-path wiring; required only for any
  non-engine fake monitor lifecycle helper that cannot be validated by unit
  tests
- Expected paths: prefer none for engine behavior in this phase. If needed, add
  a small dependency-free test under `tests/integration/` that exercises a fake
  monitor and fake writer without `NativeTrainingEngine`, Lightning, or
  datasource producers.
- Required assertions or deferral reason: Native, Lightning, and data-path
  integration are explicitly deferred to Phases 4, 5, and 7. Do not add
  integration tests that require real hardware, framework imports, schedulers,
  or file/artifact stores.

### E2E Suite

- Status: deferred
- Expected paths: none expected
- Required assertions or deferral reason: no end-to-end training, Lightning,
  data-path, or artifact workflow is in Phase 3 scope. E2E coverage belongs
  after Native/Lightning/data-path producers are wired in later phases.

### Acceptance Suite

- Status: deferred by default; optional only if a safe marker already exists or
  the executor adds a skip-by-default marker with explicit unavailable evidence
- Markers affected: optional real resource-probe marker only if implemented
- Required assertions or deferral reason: default Phase 3 completion must not
  depend on GPU, NVML, `psutil`, torch, Lightning, network devices, or machine
  speed. Optional real-probe acceptance may reduce risk but must skip cleanly
  when dependencies, hardware, permissions, or safe versions are absent.

## Risks

- Public schema breadth could drift into engine, data-path, writer-backend, or
  hardware-specific behavior. Stop if a field cannot be explained
  engine-neutrally.
- Async writer semantics could accidentally become a storage API. Keep writes
  contract/fake-only and record flush evidence rather than defining file
  formats.
- Thread/process sampler examples could imply daemon/scheduler ownership. Keep
  lifecycle records run-scoped and deterministic.
- Metric taxonomy may be too broad or too vague. Prefer typed metric kinds and
  units with metadata as secondary evidence; reopen planning only if validation
  cannot distinguish required blind spots.
- Adding resource traces to `TrainingProfile` could break Phase 1 contract
  tests that asserted no resource traces before Phase 3. Update those tests
  intentionally to assert the new additive contract and preserve existing
  behavior.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/training/test_profiling.py
uv run pytest tests/contracts/test_stage15_training_profile_contract.py
make test-package
```

If focused split tests are added:

```sh
uv run pytest tests/unit/rphys/training/test_resource_monitoring.py
uv run pytest tests/unit/rphys/training/test_profile_writers.py
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-package
make validate-pr
make test-summary
uv lock --check
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: records/taxonomy first, `TrainingProfile`
  additive storage second, fake probes/monitor lifecycle third, bounded buffer
  and writer contracts fourth, exports/docs/tests last.
- Tests to run with each slice: run the focused unit file after each record or
  helper slice; run contract and package checks after public exports or import
  changes; reserve broad validation for final PR preparation.
- Decisions the executor must not revisit: resource behavior is a timestamped
  trace, not one value per step; default probes are fake and dependency-free;
  monitors are run-scoped optional components; async persistence is not an
  artifact store; Native, Lightning, real hardware, data-path producer, and
  scheduler behavior are out of scope.
- Conditions that require stopping for the manager: a required public field
  implies real hardware dependencies, global clock synchronization, a durable
  file format, a scheduler/daemon, Native or Lightning API changes, data-path
  producer wiring, or a breaking change to Phase 1/2 public contracts.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed; expanded-path risks addressed
  in this plan
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this branch at
  `docs/roadmap/stage-15/phases/resource-monitoring-profile-persistence.md`
- Final phase execution plan: this artifact is ready for implementation
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: no separate refinement requested or needed
- Pre-submit blocker gate: pending implementation
- PR preparation: pending implementation
- Automated review: pending implementation
- Merge result: pending implementation
- Cleanup: pending implementation
- Remaining blockers: none known for Phase 3 planning
