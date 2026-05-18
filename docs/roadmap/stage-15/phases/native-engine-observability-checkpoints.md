# Phase 4 Execution Plan: Native Engine Observability And Checkpoints

## Metadata

- Status: final phase execution plan; expanded-path concerns addressed; ready
  for implementation
- Roadmap stage: `v15`
- Feature focus: training performance profiling and data-path optimization
- Stage descriptor: Training Performance Profiling And Data-Path Optimization
- Phase descriptor: Native Engine Observability And Checkpoints
- PR title: `Stage 15 Training Performance Profiling And Data-Path Optimization - Phase 4: Native Engine Observability And Checkpoints`
- Branch: `agent/stage-15-training-profiling-p4-native-engine-observability-checkpoints`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p4-native-engine-observability-checkpoints`
- Phase execution plan path: `docs/roadmap/stage-15/phases/native-engine-observability-checkpoints.md`
- Full plan: `docs/roadmap/stage-15/implementation-plan.md`
- Planning document: `docs/roadmap/stage-15/planning.md`
- Source phase: `docs/roadmap/stage-15/implementation-plan.md`, `## Phase 4: Native Engine Observability And Checkpoints`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation plan approved; Phase 1, Phase 2, and
  Phase 3 are merged into `develop`; this artifact captures native-only
  integration details for shared event, profile, resource monitor, async
  writer, probe, checkpoint, restart, and policy records
- Draft pass: complete
- Refine pass: not needed; public API, scientific-contract, import-boundary,
  checkpoint-boundary, reviewability, and blocker criteria are captured here
- Setup limitations: existing manager-created worktree and branch were
  verified instead of creating a new branch/worktree; no fetch, push, broad
  validation, or PR action was performed in this planning pass
- Blockers: none for Phase 4 implementation startup

## Objective

Make `NativeTrainingEngine` the reference implementation that populates the
shared Stage 15 observability and restart contracts during real native runs.
The phase wires native setup, teardown, loop regions, resource monitor
lifecycle, async profile writer flushes, model/data probe invocation,
checkpoint save/restore/prune evidence, and restart selector resolution into
`TrainingResult.training_profile` without creating native-only profile
families, a checkpoint storage backend, Lightning integration, data-path
pipeline instrumentation, real hardware probes, or an artifact store.

## Full-Plan Context

Phase 1 added timestamped training events, append-only event logs, scalar
spans, unavailable profile evidence, `TrainingProfileRecorder`, and optional
`TrainingResult.training_profile`. Phase 2 added generic probe records,
checkpoint catalogs, restart selectors, and precision/compile/kernel policy
records. Phase 3 added resource traces, fake resource probes, run-scoped
resource monitors, bounded buffers, and async writer contracts.

Phase 4 is the first engine pressure test for those shared contracts. It should
modify the native loop and plan surface only as far as needed to invoke the
already-merged contracts. Phase 5 owns Stage 9 data-path and `BatchOperation`
pipeline evidence. Phases 6 and 7 own optional Lightning API and bridge
behavior. Phase 8 owns final docs, tiers, examples, and broad hardening. Those
future phases must not be pulled into this PR.

## Source Phase Summary

- Goal: make Native the reference integration for shared observability, probe,
  resource, checkpoint, and restart contracts.
- Required scope: `src/rphys/training/backend.py`,
  `src/rphys/training/plan.py`, narrowly needed `results.py`,
  `checkpoint.py`, `profiling.py`, `probes.py`, package exports only if a
  code-backed public native hook type is added, native unit tests, Stage 15
  contract tests, and native integration tests.
- Required checkpoints: emit setup/teardown/event-log evidence; record scalar
  spans for native-owned regions; start, sample, flush, and stop resource
  monitors; append and flush async profile writers; invoke model/data probes at
  native-owned hook points; resolve restart selectors against checkpoint
  catalogs before execution; call structural checkpoint hooks for
  save/restore/prune; attach complete native `TrainingProfile` evidence to the
  returned `TrainingResult`.
- Acceptance criteria: successful, stopped, and failed native runs produce
  primitive, inspectable profile/checkpoint/probe/resource evidence; fail-loud
  observer behavior and best-effort teardown evidence are preserved; public
  imports stay dependency-light; no native-only public profile/checkpoint
  family is introduced.

## Current Source And Harness Findings

- `src/rphys/training/backend.py` currently owns the native loop. It emits only
  loop and step events through `emit_training_event`, returns unavailable
  `ProfileSummary("native.step")` records, and does not attach
  `TrainingResult.training_profile`.
