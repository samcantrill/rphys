# Phase 3 Execution Plan: Sample Field Effects, Transforms, And Checks

## Metadata

- Status: draft phase execution plan
- Roadmap stage: `v7`
- Feature focus: deterministic sample field-effect enforcement, transform
  wrappers, check wrappers, and non-policy decision/route metadata over
  `SampleOperation`
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And
  Pipelines
- Phase descriptor: Sample Field Effects, Transforms, And Checks
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 3: Sample Field Effects, Transforms, And Checks`
- Branch: `agent/stage-7-p3-sample-effects-checks`
- Worktree:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p3-sample-effects-checks`
- Phase execution plan path:
  `docs/roadmap/stage-7/phases/sample-effects-checks.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: `## Phase 3: Sample Field Effects, Transforms, And Checks`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI
  pass during the implementation workflow
- Workflow path: expanded path because this adds public transform/check
  behavior and scientific mutation-snapshot enforcement over sample fields
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed for the implementation pass
- Plan quality gate: refreshed gate passed and final maintainer approval
  recorded in `docs/roadmap/stage-7/planning.md` and
  `docs/roadmap/stage-7/implementation-plan.md`
- Draft pass: expanded-path plan created in the existing dedicated worktree
  after inspecting Stage 7 planning, the implementation plan, Phase 1 and
  Phase 2 completion notes, roadmap/glossary guidance, current operation and
  sample source, package tests, unit tests, contract tests, integration lazy
  fixtures, and test suite layout
- Refine pass: not needed; the implementation plan and source inspection give
  enough detail to lock Phase 3 execution without reopening design
- Setup limitations: GitHub auth, remote `develop`, branch, and push/PR
  infrastructure were manager-verified; this pass did not refetch, recreate the
  worktree, open a PR, or modify the control checkout
- Blockers: none

## Objective

Implement deterministic sample operation execution semantics on top of the
Phase 2 `SampleOperation` foundation: non-payload declared-read preflight,
explicit in-place/shallow/deep copy modes, before/after field inventory
snapshots, enforcement of declared field additions, deletions, renames, and
same-locator `FieldValue` replacements, plus code-backed `SampleTransform`,
`SampleCheck`, `SampleDecision`, and `SampleRoute` behavior.

## Full-Plan Context

Phase 1 merged the public `OperationStep` foundation and Phase 2 merged the
code-backed `SampleOperation`, `SampleOperationContract`,
`SampleFieldPermissions`, `SampleOperationContext`, and `SampleReplayRecord`
surface. Phase 2 already performs declared-read preflight with `Sample.has()`
and normalizes results to `OperationResult`, but it intentionally does not
enforce write/delete/dynamic permissions or expose transform/check classes.

This phase locks the core deterministic sample mutation boundary that later
Stage 7 phases will rely on. Phase 4 must add stochastic augmentation replay
and view-writing on top of these field-effect checks. Phase 5 must add
specialized sample pipelines on top of these operation semantics. Phase 6 must
use sample-side behavior as the correctness reference for provisional batch
operations. Those later phases remain out of scope here.

## Source Phase Summary

- Goal: implement deterministic sample operation behavior with declared-read
  preflight, field-effect snapshots, transforms, checks, and informational
  route/decision records.
- Required scope: `src/rphys/ops/sample.py`, `src/rphys/ops/__init__.py`,
  focused exercised errors in `src/rphys/errors.py`, package/unit/contract/
  integration tests, and public docstrings for mutation/copy/check boundaries.
- Required checkpoints: before/after `field_items()` snapshots detect added
  locators, removed locators, rename-as-remove-plus-add effects, and
  same-locator `FieldValue` identity replacements; declared writes/deletes/
  dynamic permissions pass; undeclared field-set mutation fails loudly; lazy
  fields are not materialized by preflight, snapshots, or copy setup; checks
  return `Sample` output and route labels stay informational metadata.
