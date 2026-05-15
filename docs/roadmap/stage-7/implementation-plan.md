# Roadmap Stage 7 Implementation Plan

Status: approved; ready for implementation workflow
Roadmap version: `v7`
Planning document: `docs/roadmap/stage-7/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 3 PR open after local validation
Blockers: none

## Summary

- Goal: refactor the operation foundation first, then implement Stage 7 runtime
  sample and provisional batch operation contracts in small dependency-ordered
  phases, preserving Stage 6 behavior and the approved no-code-planning
  boundaries.
- Source functionality-agreement gate: passed in `planning.md`; FQ-0 is locked
  from maintainer naming guidance and FQ-1 through FQ-8 are repo-resolved.
- Approved behavior: full-name `SampleOperation` and provisional
  `BatchOperation` families over existing `Sample`, `Batch`, `FieldLocator`,
  and Stage 6 `OperationResult` semantics; field-permission-aware mutation;
  deterministic checks; replayable augmentations; specialized pipelines; and
  dependency-light batch equivalence reporting.
- Source behavior confirmation: passed in `planning.md`.
- Key design constraints: DD-1 revised operation-foundation refactor with public
  `OperationStep`, `Operation` compatibility, sequence-only generic pipeline
  behavior, callable-first wrappers, and compatibility-preserving Stage 6
  foundation cleanup for a cohesive execution interface; DD-2 specialized
  field-permission contracts; DD-3 snapshot mutation enforcement; DD-4 typed
  context/RNG/replay records; DD-5 split augmentation sampling/application;
  DD-6 specialized-only
  ordered mapping pipelines; DD-7 informational check/route records; DD-8
  provisional batch equivalence; DD-9 code-backed exports/errors only; DD-10
  private helpers only behind public behavior tests.
- Source design-agreement gate: revision applied in `planning.md`; no
  functionality item remains blocked or marked `needs maintainer discussion`.
- Source functionality-agreement queue: FQ-0 through FQ-8 resolved.
- Source design-agreement queue: DQ-0 recorded, DQ-1 revised approved,
  DQ-2 through DQ-7 approved, DQ-8 reviewed recommendation, DQ-9
  auto-approved with private-helper guardrails.
- Source future-roadmap/reuse safety review: passed; Stage 8 export/save,
  Stage 9 loader/cache/batch planning, and later trainer/model/workflow
  responsibilities remain deferred with revisit triggers.
- Examples covered: sample contract inspection, declared mutation, same-locator
  replacement failure, payload-mutation limitation, lazy-field
  non-materialization, deterministic transforms/checks, replayable linked
  augmentations, self-supervised view locators, ordered mapping diagnostics,
  route records as non-policy metadata, synthetic batch equivalence, and batch
  import-boundary examples.
- Source phase shaping: revised; seven dependency-ordered phases are accepted
  by the planning artifact, with refreshed plan-quality confirmation passed.
  The second design pass clarifies that Phase 1 may refactor Stage 6 internals
  for cohesion, but semantic changes beyond accepting `OperationStep` sequence
  entries reopen DD-1.
- Source plan quality gate: refreshed standalone review passed for the revised
  seven-phase plan; prior six-phase confirmation remains supporting context
  for DD-2 through DD-10 only.
- Out of scope: code implementation in this pass; concrete CHROM/POS or
  model-specific algorithms; export/save/cache/materialization manifests;
  datasource scanning/filtering; DataLoader adapters; trainer/device movement;
  model tuple formatting; workflow/artifact runtime behavior; DAG/retry/resume
  pipelines; broad `BatchProgram`; nested view `Sample`s; multi-member
  `IndexItem`s; top-level `rphys.transforms`; root `rphys` exports; placeholder
  future APIs; heavy optional imports.

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: completed by managing agent for the revised seven-phase shape;
  refreshed plan-quality approval passed
- Refinement pass: not needed before approval
- Confirmation review: maintainer approval recorded
- Automatic merge mode: enabled for later implementation workflow only
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`,
  `merged`, `blocked`
- Branch rule: every later implementation phase targets `develop`.
- Worktree rule: larger later implementation work should use one isolated
  worktree per phase under `/home/samcantrill/work/rphys-worktrees`.