- `src/rphys/training/plan.py` currently owns assembled inputs and native
  hooks: batch iterables, max step/epoch limits, `device_mover`, `optimizer`,
  `scheduler`, `backward`, event sinks, callbacks, `TrainingProfiler`
  observers, metadata, and provenance. It deliberately has no generic
  `engine_config`.
- `src/rphys/training/events.py` already includes the Stage 15 phases needed
  by Native: `setup`, `teardown`, `data_wait`, `device_transfer`,
  `validation`, `checkpoint`, `profiling_summary`, and generic `stage`.
- `src/rphys/training/profiling.py` owns `TrainingProfileRecorder`,
  `ProfileSpanSummary`, `ResourceMonitor`, fake resource probes,
  `AsyncTrainingProfileWriter`, writer result records, resource traces, and
  monitor lifecycle records. These are dependency-free and suitable for native
  tests.
- `src/rphys/training/probes.py` owns `TrainingProbe`, `ProbeHookPoint`,
  `ModelProbeSummary`, `DataProbeSummary`, unavailable probe evidence, and
  Stage 9 aligned `TrainingPipelineStage` names. Phase 4 should invoke generic
  model/data probes around native loop hook points but not add Stage 9 data
  producer hooks.
- `src/rphys/training/checkpoint.py` owns `CheckpointCatalog`,
  `CheckpointSelection`, save/restore/prune policies, result records, and
  deterministic selector behavior. It does not own storage, serialization, or
  a writer.
- Existing tests include `tests/unit/rphys/training/test_backend.py`,
  `tests/unit/rphys/training/test_plan.py`,
  `tests/unit/rphys/training/test_checkpoint.py`,
  `tests/unit/rphys/training/test_profiling.py`,
  `tests/unit/rphys/training/test_probes.py`,
  `tests/contracts/test_stage15_training_profile_contract.py`,
  `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`,
  `tests/contracts/test_stage12_observability_contract.py`,
  package import tests, and Stage 12 synthetic native integration flows.
- Import-boundary tests forbid base training imports from loading Lightning,
  torch, CUDA/NVML, numpy, pandas, scipy, plotting/video libraries, system
  profiler libraries, dataset SDKs, or `tests.support`.

## Phase Isolation State

- Control checkout dirty-state review: verified the requested worktree was
  clean before creating this plan.
- Dedicated branch/worktree status: verified clean worktree at
  `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p4-native-engine-observability-checkpoints`
  on `agent/stage-15-training-profiling-p4-native-engine-observability-checkpoints`.
- Current base: worktree `HEAD`, local `develop`, and `origin/develop` resolved
  to `cca845e` when this plan was drafted; the branch was at the Phase 3
  merge-record base.
- Earlier phase dependency status: Phase 1, Phase 2, and Phase 3 are recorded
  as merged in `docs/roadmap/stage-15/implementation-plan.md`.
- Push/PR infrastructure status: not exercised during this plan-only pass; the
  implementation workflow should verify `gh auth status` before opening the PR.
- Stop condition if isolation cannot be maintained: stop before editing product
  code if this branch diverges unexpectedly from `develop`, the worktree has
  unrelated local edits, or another Stage 15 phase writes into this worktree.

## In-Scope Work

- Extend `TrainingPlan` with explicit typed native integration inputs only.
  Acceptable additions include recorder/profile construction knobs, resource
  monitors, async profile writers, generic training probes, checkpoint save,
  restore, and prune hooks, checkpoint catalogs, checkpoint save/prune/restore
  policies, restart selectors, run/timeline attribution, and optional
  rank/device attribution. Do not add `engine_config`.
- Add structural protocols or focused dataclass records only when existing
  Phase 1-3 types cannot represent native hook inputs or outputs. Keep any new
  public names in `src/rphys/training/` code-backed, tested, documented, and
  package-exported intentionally.
- Create a native run context or private helper in `backend.py` if it keeps the
  loop reviewable. It may hold a `TrainingProfileRecorder`, run/timeline ids,
  current mode/split/epoch/step/batch attribution, active monitors, writers,
  checkpoint catalog state, and teardown state.
- Emit and record timestamped native events for setup started/completed,
  teardown started/completed, loop start/completion/failure, epoch or generic
  stage boundaries where useful, data wait or batch fetch, device transfer,
  learner step/forward, objective validation, backward, optimizer step,
  scheduler step, validation sub-loop, checkpoint operations, callback
  observation, profile summary, and failure cleanup.
- Record scalar spans for native-owned code regions: setup, data wait or batch
  fetch, pre/post device transfer, learner step/forward, learner output
  validation, backward, optimizer step, scheduler step, validation, callback
  fanout, checkpoint save/restore/prune, resource monitor start/stop/sample,
  writer append/flush, teardown, and failure cleanup.