- Acceptance criteria: field effects are recoverable from declarations and
  runtime metadata; payload-internal mutation and transparent read tracking are
  explicitly documented as outside automatic enforcement; no stochastic
  augmentation, specialized pipeline mapping support, batch APIs, export/cache,
  loader/drop/retry/split, trainer, or workflow policy is added.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/ops/sample.py` currently exports `SampleFieldPermissions`,
  `SampleOperationContract`, `SampleOperationContext`, `SampleReplayRecord`,
  and `SampleOperation`. `SampleOperation.run()` coerces context, validates
  required context keys, validates `Sample` input, preflights declared reads
  with `Sample.has()`, invokes the callable, and normalizes results through
  Stage 6 `_coerce_and_validate_result()`.
- `SampleFieldPermissions` currently stores immutable parsed locator tuples for
  `reads`, `writes`, `deletes`, and `dynamic_writes`, rejects duplicates within
  each category, rejects write/delete overlap, and rejects dynamic/write
  duplication. Enforcement is not implemented yet.
- `SampleOperationContract` adapts to generic `OperationContract` with
  `input_type=Sample` and `output_type=Sample`; generic Stage 6
  `OperationContract`, `OperationContext`, `OperationResult`,
  `OperationStep`, and `OperationPipeline` must not be expanded for sample
  field semantics.
- `src/rphys/data/containers.py` exposes the required non-payload and mutation
  APIs: `has()`, `field()`, `field_items()`, `set_field()`, `delete_field()`,
  `rename_field()`, `shallow_copy()`, and `deep_copy()`. Payload-demanding APIs
  are `get()` and `require()`, and must not be used for preflight or snapshots.
- `src/rphys/data/sample_fields.py` defines lazy `SampleField` handles.
  Existing unit and contract tests prove `has()`, `field_items()`, and copy
  paths can preserve lazy handles without materializing payloads.
- `src/rphys/errors.py` currently has broad operation errors and Stage 6
  concrete operation/pipeline errors only. A single focused sample mutation
  error may be justified if tests exercise distinct undeclared field-effect
  semantics; broad public error taxonomies are not justified.
- Existing tests or harness behavior: `tests/unit/rphys/ops/test_sample.py` and
  `tests/contracts/test_sample_operations.py` cover Phase 2 sample operation
  records, context coercion, required-read preflight, lazy non-materialization,
  explicit `OperationResult` validation, generic pipeline compatibility, and
  callable error wrapping.
- Package tests lock `rphys.ops.__all__`, `rphys.ops.sample.__all__`, no root
  `rphys` re-exports, and lightweight imports. Adding
  `SampleTransform`, `SampleCheck`, `SampleDecision`, or `SampleRoute` requires
  package test updates.
- Import-boundary or dependency constraints: this phase may import
  `dataclasses`, `collections.abc`, Stage 6 operation primitives, `Sample`,
  `FieldLocator`, and `FieldValue`-compatible handles. It must not import
  NumPy, torch, OpenCV, PyAV, scipy, pandas, plotting stacks, datasource
  builders, loader/cache/export modules, model/trainer modules, or
  `tests.support` in package code.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is on
  `develop...origin/develop` with unrelated untracked `docs/roadmap/stage-8/`;
  it was inspected only for status and left untouched.
- Dedicated branch/worktree status:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p3-sample-effects-checks` is
  on `agent/stage-7-p3-sample-effects-checks` at `6403262` and was clean before
  this plan file was created.
- Current `develop` base: `6403262 docs: record stage 7 phase 2 merge`; local
  `develop`, `origin/develop`, and this worktree `HEAD` all resolve to that
  metadata commit.
- Earlier phase dependency status: Phase 1 and Phase 2 are merged to
  `develop`. Phase 1 merged in PR #48 at
  `4c693336ad12eb8db381795963ef7bcb58a0a4a7`; Phase 2 merged in PR #49 at
  `f9b1850fe0e9793150574bd387d7081f53b28ed0`, with latest metadata commit
  `6403262`.