- Boundary rule: implementation phases must not add export/cache/loader,
  DataLoader, trainer, model-formatting, workflow runtime, or heavy backend
  behavior. They must preserve lightweight imports and code-backed public names
  only.

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `operation-foundation` | merged | `agent/stage-7-p1-operation-foundation` | [#48](https://github.com/samcantrill/rphys/pull/48) | `src/rphys/ops/core.py`, `src/rphys/ops/pipelines.py`, `src/rphys/ops/__init__.py`, focused errors/tests/docs | Refactor the operation foundation around `OperationStep`. | `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | OperationStep, custom step pipeline, generic mapping rejection |
| 2 | `sample-foundations` | merged | `agent/stage-7-p2-sample-foundations` | [#49](https://github.com/samcantrill/rphys/pull/49) | `src/rphys/ops/sample.py`, `src/rphys/ops/__init__.py`, focused errors/tests | Establish sample operation public foundations. | `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | contract inspection, locator parsing, context/replay records, exports |
| 3 | `sample-effects-checks` | pr_open | `agent/stage-7-p3-sample-effects-checks` | [#50](https://github.com/samcantrill/rphys/pull/50) | sample enforcement, transforms/checks, focused private helpers | Implement sample field-effect enforcement, transforms, and checks. | `make test-unit`; `make test-contract`; `make test-integration`; `make test-package`; `make validate-pr`; `make test-summary`; `git diff --check` | declared mutation, same-locator replacement, lazy fields, route non-policy |
| 4 | `sample-augmentation-views` | pending | `agent/stage-7-p4-sample-augmentation-views` | pending | sample augmentation params/replay/view behavior | Add sample augmentation replay and self-supervised view writing. | `make test-unit`; `make test-contract`; `make test-integration`; `git diff --check` | replay, linked fields, no global RNG, view locators |
| 5 | `sample-pipeline` | pending | `agent/stage-7-p5-sample-pipeline` | pending | `src/rphys/ops/pipelines.py`, specialized pipeline tests | Add specialized sample pipeline composition. | `make test-unit`; `make test-contract`; `git diff --check` | ordered mapping, step diagnostics, generic pipeline regression |
| 6 | `batch-surface` | pending | `agent/stage-7-p6-batch-surface` | pending | `src/rphys/ops/batch.py`, batch pipeline/equivalence tests | Add provisional batch operation, augmentation, equivalence, and pipeline surface. | `make test-unit`; `make test-contract`; `make test-integration`; `make test-package`; `git diff --check` | LIST-collated equivalence, batch params, dtype/device metadata |
| 7 | `docs-validation` | pending | `agent/stage-7-p7-docs-validation` | pending | public docstrings/docs/examples/final validation evidence | Finalize docs, examples, and PR validation evidence. | `make test`; `make test-summary`; `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `uv lock --check`; `git diff --check`; `make validate-pr` if PR breadth warrants | public examples and residual-risk readback |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. | `planning.md` Stage Gates, Stage Readbacks, Plan Quality Gate; this implementation plan | Refreshed plan quality passed, seven-phase alignment is complete, and maintainer approval is recorded. | resolved |

## Phase 1: Operation Foundation Refactor

Status: merged
Slug: `operation-foundation`
Branch: `agent/stage-7-p1-operation-foundation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p1-operation-foundation`
PR: [#48](https://github.com/samcantrill/rphys/pull/48)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path because this intentionally refactors shared
operation foundation code

### Scope

- Goal: refactor the Stage 6 operation foundation so generic and specialized
  pipelines compose a stable operation-step execution interface instead of
  concrete `Operation` instances only, while preserving Stage 6 user-visible
  semantics except for the accepted broader sequence step type.
- Files/modules owned: likely `src/rphys/ops/core.py`,
  `src/rphys/ops/pipelines.py`, `src/rphys/ops/__init__.py`, exercised error
  additions in `src/rphys/errors.py`, public docs/docstrings for operation
  extension, and focused unit/contract/package tests.
- Behavior implemented: public `OperationStep`; `Operation` implements
  `OperationStep`; generic `OperationPipeline` accepts an ordered sequence of
  `OperationStep` objects; generic pipeline still rejects mappings, tuple
  named entries, text, raw callables, and empty sequences; adjacent type
  compatibility continues through `OperationContract`; execution forwards
  `OperationResult.output` and wraps failures with step diagnostics. Internal
  Stage 6 operation/pipeline code may be reorganized so `Operation`, direct
  advanced operation steps, and later sample/batch adapters share one cohesive
  execution path.
- Decisions applied: DD-1, DD-9, DD-10.
- Future-roadmap/reuse constraints: this is an execution interface only, not a
  registry, symbolic-name system, graph/DAG language, retry/resume engine,
  export/cache identity, loader policy, trainer policy, or workflow runtime.
- Examples or demos covered: `Operation` as an `OperationStep`, a minimal
  custom operation-step object in `OperationPipeline`, raw callable rejection,
  mapping rejection, tuple named-entry rejection, and existing Stage 6
  operation behavior.
- Out of scope: sample/batch contracts, locator permissions, mutation
  enforcement, augmentations, specialized mapping support, export/cache/loader
  behavior, and heavy optional imports.
- Dependencies: code-backed Stage 6 operation modules and tests.

### Tasks

- Add the public operation-step interface in the smallest coherent operation
  module location and export it from `rphys.ops`.
- Update `Operation` to explicitly satisfy the operation-step interface without
  changing wrapper-first callable behavior.
- Refactor shared Stage 6 operation/pipeline internals where that reduces
  duplicated execution logic, while keeping existing public result/context,
  contract, mapping-rejection, raw-callable rejection, and error semantics.
- Update generic `OperationPipeline` step validation from concrete
  `Operation` checks to operation-step validation while preserving all Stage 6
  construction and execution semantics except the broader accepted step type.
- Preserve or improve typed pipeline errors for invalid steps, mappings, tuple
  named entries, raw callables, context validation, compatibility failures, and
  execution failures.
- Add focused unit, contract, and package tests plus public docstrings that
  make callable-first wrappers the ordinary user extension path and direct
  `OperationStep` implementation the advanced adapter path.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Unit coverage for `Operation`, `OperationStep`, and generic pipeline behavior. | yes |
| `make test-contract` | Public operation-step and pipeline composition contracts. | yes |
| `make test-package` | Public exports and lightweight import boundaries. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: `Operation` satisfies `OperationStep`; a minimal custom
  operation-step object composes in `OperationPipeline`; raw callables are not
  accepted as pipeline steps.
- Cohesion evidence: `Operation`, minimal custom operation-step objects, and
  the later specialized operation families can target the same execution
  interface without duplicating result forwarding or adjacent compatibility
  checks.
- Design-decision evidence: DD-1 operation-foundation refactor preserves
  `OperationResult`, `.run()`, `__call__`, `name`, `contract`, compatibility
  checks, and typed failure behavior.
- Future-roadmap/reuse evidence: no registry, symbolic-name system, graph,
  workflow, cache/export identity, loader policy, trainer policy, or heavy
  backend dependency appears.
- Example/demo evidence: tiny synthetic operation-step tests demonstrate the
  advanced adapter path while wrapper examples remain the primary docs path.
- Documentation evidence: docstrings explain `OperationStep` as the composition
  interface and `Operation`/specialized wrappers as the ordinary implementation
  surface.
- Scientific contract evidence: the foundation refactor does not weaken later
  field-permission, replay, or provenance guarantees.

### Phase Workflow State

- Phase execution plan: completed in
  `docs/roadmap/stage-7/phases/operation-foundation.md`
- Planning/refinement budget: one scoped planning pass because shared core
  operation behavior is being refactored
- Implementation/refinement budget: one implementation pass plus targeted
  compatibility fixes
- PR review budget: one foundation/API compatibility review
- Blocker-resolution budget: reopen planning only if `OperationStep` requires
  changing `OperationResult`, generic `OperationContext`, generic
  `OperationContract`, mapping rejection, raw callable rejection, or public
  workflow semantics
- Pre-submit blocker gate: Stage 6 operation test regressions, package/import
  regressions, raw-callable pipeline acceptance, registry/workflow behavior, or
  heavy imports block completion
- Merge record: completed

### Risks And Stop Conditions

- Risks: broad core edits may accidentally change Stage 6 behavior; a too-broad
  interface could become an accidental workflow abstraction; structural checks
  may produce weaker errors than concrete `Operation` checks if not tested.
- Stop conditions: implementation requires accepting raw callables in
  pipelines, changing generic result/context/contract semantics, changing
  mapping rejection, adding operation registries, adding graph/retry/workflow
  policy, or using operation-step fields as durable export/cache identity.
- Assumptions: existing Stage 6 behavior remains the compatibility baseline.

### Completion Summary

- Implementation: added public `OperationStep`, made `Operation` explicitly
  satisfy the interface, and updated generic `OperationPipeline` to accept
  ordered `OperationStep` entries while preserving Stage 6 result forwarding,
  compatibility checks, raw-callable/mapping/tuple-entry rejection, and typed
  execution diagnostics.
- Validation: `make test-unit`, `make test-contract`, `make test-package`,
  `git diff --check`, and `make validate-pr` passed. `make validate-pr`
  generated `build/test-summary.md` with 529 passing package/unit/contract/
  integration tests, ran `uv lock --check`, built sdist/wheel artifacts, and
  reran `git diff --check`.
- PR: [#48](https://github.com/samcantrill/rphys/pull/48) opened against
  `develop` from `agent/stage-7-p1-operation-foundation`; target and title
  verified by `gh pr view`
- Merge: squash-merged to `develop` on 2026-05-15 at
  `4c693336ad12eb8db381795963ef7bcb58a0a4a7`; merge command
  `gh pr merge 48 --squash --delete-branch`; local branch cleanup deferred
  until worktree removal because the branch was checked out in the phase
  worktree.
- Follow-up: later phases must keep `OperationStep` as an execution interface,
  not a registry, workflow abstraction, export/cache identity, loader policy,
  or trainer policy.

## Phase 2: Sample Operation Public Foundations

Status: merged
Slug: `sample-foundations`
Branch: `agent/stage-7-p2-sample-foundations`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p2-sample-foundations`
PR: [#49](https://github.com/samcantrill/rphys/pull/49)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path unless implementation discovers an operation-step
adapter conflict

### Scope

- Goal: establish the code-backed public sample operation foundation without
  mutation enforcement beyond base declaration/read validation.
- Files/modules owned: likely `src/rphys/ops/sample.py`,
  `src/rphys/ops/__init__.py`, exercised error additions in
  `src/rphys/errors.py`, package/unit/contract tests for the new public names.
- Behavior implemented: `SampleOperation`, `SampleOperationContract`,
  `SampleFieldPermissions`, `SampleOperationContext`, and runtime replay/context
  records needed by the base; parsed locator declarations; immutable,
  inspectable contracts; callable-first `OperationStep` adapter behavior;
  adaptation to generic `OperationContract` and `OperationResult`.
- Decisions applied: DD-0, DD-1, DD-2, DD-4, DD-9, DD-10.
- Future-roadmap/reuse constraints: replay/context records are runtime evidence
  only, not export/cache schemas; no registry, shorthand alias, top-level
  `rphys.transforms`, root `rphys` export, or heavy import.
- Examples or demos covered: contract inspection, malformed locator failure,
  missing required field preflight, code-backed `rphys.ops` imports.
- Out of scope: transforms/checks, snapshot mutation enforcement, augmentation
  params, specialized pipelines, batch classes, export/cache/loader/trainer
  behavior.
- Dependencies: Phase 1 operation foundation; `OperationStep`,
  `OperationContract`, `OperationContext`, `OperationResult`, `Sample`, and
  `FieldLocator`.

### Tasks

- Add the minimal sample operation module and public records required for the
  base contract.
- Adapt specialized contracts to generic operation-step type checks without
  expanding Stage 6 generic contracts.
- Add only concrete error classes that are exercised by tests.
- Re-export implemented public names from `rphys.ops`; do not add placeholder
  future names.
- Add focused package, unit, and contract tests for public imports, contract
  immutability, locator parsing, context adaptation, and result semantics.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Unit coverage for sample foundation records and base execution. | yes |
| `make test-contract` | Public contract and `OperationResult` semantics. | yes |
| `make test-package` | Public exports and lightweight import boundaries. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: public full names exist only when implemented; contracts
  parse locators, reject malformed declarations, and remain immutable.
- Design-decision evidence: DD-1 operation-step adaptation preserves
  `OperationResult`, specialized contract access, `.run()`, `__call__`,
  `name`, `contract`, and typed failures.
- Future-roadmap/reuse evidence: runtime replay/context records are documented
  as non-durable and no export/cache/loader/trainer hooks appear.
- Example/demo evidence: tiny synthetic sample tests show declaration
  inspection and required-field preflight.
- Documentation evidence: docstrings cover locator formats, context fields, and
  stability/boundary notes for public records.
- Scientific contract evidence: field declarations are visible before
  execution and do not require payload materialization.

### Phase Workflow State

- Phase execution plan: completed in
  `docs/roadmap/stage-7/phases/sample-foundations.md`
- Planning/refinement budget: one scoped planning pass if operation-step
  adaptation is ambiguous
- Implementation/refinement budget: one implementation pass plus targeted fixes
- PR review budget: one focused public-API review
- Blocker-resolution budget: reopen planning only if operation-step or context
  adaptation conflicts with approved DD-1/DD-4
- Pre-submit blocker gate: package/import regressions, placeholder exports, or
  heavy imports block completion
- Merge record: completed

### Risks And Stop Conditions

- Risks: direct operation-step implementations may bypass sample contracts if
  accepted too broadly; dynamic permission shape may become too broad; public
  record names may exceed the minimal approved surface.
- Stop conditions: implementation requires changing Stage 6 generic
  `OperationContract`, adding root exports, adding a registry/workflow layer, or
  using replay records as export/cache identity.
- Assumptions: Stage 6 code-backed operation APIs match the approved Stage 6
  plan.

### Completion Summary

- Implementation: added code-backed public `SampleOperation`,
  `SampleOperationContract`, `SampleFieldPermissions`,
  `SampleOperationContext`, and `SampleReplayRecord`; preserved generic
  `OperationResult` semantics and exposed an adapted generic
  `OperationContract` without expanding Stage 6 records. Required-read
  preflight uses non-payload `Sample.has()` access and no sample transforms,
  checks, augmentations, pipelines, or batch APIs were added. Review-blocker
  resolution rejects mismatched `SampleOperationContext.operation_name` values
  to keep replay/provenance evidence aligned with the executing operation.
- Validation: `make test-unit`, `make test-contract`, `make test-package`,
  `git diff --check`, `git diff --check develop...HEAD`, and
  `make validate-pr` passed after blocker resolution. The final
  `make validate-pr` generated `build/test-summary.md` with 556 passing
  package/unit/contract/integration tests, ran `uv lock --check`, built
  sdist/wheel artifacts, and reran `git diff --check`.
- PR: [#49](https://github.com/samcantrill/rphys/pull/49) opened against
  `develop` from `agent/stage-7-p2-sample-foundations`; target and title
  verified by `gh pr view`
- Merge: squash-merged to `develop` on 2026-05-15 at
  `f9b1850fe0e9793150574bd387d7081f53b28ed0`; merge command
  `gh pr merge 49 --squash`.
- Follow-up: Phase 3 owns write/delete/dynamic mutation enforcement, snapshot
  evidence, transforms/checks, and route/decision records on top of the Phase 2
  foundation.

## Phase 3: Sample Field Effects, Transforms, And Checks

Status: pr_open
Slug: `sample-effects-checks`
Branch: `agent/stage-7-p3-sample-effects-checks`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p3-sample-effects-checks`
PR: [#50](https://github.com/samcantrill/rphys/pull/50)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path if snapshot behavior touches shared helpers or
error wrapping broadly

### Scope

- Goal: implement deterministic sample operation behavior: declared-read
  preflight, field-effect snapshots, transforms, checks, and informational
  route/decision records.
- Files/modules owned: sample operation enforcement internals, private helper
  modules if needed, `SampleTransform`, `SampleCheck`, `SampleDecision`,
  `SampleRoute`, focused errors/tests.
- Behavior implemented: in-place default execution, explicit shallow/deep copy
  modes, before/after `field_items()` snapshots, add/delete/rename and
  same-locator `FieldValue` identity replacement detection, declared
  write/delete/dynamic permissions, deterministic check/report behavior.
- Decisions applied: DD-2, DD-3, DD-7, DD-9, DD-10.
- Future-roadmap/reuse constraints: field-effect metadata is inspectable for
  later export/cache planning but does not write export artifacts, cache keys,
  loader policy, or workflow branches.
- Examples or demos covered: declared write/delete success, undeclared
  mutation failure, same-locator replacement failure, lazy field
  non-materialization, route labels as informational metadata.
- Out of scope: stochastic augmentation, pipeline mapping support, batch
  operations, transparent read tracking, payload-internal mutation detection,
  loader/drop/retry/split/workflow policy.
- Dependencies: Phase 2.

### Tasks

- Add snapshot inventory helpers privately, validating only through public
  sample operation behavior.
- Implement declared read preflight without payload-demanding APIs.
- Implement mutation enforcement for additions, deletions, renames, dynamic
  fields, and same-locator `FieldValue` replacements.
- Add `SampleTransform` and deterministic `SampleCheck` behavior, including
  optional informational decision/route metadata.
- Document the payload-internal mutation and transparent read-tracking limits.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Snapshot, transform, check, and error behavior. | yes |
| `make test-contract` | Public failure and contract semantics. | yes |
| `make test-integration` | Lazy-field non-materialization fixtures. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: declared writes/deletes/replacements pass; undeclared
  additions, deletions, renames, and same-locator replacements fail loudly.
- Design-decision evidence: DD-3 snapshot enforcement includes `FieldValue`
  identity replacement and explicit copy behavior.
- Future-roadmap/reuse evidence: route labels are metadata for callers, not
  loader/drop/split/trainer policy.
- Example/demo evidence: adversarial tests cover mutation boundaries and
  deterministic check/report behavior.
- Documentation evidence: docstrings describe mutation/copy semantics, lazy
  boundaries, and explicit limitations.
- Scientific contract evidence: field effects are recoverable from declarations
  and runtime evidence without hiding payload access or mutation assumptions.

### Phase Workflow State

- Phase execution plan: completed on the expanded path in
  `docs/roadmap/stage-7/phases/sample-effects-checks.md`
- Planning/refinement budget: completed with one expanded-path refinement pass
- Implementation/refinement budget: completed with one implementation pass and
  one focused expanded-path metadata/report-field refinement
- PR review budget: one deterministic behavior/scientific-boundary review
- Blocker-resolution budget: 1/3 used for `SampleCheck` reserved metadata and
  report-field coverage hardening
- Pre-submit blocker gate: completed; no lazy-field materialization,
  route/drop policy, or public private-helper leakage blocker found
- Merge record: pending

### Risks And Stop Conditions

- Risks: snapshot logic cannot detect payload-internal mutation by design;
  route labels may be mistaken for policy; private helpers could drift into a
  public API.
- Stop conditions: implementation requires changing `Sample`/`FieldLocator`
  semantics, using payload-demanding APIs for preflight, or encoding loader or
  workflow decisions.
- Assumptions: current `Sample.field_items()` and `FieldValue` identity are
  sufficient for approved snapshot enforcement.

### Completion Summary

- Implementation: completed with deterministic sample copy modes, field-effect
  snapshots, declared mutation enforcement, `SampleTransform`, `SampleCheck`,
  `SampleDecision`, `SampleRoute`, and
  `UndeclaredSampleFieldMutationError`.
- Validation: `make test-unit`, `make test-contract`, `make
  test-integration`, `make test-package`, `make validate-pr`, `make
  test-summary`, and `git diff --check` passed. `make test-summary` reported
  592 passing package/unit/contract/integration tests; e2e and acceptance
  suites are not present.
- PR: [#50](https://github.com/samcantrill/rphys/pull/50) opened against
  `develop` from `agent/stage-7-p3-sample-effects-checks`; target and title
  verified by `gh pr view`.
- Merge: pending
- Follow-up: Phase 4 owns augmentation params, replay, stochastic sampling, and
  generated view writes; Phase 5 owns specialized sample pipeline composition.

## Phase 4: Sample Augmentation Replay And Views

Status: pending
Slug: `sample-augmentation-views`
Branch: `agent/stage-7-p4-sample-augmentation-views`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p4-sample-augmentation-views`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path unless parameter records require new public fields

### Scope

- Goal: add reproducible sample augmentation behavior and the initial
  self-supervised view-writing path.
- Files/modules owned: sample augmentation classes/params/replay records,
  sample tests for stochastic/replay behavior, integration tests for linked
  view fields.
- Behavior implemented: `SampleAugmentation`, immutable lightweight params,
  `sample_params(sample, context)`, deterministic
  `apply_params(sample, params, context)`, replay metadata, synchronized linked
  fields, declared self-supervised view locator writes such as
  `inputs/video.rgb.view_a` and `inputs/video.rgb.view_b`.
- Decisions applied: DD-4, DD-5, DD-2, DD-3.
- Future-roadmap/reuse constraints: no durable replay serialization, no
  cache/export identity, no backend-native array params, no hidden global RNG;
  Stage 9 loader worker contexts remain future adapters.
- Examples or demos covered: replay from params/context, linked field
  synchronization, invalid params, no global/default RNG use, dynamic view
  permissions.
- Out of scope: concrete rPPG algorithms, backend-specific RNG integrations,
  nested view `Sample`s, multi-member `IndexItem`s, learner/model consumption.
- Dependencies: Phases 2 and 3.

### Tasks

- Implement the public augmentation class shape with separate sampling and
  deterministic application.
- Add immutable dependency-light params and replay records with context seed
  material evidence.
- Ensure `run()` samples exactly once, applies params deterministically, and
  records replay metadata.
- Add tests that fail if `apply_params()` performs RNG sampling or writes
  undeclared locators.
- Add synthetic self-supervised view locator examples using one wide-window
  `Sample`.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Params, replay records, invalid params, and run behavior. | yes |
| `make test-contract` | Public replay contract and field permissions. | yes |
| `make test-integration` | Linked fields, view locators, and lazy boundaries. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: fixed params/context produce deterministic output and
  replay metadata; invalid params fail loudly.
- Design-decision evidence: DD-5 split sampling/application is visible in
  public methods and tests.
- Future-roadmap/reuse evidence: replay records remain runtime evidence and no
  cache/export schema or loader adapter is introduced.
- Example/demo evidence: view locators are written through declared explicit or
  narrow dynamic permissions.
- Documentation evidence: docstrings explain seed material, params immutability,
  linked fields, and no global/default RNG.
- Scientific contract evidence: synchronized fields and stochastic parameters
  are inspectable and replayable.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one scoped pass if params need additive fields
- Implementation/refinement budget: one implementation pass plus replay
  regression fixes
- PR review budget: one reproducibility/scientific-contract review
- Blocker-resolution budget: reopen planning if augmentation params need
  backend arrays, durable serialization, or hidden RNG
- Pre-submit blocker gate: use of global/default NumPy/Torch/random RNG,
  backend-heavy imports, or nested sample views blocks completion
- Merge record: pending

### Risks And Stop Conditions

- Risks: params records may be too narrow for future modalities; hidden RNG use
  can break replay; dynamic view permissions can weaken provenance if too broad.
- Stop conditions: implementation needs NumPy/Torch RNG in base imports,
  durable replay serialization, nested view samples, or multi-member index
  items.
- Assumptions: a lightweight standard-library params/replay shape can express
  the synthetic view-writing examples.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: Specialized Sample Pipeline Composition

Status: pending
Slug: `sample-pipeline`
Branch: `agent/stage-7-p5-sample-pipeline`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p5-sample-pipeline`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path with explicit Stage 6 regression checks

### Scope

- Goal: implement `SampleOperationPipeline` ordering, context propagation, and
  step-aware diagnostics without changing generic `OperationPipeline`.
- Files/modules owned: `src/rphys/ops/pipelines.py`, private step helper if
  needed, specialized pipeline tests and generic pipeline regression tests.
- Behavior implemented: sequence and insertion-ordered mapping construction,
  private immutable step normalization, mapping keys as diagnostic names,
  context propagation, `OperationResult.output` forwarding, invalid step
  rejection, failures with step index and effective name.
- Decisions applied: DD-6, DD-1, DD-3, DD-4, DD-10.
- Future-roadmap/reuse constraints: no DAGs, retry/resume, tuple named entries,
  routing graphs, loader orchestration, or workflow runtime; Stage 9 can later
  call sample pipelines from loader adapters.
- Examples or demos covered: ordered sequence execution, ordered mapping
  execution, named step failure, generic `OperationPipeline` mapping rejection.
- Out of scope: batch pipeline except for shared helper smoke checks; generic
  mapping support; DataLoader/workflow behavior.
- Dependencies: Phases 1 through 4.

### Tasks

- Add specialized pipeline construction and step normalization for sequences
  and insertion-ordered mappings.
- Preserve Stage 6 generic `OperationPipeline` sequence-only constructor and
  existing tests.
- Forward each step's `OperationResult.output` to the next operation.
- Include step index and effective diagnostic name in failures, including
  missing fields and undeclared mutation failures.
- Keep step records private and undocumented as extension points.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Pipeline construction, execution, and generic regression tests. | yes |
| `make test-contract` | Public composition and diagnostic contracts. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: sequences and ordered mappings preserve execution order;
  mapping keys appear only as diagnostics.
- Design-decision evidence: DD-6 specialized-only mapping support is proven by
  generic `OperationPipeline` mapping rejection tests.
- Future-roadmap/reuse evidence: no loader, retry, resume, DAG, or workflow
  semantics are introduced.
- Example/demo evidence: failing step tests show both index and effective name.
- Documentation evidence: public docstrings explain accepted construction
  forms and step-name meaning.
- Scientific contract evidence: pipeline preflight/execution preserves lazy
  field boundaries and mutation enforcement.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one scoped pass if helper sharing affects generic
  pipeline behavior
- Implementation/refinement budget: one implementation pass plus focused
  regression fixes
- PR review budget: one pipeline/API review
- Blocker-resolution budget: reopen planning if generic pipeline behavior must
  change
- Pre-submit blocker gate: generic mapping support, workflow semantics, or
  public step helper leakage blocks completion
- Merge record: pending

### Risks And Stop Conditions

- Risks: helper reuse can accidentally alter Stage 6 generic pipeline
  behavior; users may confuse diagnostic names with operation identity.
- Stop conditions: implementation requires changing generic
  `OperationPipeline` mapping rejection or adding graph/retry/workflow
  semantics.
- Assumptions: Python insertion-ordered mappings are sufficient for the
  approved specialized pipeline API.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 6: Provisional Batch Operation Surface

Status: pending
Slug: `batch-surface`
Branch: `agent/stage-7-p6-batch-surface`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p6-batch-surface`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path because this adds a provisional public surface

### Scope

- Goal: add dependency-light provisional batch operation, augmentation,
  equivalence, and pipeline APIs referenced to sample-side correctness.
- Files/modules owned: likely `src/rphys/ops/batch.py`,
  `src/rphys/ops/pipelines.py` for `BatchOperationPipeline`,
  `src/rphys/ops/__init__.py`, focused errors/tests/import checks.
- Behavior implemented: `BatchOperation`, `BatchTransform`,
  `BatchAugmentation`, `BatchOperationContext`, `BatchOperationContract`,
  `BatchEquivalenceReport`, batch/per-sample parameter scope declarations,
  dtype/device descriptive metadata, and `BatchOperationPipeline` sequence and
  mapping diagnostics.
- Decisions applied: DD-1, DD-4, DD-5, DD-6, DD-8, DD-9.
- Future-roadmap/reuse constraints: batch execution is an optimization
  contract, not a DataLoader/model/device policy; Stage 9 batch planning,
  loader adapters, cache/materialization, and backend fused kernels remain
  deferred.
- Examples or demos covered: synthetic LIST-collated fields, identical and
  approximate sample/batch equivalence reports, per-sample versus batch-level
  params, import-boundary guardrails.
- Out of scope: Torch/DataLoader/model layout policy, device movement, broad
  batch planner/program, selector parsing in hot loops, concrete fused kernels,
  collation policy changes.
- Dependencies: Phases 1, 2, 4, and 5.

### Tasks

- Implement provisional batch operation/context/contract records with field
  permissions and randomness scope.
- Implement batch augmentation params with explicit batch-level versus
  per-sample sampling scope.
- Implement `BatchEquivalenceReport` for identical, approximate, diagnostic, or
  unsupported replacement claims.
- Add `BatchOperationPipeline` with the same specialized sequence/mapping
  diagnostic rules as the sample pipeline.
- Validate synthetic LIST-collated examples without importing heavy backend,
  DataLoader, model, export, or cache code.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Batch contracts, params, equivalence reports, and pipeline behavior. | yes |
| `make test-contract` | Public provisional batch semantics. | yes |
| `make test-integration` | Synthetic sample/batch equivalence over collated fields. | yes |
| `make test-package` | Batch public exports and import boundary guardrails. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: batch contracts are inspectable and dependency-light;
  batch param scope is explicit; equivalence reports reject unsupported claims.
- Design-decision evidence: DD-8 batch equivalence references sample-side
  behavior and keeps dtype/device declarations descriptive only.
- Future-roadmap/reuse evidence: no DataLoader, model layout, device movement,
  selector-hot-loop, cache, export, or broad batch planning behavior exists.
- Example/demo evidence: synthetic LIST-collated samples show batch replacement
  evidence and per-sample diagnostics/provenance recovery.
- Documentation evidence: public docstrings mark batch APIs provisional and
  explain equivalence, masking/alignment/provenance obligations, and backend
  deferrals.
- Scientific contract evidence: batch operations cannot claim replacement
  unless scientific meaning, addressing, masking/alignment, replay, and
  provenance are described.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one scoped pass if equivalence fields imply
  backend policy
- Implementation/refinement budget: one implementation pass plus import and
  equivalence fixes
- PR review budget: one provisional public-API and future-roadmap review
- Blocker-resolution budget: reopen planning if batch behavior requires heavy
  backend dependencies or loader/model policy
- Pre-submit blocker gate: torch/DataLoader/model imports, device movement,
  broad batch program, or collation policy changes block completion
- Merge record: pending

### Risks And Stop Conditions

- Risks: provisional batch APIs may lock too much before real fused kernels;
  dtype/device metadata may be mistaken for movement policy; equivalence fields
  may under-specify masking/alignment needs.
- Stop conditions: implementation needs backend arrays in public records,
  DataLoader/model adapters, device movement, or a general batch execution
  language.
- Assumptions: tiny dependency-light synthetic batch fixtures are sufficient to
  validate the provisional contract.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 7: Docs, Examples, And Final Validation Evidence

Status: pending
Slug: `docs-validation`
Branch: `agent/stage-7-p7-docs-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p7-docs-validation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path if broad validation exposes prior phase gaps

### Scope

- Goal: align public documentation, examples, and validation evidence with the
  implemented Stage 7 behavior and accepted deferrals.
- Files/modules owned: public docstrings, examples in tests/docs as needed,
  `docs/GLOSSARY.md` only if code-backed wording requires alignment, final PR
  evidence notes.
- Behavior implemented: no new behavior beyond earlier phases; this phase
  records and validates behavior already merged.
- Decisions applied: DD-0 through DD-10, with special attention to DD-9 public
  exports/errors and DD-10 private-helper boundaries.
- Future-roadmap/reuse constraints: docs must preserve Stage 8/9/10 deferrals
  and avoid implying export/cache/loader/trainer/workflow ownership.
- Examples or demos covered: public operation contracts, mutation/copy limits,
  lazy-field boundary, replay records, view writing, check/route non-policy,
  specialized pipeline names, provisional batch equivalence.
- Out of scope: new public API beyond implemented code, docs-only PR separation
  between roadmap phase PRs, workflow/template changes unless maintainer asks.
- Dependencies: Phases 1 through 6.

### Tasks

- Review public docstrings and examples for scientific details: locators,
  roles, shapes where relevant, copy/mutation order, lazy loading, replay,
  route/check metadata, batch provisional status, and dtype/device metadata.
- Update `docs/GLOSSARY.md` only if implementation changes public wording
  beyond the roadmap shorthand/full-name clarification.
- Ensure examples use public APIs only and never private helpers.
- Run broad validation and record residual risks/deferrals for PR handoff.
- Send fixes back to the owning implementation phase if broad validation
  reveals a behavioral gap.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test` | Broad test suite for merged Stage 7 behavior. | yes |
| `make test-summary` | Markdown summary evidence for PR handoff. | yes |
| `make test-package` | Public imports and lightweight boundaries. | yes |
| `make test-unit` | Unit regression coverage. | yes |
| `make test-contract` | Public contract coverage. | yes |
| `make test-integration` | Synthetic lazy/view/batch integration coverage. | yes |
| `uv lock --check` | Dependency lock unchanged or valid. | yes |
| `git diff --check` | Whitespace/patch hygiene. | yes |
| `make validate-pr` | PR-ready validation if the combined implementation breadth warrants it. | conditional |

### Acceptance Evidence

- Behavior evidence: docs and examples match code-backed behavior, not planned
  or placeholder APIs.
- Design-decision evidence: every public behavior traces to DD-0 through DD-10
  and no reopened decision is hidden.
- Future-roadmap/reuse evidence: export/cache/loader/trainer/model/workflow
  boundaries are explicit and no future-stage behavior appears in examples.
- Example/demo evidence: examples exercise public names and synthetic fixtures
  only.
- Documentation evidence: no docs depend on private helpers; provisional and
  deferred behavior is labeled clearly.
- Scientific contract evidence: operation provenance, mutation limits, lazy
  boundaries, replayability, and batch equivalence obligations are documented.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one docs/evidence pass
- Implementation/refinement budget: documentation and validation fixes only;
  behavioral fixes return to the owning phase
- PR review budget: one final integration/documentation review
- Blocker-resolution budget: reopen planning only if docs expose a missing
  product or scientific decision
- Pre-submit blocker gate: undocumented public behavior, private helper docs,
  broad validation failures, or implied future-stage ownership blocks completion
- Merge record: pending

### Risks And Stop Conditions

- Risks: broad validation may reveal earlier phase gaps; docs can accidentally
  imply export/cache or loader ownership; examples may expose private helpers.
- Stop conditions: final docs require a new public API, change a locked
  decision, or introduce workflow/template changes beyond Stage 7 behavior.
- Assumptions: behavior is already code-backed by Phases 1 through 6 before this
  phase begins.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: after all implementation phases, run `make test`,
  `make test-summary`, `make test-package`, `make test-unit`,
  `make test-contract`, `make test-integration`, `uv lock --check`, and
  `git diff --check`; run `make validate-pr` when preparing the combined PR or
  when public/shared breadth warrants it.
- Docs/template checks: public docs and docstrings must cite implemented names
  only, preserve full public naming, keep private helpers undocumented, and
  update `docs/GLOSSARY.md` only if public wording changes require it.
- Scientific/workflow contract checks: verify `OperationStep` compatibility,
  field-permission declarations, mutation snapshots, lazy-field boundaries,
  deterministic checks, replayable augmentation params, informational route
  labels, provisional batch equivalence, import cost, and explicit
  no-export/cache/loader/trainer/workflow boundaries.
- Example/demo checks: use tiny synthetic/license-safe fixtures; no raw
  datasets; no heavyweight optional backends; examples should be seeds for
  tests, not extra product scope.
- Manual review focus: public API minimality, DD traceability, Stage 6 behavior
  preservation, future-roadmap deferrals, typed failure quality, and whether any
  implementation pressure hits a revisit trigger.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Managing-agent implementation-plan review completed for revised plan. | note | The phases, ownership hints, validation expectations, boundaries, risks, and stop conditions now include operation-foundation Phase 1, the second Stage 6 foundation design pass, and compatibility guardrails from revised `planning.md`. | reviewed |
| Refreshed plan-quality gate passed. | note | Standalone reviewer confirmed `planning.md` and this implementation plan are coherent around the revised seven-phase plan, with no blockers and no reopened functionality/design queues. | passed |
| Implementation-plan approval recorded. | note | Maintainer approved this seven-phase implementation plan before code implementation begins. | approved |

Gate result:

- Status: approved for implementation workflow
- Review evidence: this artifact is revised from the operation-foundation
  update in `planning.md`; the prior independent plan-quality gate is
  superseded for final approval, and refreshed plan-quality confirmation has
  passed for the seven-phase plan.
- Accepted risks: operation-foundation refactoring touches shared Stage 6
  behavior to improve interface cohesion; accepted user-visible change is
  limited to broader `OperationStep` sequence entries. Snapshot enforcement
  does not transparently police reads or payload-internal mutation; replay
  records are runtime evidence, not durable cache/export schemas; route/check
  records are informational only; batch APIs are provisional and
  dependency-light.
- Revisit triggers: Stage 6 operation behavior differs from the approved
  prerequisite beyond the DD-1 item-type broadening; concrete algorithms are
  pulled into Stage 7; batch work needs heavy backend dependencies; pipeline
  routing becomes loader/workflow policy; generic `OperationPipeline` mapping
  rejection or raw callable rejection changes; `OperationStep` accumulates
  registry/workflow/persistence policy; replay/context records become durable
  export/cache identity.

## Final Approval

- Approval status: approved by maintainer on 2026-05-15
- Approved scope: the seven phases above.
- Accepted risks: approved as listed in the plan review and phase stop
  conditions.
- Deferred items: concrete algorithms; export/save/cache/materialization;
  datasource scanning/filtering; DataLoader adapters; trainer/device movement;
  model formatting; workflow/artifact runtime behavior; broad batch planning;
  root exports; shorthand aliases; placeholder future APIs; heavy optional
  imports.