- Start configured `ResourceMonitor` instances after setup begins and stop them
  during teardown or failure cleanup. Collect deterministic samples at
  lifecycle points that are cheap and explicit: setup, step boundary, epoch
  boundary, checkpoint boundary, failure, and teardown. Record monitor
  lifecycle events and resource samples/traces into the profile.
- Append normalized profile records to configured `AsyncTrainingProfileWriter`
  instances without defining a storage format. Flush at step, epoch, checkpoint,
  failure, and run boundaries where configured or cheap. Record all append and
  flush results, including disabled, skipped, failed, dropped, and backpressure
  evidence.
- Invoke generic `TrainingProbe` instances with primitive context mappings at
  native-owned `ProbeHookPoint`s: setup, teardown, failure, epoch started,
  epoch completed, step started, step completed, data wait or batch fetch,
  pre-device-transfer, post-device-transfer, forward, objective, backward,
  optimizer step, scheduler step, validation, checkpoint, and callback.
- Normalize probe outputs into `TrainingProfile` evidence without storing raw
  model objects, tensors, batches, optimizers, dataloaders, or framework
  objects. Model and data probe summaries must carry run/timeline, split,
  epoch, step, batch, rank/process/device, cadence, selector, and failure
  policy evidence.
- Resolve `CheckpointSelection` or `CheckpointRestorePolicy` against a
  `CheckpointCatalog` before native execution. Record
  `CheckpointSelectionResult` and `CheckpointRestoreResult` evidence even when
  restore is skipped, unavailable, or unsupported.
- Add structural checkpoint hooks for restore, save, and prune. Hooks may be
  supplied by the caller or fake tests and must return existing
  `CheckpointRestoreResult`, `CheckpointSaveResult`, `CheckpointPruneResult`,
  `CheckpointRef`, or catalog evidence. Native must not serialize learner,
  optimizer, scheduler, or batch payloads itself.
- Evaluate checkpoint save policy at explicit native boundaries: by step, by
  epoch, metric-triggered when relevant metric evidence is available,
  on-failure, and final. Add refs/results to the in-memory catalog evidence
  only through normalized checkpoint records.
- Apply prune policy after save boundaries where configured. Record kept and
  dropped refs with `CheckpointRetentionReason`; call delete/prune hooks only
  when supplied; otherwise record unsupported or unavailable evidence.
- Attach `TrainingProfile` to every native `TrainingResult` path that starts
  setup: completed, failed, stopped after setup, validation/test/predict, and
  failure during setup/teardown. Missing training batches before setup may
  remain a stopped result with no profile if no runtime was started, but that
  behavior must be explicit and tested.
- Keep `TrainingResult.profiles` compatibility summaries deterministic. If
  derived from `training_profile.as_profile_summaries()`, preserve existing
  profile-summary semantics and avoid duplicate unavailable placeholders.
- Preserve observer/callback fail-loud behavior. Observer errors should still
  fail the native run, emit failure evidence when possible, and run best-effort
  teardown after setup has started.
- Add docstrings or focused docs for native-owned hook points, checkpoint
  serialization boundary, resource monitor lifecycle, async writer evidence,
  and failure behavior when those public APIs are introduced or changed.

## Out-of-Scope Work

- Lightning imports, `rphys.training.lightning`, Lightning callback/profiler
  bridges, Lightning checkpoint callback mapping, `ckpt_path`, distributed
  strategy parity, installed-Lightning validation, and Lightning security
  preflight. Those are Phases 6 and 7.
- Stage 9 data-path pipeline instrumentation, datasource/cache/prepared
  producer changes, data-path benchmark/profile producers, queue starvation
  measurement over real loaders, `BatchOperation` equivalence work, and
  dataset fixtures. Those are Phase 5.
- Real GPU/system/hardware probes, psutil, NVML, CUDA, torch profiler,
  platform-specific disk/network readers, real network probes, hardware
  availability assumptions, and machine-speed thresholds.
- Artifact stores, default filesystem checkpoint writers, cloud/object storage,
  file locks, durable profile/checkpoint codecs, JSONL/parquet formats, pickle
  payloads, and core-owned serialization of model/optimizer/scheduler state.
- Workflow runtime, scheduler, job runner, daemon, monitor service,
  multiprocessing manager, auto-tuning, dashboards, cost reporting, or
  long-lived background work after a native run ends.
- New native-specific public profile, checkpoint, restart, or probe result
  families. Native must populate the shared Stage 15 records.
- Broad docs/examples/tier closeout beyond narrow docstrings and native API
  notes needed to make Phase 4 behavior reviewable. Phase 8 owns final docs.