- Push/PR infrastructure status: manager verified GitHub auth and remote
  `develop`; this planning pass did not push or open a PR.
- Stop condition if isolation cannot be maintained: stop before editing the
  control checkout, committing product code during the planning pass, rebasing
  onto an unverified base, broadening into later phases, or committing files
  beyond this phase execution plan.

## In-Scope Work

- Extend the sample operation execution path to prepare an execution sample
  using explicit copy semantics: default `in_place`, explicit `shallow`, and
  explicit `deep`. Copy selection should be inspectable from the sample
  operation contract or operation configuration, with no root export and no
  heavy dependency.
- Preserve declared-read preflight using non-payload `Sample.has()` before
  callable invocation and before any payload-demanding operation code can run.
- Add private inventory snapshot/diff helpers that read only `field_items()`
  and compare locators plus `FieldValue` object identity. Validate these
  helpers only through public `SampleOperation`, `SampleTransform`, and
  `SampleCheck` behavior.
- Enforce declared field effects for additions, deletions, renames, and
  same-locator `FieldValue` replacements. Treat rename as the observable
  combination of one removed locator and one added locator; both halves must be
  permitted by declarations.
- Allow explicit `writes` to cover added locators and same-locator
  `FieldValue` replacements. Allow explicit `deletes` to cover removed
  locators. Allow the existing `dynamic_writes` declaration only as an
  inspectable write allowance; do not add arbitrary public predicate callables.
- Add runtime field-effect evidence to `OperationResult.metadata` using
  dependency-light values such as locator strings grouped by added, removed,
  and replaced fields. This evidence is runtime metadata only, not a cache key,
  export manifest, or durable serialization schema.
- Add code-backed `SampleTransform` as a deterministic `SampleOperation`
  specialization for declared output-producing work. It should reuse the same
  copy, preflight, snapshot, result, and enforcement path and should not add
  concrete physiological algorithms.
- Add code-backed `SampleCheck` as a deterministic `SampleOperation`
  specialization whose output remains a `Sample`. It may raise typed errors,
  write declared diagnostic/report fields, and include optional informational
  decision/route records in `OperationResult.metadata`.
- Add small frozen public `SampleDecision` and `SampleRoute` records with
  non-empty labels and optional reason/metadata. Route labels are information
  for callers only; they are not loader drop/retry/split/workflow policy.
- Add focused exercised errors only where existing Stage 6 operation errors
  are too broad, likely one catchable undeclared sample field mutation error
  under `RemotePhysOperationError`.
- Update `rphys.ops` lazy exports and `rphys.ops.sample.__all__` only for
  names implemented in this phase. Preserve no root `rphys` exports and no
  placeholder future names.
- Add public docstrings and tests that state the payload-internal mutation
  limitation, transparent read-tracking limitation, lazy boundary, copy
  behavior, and non-policy route/check boundary.

## Out-of-Scope Work

- `SampleAugmentation`, augmentation params, `sample_params()`,
  `apply_params()`, linked-field synchronization, replay sampling,
  self-supervised view writes, generated view-family permissions, global RNG
  checks, backend-specific RNG integration, and durable replay serialization.
- `SampleOperationPipeline`, ordered mapping support, tuple named entries,
  step normalization records, pipeline context propagation, DAGs, routing
  graphs, retries, resume, workflow stages, DataLoader orchestration, or
  generic `OperationPipeline` constructor changes.
- `BatchOperation`, `BatchTransform`, `BatchAugmentation`,
  `BatchOperationContext`, `BatchOperationPipeline`, batch equivalence reports,
  dtype/device declarations, collation policy changes, and model tuple layouts.
- Transparent read tracking, container proxies, payload-internal mutation
  detection, payload hashing, deep comparison of payload values, or replacing
  `Sample`, `FieldLocator`, `FieldValue`, or `SampleField` semantics.