## Assumptions

- Phase 1-3 contracts are the source of truth. Phase 4 should extend them only
  when native pressure exposes a concrete missing field or helper, and those
  additions must remain additive and engine-neutral.
- Default validation is CPU-only, deterministic, synthetic, dependency-light,
  and threshold-free. Fake resource probes, fake profile writers, fake
  checkpoint hooks, fake training probes, and fake clocks are sufficient.
- Native observes already-built batch iterables. It does not build dataloaders,
  inspect Stage 9 sources, or materialize data-path profile records.
- Checkpoint hooks are caller-supplied capabilities. Native coordinates
  timing, policies, selection, and evidence, but the hook owns any actual save,
  restore, delete, or payload handling.
- Resource monitor lifecycle is run-scoped. A monitor can emulate thread or
  process mode through existing records, but implementation must not spawn a
  durable daemon or require multiprocessing for default tests.
- Timestamps and sequence ids provide per-run/per-timeline evidence only. The
  implementation must not claim cross-process global ordering without explicit
  clock-origin evidence.
- Probe context mappings are primitive evidence plus references needed by
  caller-supplied probes. Public records must store only summaries and
  primitive attribution, not live objects.

## Scope Contract

Public behavior:

- `NativeTrainingEngine.fit`, `validate`, `test`, and `predict` continue to
  return `TrainingResult`. When setup starts, the returned result should carry
  `training_profile` containing native events, scalar spans, monitor/resource
  evidence, writer results, probe evidence, checkpoint selection/restore/save
  /prune evidence, and teardown/failure evidence as applicable.
- Native event and span names must be stable enough for tests and examples but
  not overfit to implementation-private helpers. Prefer field-driven evidence:
  phase, status, stage name, mode, split, epoch, step, batch, run id, timeline
  id, rank/process/device, metadata, and provenance.
- Native checkpoint behavior is coordination, not serialization. The public
  contract is selection/result/catalog/ref/prune evidence. The actual payload,
  file naming, storage location, save/delete mechanics, and restore mechanics
  stay behind structural hooks supplied by callers or tests.
- Restart selection must be deterministic. If the catalog has no matching ref,
  native records an unavailable selection/restore result and either starts from
  scratch or stops according to the explicit restore policy. Do not silently
  pick an arbitrary path.
- Resource monitors and async writers must be optional. Disabled, unavailable,
  unsupported, failed, backpressured, and dropped-sample states are profile
  evidence, not hidden logs.
- Probe failures follow `ProbeFailurePolicy`: record-and-continue failures
  become unavailable/failure evidence; fail-run policies fail the native run
  after recording failure and teardown evidence when possible; unavailable
  policies must not silently disappear.
- Callback and event sink behavior remains observe-only. Callback return values
  do not control the loop. Sink/callback exceptions remain fail-loud and are
  reflected in result failure/profile evidence when setup has started.
- `TrainingPlan` remains assembled-object configuration. It may grow explicit
  typed fields but must not become a broad config bag or project workflow
  descriptor.

Module boundaries:

- `backend.py` owns native loop orchestration, event/span/probe/monitor/writer
  invocation, profile attachment, checkpoint policy boundary checks, and
  failure/teardown ordering.
- `plan.py` owns typed user-supplied native integration inputs and validation:
  monitors, writers, probes, checkpoint policies/catalogs/selectors/hooks, and
  attribution defaults if added.
- `checkpoint.py` remains the shared checkpoint contract owner. Native may add
  narrowly needed structural hook protocols or helper functions here only if
  they are engine-neutral and tested outside Native.
- `profiling.py` remains the shared profile/resource/writer contract owner.
  Native should consume its types rather than adding backend-specific profile
  records.
- `probes.py` remains the shared probe contract owner. Native should invoke
  `TrainingProbe` and normalize existing model/data/unavailable summaries
  rather than adding probe subclasses for native internals.
- `results.py` should change only if profile attachment or compatibility
  summary projection needs a narrow additive helper.
- Package exports are updated only for code-backed public names required by
  this phase.

Data shapes:

- Profile, event, resource, probe, checkpoint, and policy evidence must remain
  dataclass-inspectable and primitive at public leaves: strings, numbers,
  booleans, `None`, tuples, and primitive mappings.
- Public records must not contain `Batch`, `FieldValue`, learner, model,
  optimizer, scheduler, dataloader, tensor, module, file handle, profile writer
  backend, resource probe object, checkpoint payload, or callback object.
- Native context passed to probes/hooks may include live objects when needed by
  caller-supplied code, but any persisted evidence must contain primitive
  summaries and attribution only.