- Datasource scanning/filtering/splitting, loader drop/retry policy, trainer
  policy, backend device movement, export/save/cache/materialization files,
  operation fingerprints as durable identity, public registries, root
  `rphys` exports, shorthand `SampleOp` aliases, concrete CHROM/POS/rPPG
  algorithms, and heavy optional imports.

## Assumptions

- Phase 2 public records are the implementation baseline and should remain
  backward compatible unless a narrow additive field is required for copy mode.
- `Sample.field_items()` returns stable `FieldLocator` keys and stored
  `FieldValue` objects without materializing lazy `SampleField` payloads.
- `FieldValue` object identity is the approved replacement boundary. In-place
  mutation of a payload inside an unchanged `FieldValue` object is outside
  automatic enforcement and must be documented and tested as a limitation.
- The current exact `dynamic_writes` locator tuple is sufficient for this
  deterministic phase. If implementation needs prefix/family permissions for
  generated view fields, stop and leave that design to Phase 4.
- Field-effect metadata can be added to `OperationResult.metadata` without
  changing the generic `OperationResult` schema.
- No dependency metadata change is expected. Any dependency addition is a
  stop-and-review condition.

## Scope Contract

The executor must keep the public operation shape as `Sample -> OperationResult`
with `OperationResult.output` holding the resulting `Sample`. `SampleOperation`,
`SampleTransform`, and `SampleCheck` all use the same execution skeleton:

1. Validate input is a `Sample` and coerce `SampleOperationContext`.
2. Preflight declared reads with non-payload access.
3. Select the execution sample by copy mode: `in_place` passes the original
   sample, `shallow` passes `sample.shallow_copy()`, and `deep` passes
   `sample.deep_copy()`.
4. Capture a before snapshot of the execution sample with `field_items()`.
5. Invoke the wrapped callable with the execution sample and sample context.
6. Normalize and validate the result as an `OperationResult` whose output is
   the same execution sample object. Arbitrary replacement of the whole sample
   is not part of this phase's copy contract.
7. Capture an after snapshot with `field_items()`.
8. Enforce the diff against `SampleFieldPermissions` and return an
   `OperationResult` augmented with field-effect metadata.

The snapshot diff contract is locator and `FieldValue` identity based:

- `added`: locators present after execution but absent before execution.
- `removed`: locators present before execution but absent after execution.
- `replaced`: locators present before and after execution whose stored
  `FieldValue` object identity changed.
- `unchanged`: locators present before and after execution with the same
  `FieldValue` object identity. Payload-internal mutation under this category
  is not detected.

Allowed effects:

- Added locators must be declared in `writes` or allowed by `dynamic_writes`.
- Removed locators must be declared in `deletes`.
- Replaced locators must be declared in `writes` or allowed by
  `dynamic_writes`.
- Renames are observed as one removal and one addition. A rename passes only
  when the removed locator is declared in `deletes` and the added locator is
  declared in `writes` or `dynamic_writes`.
- No declared permission is required for unchanged locators, even if the
  payload object was mutated in place.

Failure behavior must be fail-loud and typed. Missing declared reads continue
to raise `MissingFieldError` before callable invocation. Undeclared additions,
deletions, renames, and same-locator replacements should raise a focused
sample mutation error if added; otherwise they must raise an existing
operation-contract/execution error with operation name, locator, effect type,
declared permissions, and detected effects in context. Invalid check decision
or route metadata should raise `InvalidOperationResultError`.

`SampleTransform` must be a deterministic, callable-first sample operation
specialization. It should require declared output intent through explicit
`writes` or `dynamic_writes` unless implementation finds an existing Phase 2
compatibility concern; it must not add algorithm catalogs or numerical kernels.

`SampleCheck` must remain a deterministic `SampleOperation` whose output is a
`Sample`. It may write declared report/diagnostic fields and may attach
`SampleDecision` and `SampleRoute` records to result metadata. The recommended
reserved metadata keys are `sample_decision` and `sample_route`; if those keys
are present, the values must be the public records or tuples of those records.
The records are informational and must not encode datasource filters,
DataLoader drop/retry behavior, split assignment, trainer policy, or workflow
branching.

No public contract change is in scope for generic `OperationStep`,
`Operation`, `OperationPipeline`, `OperationResult`, `OperationContext`,
`OperationContract`, `OperationRole`, `OperationMutationPolicy`,
`FieldLocator`, `Sample`, `SampleField`, or `FieldValue`.

## Scientific Contract Notes

- Sampling and temporal alignment: this phase does not resample, window,
  filter, align, pad, or normalize payloads. Any transform kernel that touches
  scientific values must document its own shapes, units, sample rates, and
  alignment assumptions when concrete algorithms are added later.
- Field roles, locators, schemas, and provenance: permissions are parsed
  `FieldLocator` declarations. Field-effect evidence must report locator
  strings and effect classes so later export/cache/materialization planning can
  inspect what changed without treating this metadata as durable identity.
- Masking, filtering, normalization, and aggregation order: no concrete
  masking/filtering/normalization/aggregation operation is implemented in this
  phase. The only ordering contract is operation wrapper order around preflight,
  copy selection, snapshot, callable execution, diff enforcement, and metadata
  recording.
- Subject identity, splits, leakage, and grouping: this phase does not inspect
  subject IDs, split labels, group assignments, datasource records, or loader
  policies. Checks and routes may report loaded-sample decisions only after a
  `Sample` exists; datasource/index filters remain separate.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: missing declared fields fail during preflight. Payload
  validity such as NaNs, flat signals, temporal length, sample rate, dtype,
  device, masks, and unsupported slices belongs to concrete transform/check
  kernels and their declared report fields, not to the generic field-effect
  wrapper.

## Design Impact

- Maintainability: keep inventory snapshot and diff logic private and central
  so `SampleOperation`, `SampleTransform`, `SampleCheck`, and later
  augmentations use the same enforcement path.
- Extensibility: public extension remains callable-first through specialized
  wrappers; direct `OperationStep` remains the advanced adapter path from Phase
  1. Do not introduce registries or symbolic operation names.
- Lightweight import policy: `rphys.ops` should continue to avoid importing
  `rphys.data` until sample names are accessed through the existing lazy export
  mechanism. `rphys.ops.sample` must avoid heavy optional stacks and
  datasource/IO/trainer modules.
- Source-tree boundaries: sample operation policy stays in `rphys.ops.sample`.
  `Sample`, `Batch`, `FieldLocator`, `SampleField`, and codecs must not learn
  operation permission or route semantics.

## Future Compatibility

- Stage 8/9 export, materialization, and cache planning may inspect
  deterministic field-effect evidence, but Phase 3 must not create cache keys,
  manifests, export schemas, operation fingerprints, or file outputs.
- Phase 4 augmentation and view-writing should reuse the same field-effect
  enforcement path. Generated view-family permissions beyond exact
  `dynamic_writes` are a Phase 4 design pressure, not a hidden Phase 3
  addition.
- Phase 5 specialized pipelines should be able to rely on `SampleOperation`
  failures carrying operation names and effect details. Pipeline step
  diagnostics are still Phase 5 scope.
- Phase 6 provisional batch operations must reference these sample-side
  mutation semantics when claiming equivalence. No batch API should be added in
  this phase.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Container proxies for reads/writes | Too invasive for current mutable `Sample` semantics and likely to materialize or obscure lazy handles. |