- Metric-triggered checkpoint records must identify metric name, direction,
  value, mode/split, epoch/step, and unavailable/unsupported cases when the
  metric is absent.

Error behavior:

- Invalid plan fields and hook results raise `RemotePhysTrainingError` with
  owner, field, expected, and actual context consistent with existing training
  records.
- Failures after setup begins should produce a failed `TrainingResult` with
  failure text, failure event, failure span or unavailable evidence, writer
  failure/flush evidence when available, checkpoint failure evidence when
  applicable, and best-effort teardown event.
- Teardown failures should not erase earlier failure evidence. If teardown
  itself fails, record a teardown failure event/decision and return a failed
  result with the original failure preserved in metadata or provenance.
- Hook returns that do not match expected result/ref/catalog types are native
  integration errors unless the corresponding policy says unsupported evidence
  is acceptable.

Import boundaries:

- Base `rphys.training` imports must remain dependency-light. Do not import
  Lightning, torch, CUDA/NVML, psutil, numpy, pandas, scipy, plotting/video
  libraries, dataset SDKs, platform profiler libraries, real network clients,
  or `tests.support`.
- Test-only fakes belong in tests or existing fake dependency-free helpers.
  Production modules must not import `tests.support`.

## Scientific Contract Notes

- Profiling must not change learner semantics. The same input batches, output
  validation, backward call, optimizer step, scheduler step, and result
  summaries should occur when profiling/checkpoint hooks are disabled.
- Scalar spans measure code-region duration evidence, not physiological signal
  values or resource utilization. Resource behavior remains timestamped trace
  evidence with metric kind, unit, cadence, attribution, and unavailable state.
- Native must be explicit about synchronization. If a span or probe would
  require synchronization, the record must document that fact; default CPU-only
  tests must not introduce hidden device synchronization.
- Checkpoint and restart records describe what was selected, attempted, saved,
  restored, pruned, kept, dropped, skipped, unavailable, or unsupported. They
  must not imply that rphys owns checkpoint payload correctness or backend
  serialization.
- Probe summaries may describe model/data health, nonfinite counts, masks,
  shapes, dtypes, labels, gradients, updates, or activations only as summaries.
  Raw tensors, raw batches, and sample payloads are out of public evidence.
- Metric and objective evidence must preserve mode/split/epoch/step/batch
  attribution so checkpoint policies and profile summaries do not hide leakage
  risks or validation/train boundary confusion.
- Failure records must distinguish missing optional evidence, unsupported
  hooks, unavailable probes, invalid inputs, and runtime exceptions.

## Design Impact

- `TrainingPlan` becomes the typed native integration boundary for Stage 15
  observability without becoming an experiment runner or config registry.
- `NativeTrainingEngine` becomes the reference consumer of shared Stage 15
  records, which gives Phases 6 and 7 a concrete behavior target for Lightning
  parity without copying native internals.
- Shared profile/checkpoint/probe contracts may receive small additive helpers
  if native integration exposes a concrete missing operation, but this phase
  should prefer private native orchestration over widening public API.
- The old `ProfileSummary("native.step", unavailable)` placeholder should be
  replaced or made deterministic from the richer `TrainingProfile` so callers
  get one coherent profile source.

## Future Compatibility

- Lightning and future engines should be able to produce the same event, span,
  resource, probe, writer, checkpoint, and restart records from their own
  adapter hooks.
- Phase 5 data-path producers should be able to add pipeline-stage evidence
  later without Native owning Stage 9 datasource concepts.
- Real resource probes and concrete checkpoint writers can be added later as
  optional components that satisfy existing structural contracts.
- Final docs and tier/restart closeout can summarize native evidence without
  changing the Phase 4 schema if this phase keeps fields primitive and
  engine-neutral.

## Alternatives Rejected

- Native-specific `NativeProfile`, `NativeCheckpoint`, or `NativeRestart`
  records: rejected because Stage 15 explicitly standardizes shared records
  across Native, Lightning, and future engines.
- Generic `engine_config` on `TrainingPlan`: rejected because it hides public
  contracts and makes validation/review harder.
- Default filesystem checkpoint writer: rejected because Phase 4 coordinates
  evidence and hooks only; storage backend and artifact lifecycle are out of
  scope.
- Real CPU/GPU/disk/network profilers in default validation: rejected because
  Phase 4 must stay dependency-light, deterministic, and hardware-independent.
- Stage 9 datasource hook integration in Native: rejected because Phase 5 owns
  data-path pipeline probes and BatchOperation evidence.

## Debt Introduced