| Payload hashing or deep payload comparison | Heavy, backend-specific, and outside the approved limitation that payload-internal mutation is not automatically detected. |
| Public dynamic write predicate callables | Not inspectable enough for provenance, export/cache planning, or stable tests. |
| Boolean-only `SampleCheck` return | Underspecified and conflicts with the approved `Sample` output plus metadata/declared-field behavior. |
| Route labels as loader or workflow policy | Explicitly rejected by DD-7; labels are information for callers only. |
| Public snapshot helper API | Premature API surface; helpers may be private and validated through public behavior tests. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Payload-internal mutation is invisible to enforcement | Approved DD-3 trade-off avoids intrusive proxies and backend-specific payload inspection. | A later operation family needs automatic payload mutation detection and can supply a lightweight, lazy-safe instrumentation design. |
| Exact `dynamic_writes` semantics may be too narrow for generated views | Phase 3 can enforce current declarations without designing Phase 4 view-family permissions early. | Phase 4 self-supervised view-writing requires prefix/family permissions that exact locators cannot express. |
| Field-effect metadata is runtime-only metadata, not a public durable schema | Keeps Stage 8/9 export/cache identity deferred. | Export/materialization stages need stable manifest fields and can promote or replace the metadata shape intentionally. |

## Reviewability

- Expected PR size and shape: one focused deterministic sample behavior PR
  touching `src/rphys/ops/sample.py`, `src/rphys/ops/__init__.py`,
  `src/rphys/errors.py` only if a focused error is added, package tests,
  sample unit tests, sample contract tests, lazy integration tests, and
  docstrings. No broad docs-only pass is expected beyond public API docstrings.
- Files and areas to inspect: copy-mode setup, snapshot helper diffing,
  undeclared mutation failures, result metadata augmentation, public exports,
  import-boundary tests, check/route record validation, and lazy-field
  non-materialization tests.
- Scope-control checks: verify no augmentation params, no sample pipeline
  class, no batch module, no datasource/loader/export/cache/trainer imports,
  no root exports, no public private-helper docs, no concrete physiological
  kernels, and no generic `OperationPipeline` constructor changes.

## Implementation Steps

1. Add the minimal copy-mode and snapshot enforcement foundation in
   `rphys.ops.sample`: private before/after inventory helpers, copy-mode
   coercion, field-effect diffing, typed undeclared-mutation failure, and
   metadata augmentation. Preserve existing Phase 2 read preflight and context
   behavior.
2. Wire enforcement into `SampleOperation.run()` so declared writes, deletes,
   dynamic writes, renames, and same-locator replacements are checked for bare
   `Sample` and explicit `OperationResult` returns. Add unit tests for allowed
   and disallowed add/delete/rename/replacement cases plus in-place, shallow,
   and deep copy behavior.
3. Add `SampleTransform` as a deterministic specialization over the same
   execution path. Update package exports and tests for public names and import
   boundaries.
4. Add `SampleDecision`, `SampleRoute`, and `SampleCheck` with validation for
   optional metadata records, declared diagnostic/report field writes, and
   explicit non-policy route wording. Add unit and contract tests for pass,
   fail, report-field, decision, route, and invalid metadata behavior.
5. Add lazy integration coverage proving preflight, snapshots, copy setup,
   transform wrappers, and check wrappers do not materialize `SampleField`
   payloads unless the user callable accesses payload-demanding APIs.
6. Refresh public docstrings and tests to document payload-internal mutation
   limits, transparent read-tracking limits, field-effect metadata status, and
   route/check deferrals away from loader/drop/split/workflow policy.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`;
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` and
  `rphys.ops.sample.__all__` include only implemented Phase 3 public names;
  root `rphys` still does not re-export operation names; errors are exported
  only if a concrete sample mutation error is added; `rphys.ops` remains
  lightweight and `rphys.ops.sample` does not import heavy optional,
  datasource, IO, model, trainer, or `tests.support` modules.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_sample.py`; possibly focused
  additions under the same source-mirrored file rather than a new file unless
  it improves readability
- Required assertions or deferral reason: copy-mode coercion and behavior;
  declared add/delete/replacement success; undeclared add/delete/rename/
  same-locator replacement failures; replacement detection by `FieldValue`
  identity; payload-internal mutation limitation; field-effect metadata shape;
  `SampleTransform` construction/output enforcement; `SampleCheck` decision,
  route, report-field, typed-failure, and invalid-metadata behavior.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_sample_operations.py`; possible new
  focused contract file only if the existing file becomes too broad