- Native may initially use private helper functions/classes in `backend.py` to
  keep the public API narrow. Revisit only if Lightning or data-path phases need
  the same orchestration as an engine-neutral helper.
- Checkpoint hooks remain structural and caller-supplied. A future optional
  writer may add storage ergonomics, but Phase 4 should not create one.
- Resource monitor sampling cadence in Native is lifecycle-bound and
  deterministic rather than continuous real-time. Real async cadence and
  hardware-specific sampling remain optional future work.
- Public examples may remain narrow until Phase 8, provided tests and docstrings
  explain native hook boundaries and result evidence.

## Reviewability

- Keep the PR reviewable as one native integration change over existing shared
  contracts. Avoid broad rewrites of checkpoint/profiling/probe schemas unless
  a failing native test proves an additive helper is required.
- Expected production file ownership:
  `src/rphys/training/backend.py`,
  `src/rphys/training/plan.py`,
  `src/rphys/training/results.py` if needed,
  `src/rphys/training/checkpoint.py` if a shared structural hook/helper is
  needed,
  `src/rphys/training/profiling.py` if a shared recorder/writer helper is
  needed,
  `src/rphys/training/probes.py` if a shared probe-normalization helper is
  needed,
  `src/rphys/training/__init__.py` and package tests only for intentional
  public exports.
- Expected test ownership:
  `tests/unit/rphys/training/test_backend.py`,
  `tests/unit/rphys/training/test_plan.py`,
  `tests/unit/rphys/training/test_checkpoint.py`,
  `tests/unit/rphys/training/test_profiling.py`,
  `tests/unit/rphys/training/test_probes.py`,
  `tests/contracts/test_stage15_training_profile_contract.py`,
  `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`,
  `tests/contracts/test_stage12_observability_contract.py`,
  `tests/integration/test_stage15_native_observability_flow.py` or a focused
  Stage 15 native integration file,
  `tests/integration/test_stage12_synthetic_training_flow.py` only if existing
  native flow expectations need additive coverage,
  `tests/package/test_import.py`,
  and `tests/package/test_import_boundaries.py`.
- Good PR slices: plan/API fields first, recorder/event/span attachment,
  monitor/writer lifecycle, probe invocation, checkpoint/restart hooks,
  failure/teardown evidence, then package/import/docs cleanup.
- Stop and split if the implementation needs more than a small additive shared
  schema change, rewrites checkpoint selection, imports data-path runtime
  modules into training core, or introduces real storage/profiler dependencies.

## Implementation Steps

1. Reconfirm the branch is clean and based on `develop`.
2. Add typed `TrainingPlan` inputs for native observability and checkpoint
   coordination. Validate iterable/structural fields with existing
   `RemotePhysTrainingError` patterns.
3. Add private native run/profile helper(s) in `backend.py` to centralize
   run/timeline attribution, event recording, span recording, probe context
   construction, monitor lifecycle capture, writer append/flush capture, and
   checkpoint evidence capture.
4. Replace direct `_emit_loop_event` and `_emit_step_event` usage with helpers
   that both fan out to sinks/callbacks and record events into
   `TrainingProfileRecorder`.
5. Wrap setup, teardown, batch fetch/data wait, device transfer, learner step,
   output validation, backward, optimizer, scheduler, validation, checkpoint,
   callback, writer, monitor, and failure-cleanup regions with scalar spans.
6. Integrate resource monitors using existing `ResourceMonitor` methods:
   configure/start, collect deterministic samples, request flush, stop, and
   cleanup orphan when failure paths require it. Record lifecycle events and
   samples in the recorder.
7. Integrate async profile writers using `AsyncTrainingProfileWriter.append`,
   `flush_step`, `flush_epoch`, and `flush_run`. Record append and flush
   results even when disabled, skipped, failed, or backpressured.
8. Invoke generic `TrainingProbe.collect(context)` at native hook points.
   Normalize `ModelProbeSummary`, `DataProbeSummary`, nested model/data probe
   summary wrappers, and `UnavailableProbeEvidence` into profile evidence or
   decisions without storing raw probe context.
9. Resolve restart selectors/catalogs before loop execution. Record selection
   and restore evidence and call restore hooks only when supplied and
   supported.
10. Evaluate checkpoint save policies at step, epoch, failure, metric, and final
    boundaries. Call save hooks, update catalog evidence from returned refs,
    and record save events/spans/results.
11. Apply prune policies after save boundaries. Call prune hooks when supplied,
    record kept/dropped evidence, and never delete or serialize artifacts
    directly from Native.
12. Ensure every result path that starts setup attaches a `TrainingProfile`,
    compatibility `profiles`, result metadata/provenance, and clear failure
    information.
13. Add or update focused docs/docstrings for any new public plan fields,
    hooks, and native checkpoint serialization boundary.
14. Run focused tests first, then required suite-level validation.

## Test Plan

### Package Suite

- Update `tests/package/test_import.py` only for new intentionally exported
  public names.
- Extend `tests/package/test_import_boundaries.py` if new training modules or
  exports are added. Assert base training imports still avoid Lightning, torch,
  CUDA/NVML, psutil, numpy, pandas, scipy, plotting/video libraries, dataset
  SDKs, real network clients, and `tests.support`.

### Unit Suite

- `tests/unit/rphys/training/test_plan.py`: typed field validation for
  monitors, writers, probes, checkpoint policies/catalog/selectors/hooks, and
  attribution defaults; invalid hook/probe/writer/monitor objects fail with
  `RemotePhysTrainingError`.
- `tests/unit/rphys/training/test_backend.py`: native event/span attachment,
  setup/teardown ordering, data wait/device transfer/learner/objective/backward
  /optimizer/scheduler spans, callback fail-loud behavior, stopped paths,
  validation/test/predict profile attachment, and failure cleanup evidence.
- `tests/unit/rphys/training/test_checkpoint.py`: native-facing helper or hook
  behavior if added; restore/save/prune result validation remains shared and
  deterministic.
- `tests/unit/rphys/training/test_profiling.py`: recorder/writer/monitor helper
  behavior if native pressure requires additive shared helpers.
- `tests/unit/rphys/training/test_probes.py`: probe context normalization or
  unavailable/fail-run behavior if shared helpers are added.

### Contract Suite

- `tests/contracts/test_stage15_training_profile_contract.py`: native
  `TrainingResult.training_profile` contains event logs, scalar spans,
  resource traces, monitor lifecycle records, writer results, decisions, and
  compatibility summaries without native-only record families.
- `tests/contracts/test_stage15_probe_checkpoint_policy_contract.py`: native
  execution consumes shared probe, checkpoint, restart, save, prune, restore,
  and policy records without changing their primitive inspection semantics.
- `tests/contracts/test_stage12_observability_contract.py`: Stage 12 event,
  callback, sink, and `TrainingResult.profiles` compatibility still passes.
- Existing checkpoint/profile/probe contract tests continue to pass unchanged
  except for additive assertions tied to native integration.

### Integration Suite

- Add `tests/integration/test_stage15_native_observability_flow.py` or
  equivalent focused integration coverage using synthetic `Batch` objects,
  fake learners, fake resource probes, fake profile writers, fake training
  probes, and fake checkpoint hooks.
- Cover completed native fit with validation, stopped no-batch path, native
  failure after setup, callback failure, restore from latest/best/rewind
  catalog selection, keep-last/keep-best prune evidence, final/failure
  checkpoint evidence, writer flush evidence, and monitor unavailable evidence.
- Keep integration tests CPU-only, deterministic, license-safe, and free of
  optional dependencies.

### E2E Suite

- No required e2e coverage for Phase 4 unless a public native workflow already
  has a lightweight e2e fixture. Do not create broad workflow e2e tests to
  compensate for missing unit/integration coverage.

### Acceptance Suite

- No required acceptance coverage for Phase 4. Real GPU, system profilers,
  real storage, real Lightning, long-running training, and real dataset checks
  remain optional future work and must not block this phase.

## Risks

- Native loop instrumentation can accidentally change execution order. Mitigate
  with tests that assert existing device/backward/optimizer/scheduler call
  order with profiling disabled and enabled.
- Profile evidence can become too broad or backend-specific. Mitigate by using
  existing Stage 15 shared records and rejecting native-only public families.
- Checkpoint hooks can imply rphys-owned storage. Mitigate by documenting and
  testing that Native records evidence and delegates all payload work to hooks.
- Failure handling can drop teardown or writer evidence. Mitigate with
  synthetic failures in setup, learner step, callback, checkpoint hook, writer,
  monitor, probe, and teardown paths.
- Probe contexts can leak live objects into public records. Mitigate with
  contract tests using `dataclasses.asdict` or equivalent primitive inspection
  and explicit assertions against raw batches/tensors/framework objects.
- Import-boundary drift can pull optional dependencies into default imports.
  Mitigate with package import-boundary tests after every public export change.

## Blocker Criteria

- Any need to import Lightning, torch, CUDA/NVML, psutil, numpy, pandas, scipy,
  plotting/video libraries, dataset SDKs, real network clients, or
  `tests.support` from base training modules.
- Any need to implement a concrete checkpoint artifact store, default writer,
  file format, payload serializer, cloud/object-store behavior, or file lock.