- Required assertions or deferral reason: public `SampleOperation`,
  `SampleTransform`, and `SampleCheck` semantics through public imports;
  declared-read preflight still halts before callable invocation when missing;
  declared mutation passes and undeclared mutation fails with catchable typed
  failures; route labels are metadata only; generic `OperationPipeline`
  compatibility remains sequence-only and result-forwarding still works for
  sample operations.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/` with tiny synthetic `SampleField`
  fixtures; reuse existing lazy fixture patterns where practical
- Required assertions or deferral reason: lazy `SampleField` handles remain
  unloaded after declared-read preflight, snapshot capture, field-effect
  enforcement, and shallow/deep copy setup when callables avoid payload access;
  payload access from inside the user callable materializes exactly through the
  existing lazy field path; no datasource scanning, loader policy, or export
  behavior is introduced.

### E2E Suite

- Status: deferred
- Expected paths: none for this phase
- Required assertions or deferral reason: no end-to-end public pipeline,
  datasource, export, loader, or batch workflow is implemented in Phase 3.
  Later pipeline/export/loading phases should own e2e coverage once composition
  and downstream boundaries exist.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real datasets, hardware, network,
  GPU, or long-running validation is required. Synthetic package/unit/contract/
  integration coverage is sufficient for this deterministic sample behavior
  phase.

## Risks

- Snapshot enforcement can miss in-place payload mutations inside an unchanged
  `FieldValue`; tests and docstrings must make this limitation visible.
- Copy-mode behavior may be confused with generic `OperationMutationPolicy`.
  Keep sample copy mode explicit and avoid changing Stage 6 mutation policy
  semantics.
- Adding route labels can look like loader/drop/split policy. Keep the record
  vocabulary small, informational, and clearly outside workflow control.
- Field-effect metadata could be mistaken for durable export/cache identity.
  Keep it runtime-only and avoid stable manifest language.
- Public export additions can accidentally force eager `rphys.data` imports
  from `rphys.ops`; preserve the existing lazy export pattern.

## Validation Commands

Targeted development commands:

```sh
make test-unit
make test-contract
make test-integration
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-integration
make test-package
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: first enforcement/copy helpers behind existing
  `SampleOperation`, then public transform/check/decision/route names, then
  lazy integration and import-boundary hardening.
- Tests to run with each slice: run `make test-unit` after enforcement helper
  work, `make test-contract` after public behavior is wired, `make
  test-package` after export changes, and `make test-integration` after lazy
  fixture coverage.
- Decisions the executor must not revisit: snapshot enforcement is locator plus
  `FieldValue` identity based; payload-internal mutation and transparent read
  tracking are out of scope; route labels are not policy; generic
  `OperationResult` and `OperationPipeline` schemas are not expanded; helpers
  remain private.
- Conditions that require stopping for the manager: enforcement needs
  container proxies or payload instrumentation; exact `dynamic_writes` cannot
  express a required Phase 3 case; implementation needs a broad public dynamic
  permission vocabulary; copy mode requires changing `Sample` semantics;
  result metadata needs a durable export/cache schema; or any dependency,
  loader, trainer, export, cache, batch, augmentation, or pipeline behavior is
  needed to complete tests.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this file in the existing dedicated worktree.
- Final phase execution plan: pending implementation workflow review.
- Implementation summary: pending.
- Implementation validation: pending.
- Refinement summary: pending.
- Pre-submit blocker gate: pending.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none known.