- Any requirement to add data-path Stage 9 producer hooks, datasource runtime
  imports, `BatchOperation` changes, or real data-path benchmark producers.
- Any requirement for real GPU/system/hardware probes or machine-specific speed
  thresholds to satisfy required tests.
- Any change that would make callback return values control native loop
  semantics or make observer errors silently non-fatal.
- Any public native-specific profile/checkpoint/probe/restart result family
  that duplicates shared Stage 15 records.
- Any inability to attach profile/failure/teardown evidence on native paths
  after setup starts.
- Any shared schema change larger than a narrow additive helper required by a
  concrete native test. Stop for plan review if this happens.

## Validation Commands

Required focused checks before Phase 4 implementation is complete:

```bash
uv run pytest tests/unit/rphys/training/test_plan.py tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_probes.py
uv run pytest tests/contracts/test_stage15_training_profile_contract.py tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/contracts/test_stage12_observability_contract.py
uv run pytest tests/integration/test_stage15_native_observability_flow.py
make test-package
git diff --check
```

Required suite-level obligations before PR approval:

```bash
make test-unit
make test-contract
make test-integration
make test-summary
make validate-pr
uv lock --check
```

Optional or conditional checks:

```bash
make test-e2e
make test-acceptance
```

`make test-e2e` and `make test-acceptance` are not Phase 4 blockers unless the
implementation adds corresponding lightweight e2e or optional acceptance files.
Do not add real hardware, real Lightning, real storage, or real dataset
requirements to default validation.

## Handoff Notes For `rphys_phase_executor`

- Keep the implementation native-only. The fastest safe route is to treat
  `backend.py` as the orchestration owner and consume existing shared records
  rather than moving schema across modules.
- Prefer explicit typed `TrainingPlan` fields over magic dictionaries. A little
  public constructor verbosity is better than hidden engine configuration.
- Use fake clocks, fake monitors, fake writers, fake probes, and fake
  checkpoint hooks in tests. Do not add production fake hooks unless they are
  already part of shared dependency-free contracts.
- Preserve existing Native call order and Stage 12 contracts before adding new
  assertions. Profile-enabled behavior must not mask changes to learner or
  optimizer semantics.
- Record unsupported/unavailable/skipped evidence instead of inventing default
  behavior for missing hooks, writers, monitors, probes, or checkpoint refs.
- If implementation pressure suggests a larger checkpoint manager or profile
  writer abstraction, stop and record a blocker. Phase 4 should not become a
  storage/runtime phase.

## Refinement And Review Budget Status

- Fast-path decision: use a single finalized execution plan. A separate refine
  pass is not needed because this artifact explicitly covers public API,
  scientific contract, import-boundary, dependency, checkpoint serialization,
  provenance, compatibility, reviewability, suite obligations, and blocker
  criteria.
- Review focus for the implementation PR: native execution ordering,
  `TrainingPlan` public field scope, profile attachment completeness, failure
  teardown evidence, checkpoint hook/storage boundary, primitive public
  records, import boundaries, and tests that prove disabled observability keeps
  existing Native semantics.

## Completion Notes

- Planning artifact completed in commit
  `558ddbab9e8a5834bbc339fc88333b48b768cd38`.
- Implementation completed. Added explicit native `TrainingPlan` inputs for
  resource monitors, async profile writers, training probes, checkpoint
  catalogs/selectors/policies/hooks, run/timeline/rank/device attribution, and
  private Native orchestration that records setup/teardown, data wait, device
  transfer, forward/output validation, backward, optimizer, scheduler,
  checkpoint, writer, monitor, probe, failure, and profiling-summary evidence
  into `TrainingResult.training_profile`.
- Shared profile schema was extended additively with primitive
  `probe_results` and `checkpoint_results`; Native uses those shared records
  instead of creating native-only result families.
- Focused validation passed:
  `uv run pytest tests/unit/rphys/training/test_plan.py tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_probes.py tests/contracts/test_stage15_training_profile_contract.py tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/contracts/test_stage12_observability_contract.py tests/integration/test_stage15_native_observability_flow.py`
  passed with 60 tests.
- Suite validation passed on 2026-05-18: `make test-package` passed
  (72 tests), `make test-unit` passed (791 tests), `make test-contract`
  passed (187 tests), `make test-integration` passed (31 tests),
  `make test-summary` passed (package 72, unit 791, contract 187,
  integration 31; e2e/acceptance not present), `make validate-pr` passed,
  `uv lock --check` passed, and `git diff --check` passed.
- PR preparation, automated review, merge result, and cleanup are pending.
