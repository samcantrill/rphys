# Roadmap Stage 4 Implementation Plan

Status: implementation in progress
Roadmap version: `v4`
Planning document: `docs/roadmap/stage-4/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Preparation Phase 2 pending
Blockers: none identified by implementation-readiness review

## Summary

- Goal: implement Milestone 4, "Codecs And Lazy Sample Construction", as the dependency-light bridge from Stage 3 `IndexItem`/`FieldView` descriptors to Stage 2 runtime `Sample`s with lazy `SampleField` handles, after two preparation phases tighten the Stage 2/3 interfaces the bridge depends on.
- Source functionality-agreement gate: passed 2026-05-14 / manager functionality agreement; FQ-1 through FQ-8 are repo-resolved and accepted.
- Approved behavior: pre-Stage-4 cleanup adds a public field-container protocol, freezes `FieldSpec`, and clarifies `FieldIndex` as a base interface; codecs then probe/load/save logical `FieldView`s; explicit registry instances resolve codecs deterministically; dependency-light synthetic codec behavior proves probe/load/save; `SampleField` exposes unloaded/loaded/failed state; `SampleBuilder` builds all/subset/one lazy fields from one `IndexItem`; provenance, metadata, ordered resources, and typed failures remain inspectable.
- Source behavior confirmation: passed 2026-05-14 / behavior confirmation.
- Key design constraints: `rphys.data.containers` owns the public `FieldContainer` protocol and public field iteration surface; `FieldSpec` becomes frozen while remaining explicitly unhashable; `FieldIndex` stays a narrow subclass-based base interface with no registry; `rphys.io.codecs` owns datasource-neutral codec contracts, explicit registries, capabilities, contexts, results, and narrow save metadata policy; `rphys.data.sample_fields` and `rphys.data.sample_builders` own lazy runtime construction and builder-side datasource provenance; `FieldCodec` is structural/duck-typed; `SaveContext.target` is a `FieldRef`; `SampleField` is `FieldValue`-compatible and stored in `Sample` as the field object, not wrapped as payload; no global discovery, process-global mutable registry, public fake codec, descriptor mutation, hidden full-load fallback, cache policy, datasource-aware codec context, datasource scanning, export orchestration, model formatting, member binding, alignment semantics, item IDs, or fingerprints.
- Source design-agreement gate: passed 2026-05-14 / manager design agreement.
- Source functionality-agreement queue: FQ-1 through FQ-8 closed with no unresolved `needs maintainer discussion`, `blocked`, `pending approval`, or `ready for approval` items.
- Source design-agreement queue: DQ-1 through DQ-8 approved as recorded recommendations; DQ-9 through DQ-10 auto-approved with traceability and adversarial review evidence; no unresolved packet remains.
- Examples covered: EX-1 lazy sample build/load; EX-2 probe without load; EX-3 single-field save through `SaveContext.target`; EX-4 resolution failure matrix; EX-5 compound ordered resources; EX-6 public surface and import boundaries.
- Source phase shaping: validation planner accepted five primary Stage 4 phases: codec public contract, registry/synthetic codec operations, lazy runtime field compatibility, `SampleBuilder` bridge/provenance, closeout docs/examples/validation. Post-review maintainer refinement prepends two preparation phases for runtime container and descriptor-contract cleanup before the primary phases execute.
- Source plan quality gate: passed 2026-05-14 / plan quality reviewer; no missing or stale specialist evidence, unresolved queue packet, blocked design decision, reopened queue, or implementation-agent invention risk was found.
- Out of scope: real codec catalog, optional heavy integrations, datasource discovery/views/splits/index manifests, operations/pipelines, export specs/save orchestration, derived datasources, training loaders, caches, model formatting, spatial or seconds slicing, multi-member/nested samples, workflow/artifact runtime, and raw dataset handling.

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: completed 2026-05-14 / manager implementation-plan review
- Refinement pass: completed 2026-05-14 / FR traceability added; updated after maintainer request to prepend two interface-cleanup phases and refine affected primary phases
- Post-revision specialist review: completed 2026-05-14 / plan specialist review; no blocker found after adding preparation phases
- Confirmation review: maintainer approved implementation 2026-05-14 / user request
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prep 1 | `field-container-protocol` | merged | `agent/codecs-lazy-samples-prep1-field-container-protocol` | [#21](https://github.com/samcantrill/rphys/pull/21) | `src/rphys/data/containers.py`, `src/rphys/data/contracts.py`, `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`, runtime unit/contract/package tests | Add the public field-container protocol and public field-iteration surface before lazy fields widen runtime semantics. | `make validate-pr`; targeted runtime/unit/package/contract checks; `git diff --check` | Runtime compatibility and no private collation hook |
| Prep 2 | `field-spec-index-contracts` | pending | `agent/codecs-lazy-samples-prep2-field-spec-index-contracts` | pending | `src/rphys/data/fields.py`, datasource schema tests, IO index docs/tests, package/contract tests | Freeze `FieldSpec` and clarify `FieldIndex` as a subclass-based base interface. | targeted `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | Immutable datasource declarations and explicit index extension boundary |
| 1 | `codec-contract-foundation` | pending | `agent/codecs-lazy-samples-p1-codec-contract-foundation` | pending | `src/rphys/io/codecs.py`, conditional `src/rphys/io/__init__.py`, exercised `src/rphys/errors.py`, package/unit import tests | Establish the Stage 4 IO public contract without runtime sample behavior. | `make test-package`; targeted `make test-unit`; `git diff --check` | EX-3, EX-6 |
| 2 | `codec-registry-synthetic-ops` | pending | `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops` | pending | `src/rphys/io/codecs.py`, tests/support synthetic codec, IO unit/contract tests | Prove explicit codec resolution and dependency-light probe/load/save behavior. | targeted `make test-unit`; `make test-contract`; `make test-package` if exports change | EX-2, EX-3, EX-4, EX-5 |
| 3 | `lazy-sample-field-runtime` | pending | `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime` | pending | `src/rphys/data/sample_fields.py`, additive `src/rphys/data/containers.py` updates, conditional `src/rphys/data/__init__.py`, data unit/contract tests | Add lazy `SampleField` handles while preserving loaded `Sample` semantics. | targeted `make test-unit`; `make test-contract` including runtime core coverage | EX-1 |
| 4 | `sample-builder-provenance` | pending | `agent/codecs-lazy-samples-p4-sample-builder-provenance` | pending | `src/rphys/data/sample_builders.py`, conditional `src/rphys/data/__init__.py`, builder/provenance unit/contract tests | Build lazy `Sample`s from one `IndexItem` with all/subset/one/probe/eager paths. | targeted `make test-unit`; `make test-contract`; optional `make test-integration` only for one adopted vertical slice | EX-1, EX-2, EX-5 |
| 5 | `closeout-docs-validation` | pending | `agent/codecs-lazy-samples-p5-closeout-docs-validation` | pending | public docstrings/docs/examples, package expectations, final validation evidence | Harden docs, examples, contracts, import checks, and final validation without adding new behavior. | `make test-package`; `make test-unit`; `make test-contract`; `git diff --check`; broaden as needed | EX-1 through EX-6 |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Functionality, behavior confirmation, design agreement, validation and phase shaping, and plan quality gates are passed. | `docs/roadmap/stage-4/planning.md` Stage Gates, Stage Readbacks, Phase Shaping, Plan Quality Gate | No resolution required before implementation-plan review. Return to planning only if implementation proposes untraced public behavior or violates locked guardrails. | clear |

## Preparation Phase 1: Field Container Protocol

Status: merged
Slug: `field-container-protocol`
Branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep1-field-container-protocol`
PR: [#21](https://github.com/samcantrill/rphys/pull/21)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the public runtime field-container protocol that Stage 4 lazy fields, `SampleContract`, collation, and later operations can share without relying on private hooks.
- Files/modules owned: `src/rphys/data/containers.py`; `src/rphys/data/contracts.py`; `src/rphys/data/collation.py`; `src/rphys/data/__init__.py`; focused runtime unit tests; runtime contract tests; package import/export tests.
- Behavior implemented: public `FieldContainer` protocol in `rphys.data.containers`; public `field_items()` on `Sample` and `Batch`; `SampleContract` validates through the public protocol shape; LIST collation uses `field_items()` instead of private `_field_items`; `rphys.data` re-exports `FieldContainer` only if package import-boundary tests remain lightweight.
- Requirements supported: FR-4 lazy-field runtime compatibility; FR-7 intentional public imports; FR-8 scope-control validation.
- Decisions applied: maintainer post-plan refinement for public field-container protocol; existing Stage 2 loaded-runtime behavior remains unchanged.
- Examples or demos covered: runtime compatibility example and explicit no-private-collation-hook guardrail.
- Out of scope: `SampleField`, `SampleBuilder`, codecs, payload loading, lazy state, retry/cache policy, plan/build/result objects, datasource behavior, collation policy expansion, or changes to loaded `Sample`/`Batch` accessor semantics.
- Dependencies: implemented Stage 2 runtime core and Stage 3 descriptors.

### Tasks

- Add `FieldContainer` as a runtime-checkable public protocol in `rphys.data.containers` covering `has`, `field`, `get`, `require`, `role`, and `field_items`.
- Add public `field_items()` to the private container base so `Sample` and `Batch` expose stable field iteration without exposing `_FieldEntry`.
- Keep `_field_items()` only as a temporary private compatibility alias if needed by existing tests, and update internal code to call public `field_items()`.
- Update `SampleContract` container-shape validation to use the public protocol methods rather than an ad hoc `has`/`require` check only.
- Update LIST collation to consume `field_items()` and retain the current field-set/schema/policy/metadata behavior.
- Update `rphys.data.__all__` and package tests to include `FieldContainer` only after verifying import cost stays lightweight.
- Add tests that `Sample` and `Batch` satisfy the protocol, collation avoids private hooks, existing runtime contracts stay green, and no lazy IO or codec behavior appears.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| targeted `make test-unit` for containers, contracts, and collation | Verify public protocol behavior and unchanged loaded-runtime semantics. | yes |
| `make test-contract` | Verify existing runtime contract examples still pass through public container behavior. | yes |
| `make test-package` | Verify `rphys.data` exports and lightweight imports remain intentional. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: `Sample` and `Batch` expose `field_items()`; `SampleContract` and LIST collation use public container behavior; all existing loaded-runtime examples keep passing.
- Design-decision evidence: runtime interfaces are explicit before `SampleField` widens field-object semantics; no private `_field_items` dependency remains in collation.
- Documentation evidence: docstrings explain `FieldContainer` as a runtime field-access protocol, not a datasource, codec, or workflow abstraction.
- Scientific contract evidence: no new loading, collation policy, schema validation, or metadata interpretation is introduced.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-4/phases/field-container-protocol.md`
- Planning/refinement budget: one phase planner pass; one refiner pass only if protocol typing exposes a loaded-runtime regression
- Implementation/refinement budget: one executor pass; targeted refiner pass if existing runtime tests regress
- PR review budget: one reviewer pass focused on public API minimality and compatibility
- Blocker-resolution budget: return to planning if the protocol needs lazy-field-specific types before `SampleField` is implemented
- Pre-submit blocker gate: passed after PR-review blocker resolution
- Merge record: PR [#21](https://github.com/samcantrill/rphys/pull/21) squash-merged to `develop` at `c556572541df1b32a2d9625cc77993d53f57cdfd`

### Risks And Stop Conditions

- Risks: an over-specific protocol could constrain `SampleField`; an under-specific protocol could fail to help future operations.
- Stop conditions: implementing the protocol requires `SampleField`, codec imports, collation redesign, or breaking current `Sample`/`Batch` accessor semantics.
- Assumptions: Stage 4 can later extend annotations or compatible field-object types additively without changing the method names introduced here.

### Completion Summary

- Implementation: added public `FieldContainer`, public `field_items()` on `Sample`/`Batch`, public-shape validation in `SampleContract`, public field iteration in LIST collation, and `rphys.data` export/package coverage.
- Validation: `make validate-pr` passed after blocker fix: package 18, unit 257, contract 25, integration 1, e2e/acceptance not present, build succeeded, and `git diff --check` clean. Focused targeted runtime/package/contract checks also passed.
- PR: [#21](https://github.com/samcantrill/rphys/pull/21) opened against `develop`; PR title and target verified.
- Merge: squash-merged to `develop` 2026-05-14 at `c556572541df1b32a2d9625cc77993d53f57cdfd` via GitHub merge API after local validation and review.
- Follow-up: `_field_items()` remains a private compatibility alias; later lazy-field work may widen annotations additively but must preserve the public method names. Cleanup of the phase worktree/branch is pending after metadata push.

### Merge Record

- Phase: Preparation Phase 1, `field-container-protocol`
- Branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
- PR: [#21](https://github.com/samcantrill/rphys/pull/21)
- Base branch: `develop`
- Merge command: `gh api --method PUT repos/samcantrill/rphys/pulls/21/merge --field merge_method=squash ...`
- Merge result: merged
- Merge commit: `c556572541df1b32a2d9625cc77993d53f57cdfd`
- Branch cleanup: pending metadata push
- Worktree cleanup: pending metadata push
- Behavior implemented: public runtime field-container protocol, stable public field iteration, contract/collation use of public surface, and typed failures for malformed structural containers.
- Tests and validation: targeted unit/package/contract checks passed; `make validate-pr` passed with 301 total tests across present suites.
- Documentation: phase assignment, execution plan, PR body, and this merge record updated.
- Scientific contract implications: no payload loading, datasource, codec, builder, sampling, alignment, metadata interpretation, or collation policy changes were introduced.
- Remaining blockers: none.

## Preparation Phase 2: FieldSpec And FieldIndex Contract Tightening

Status: pending
Slug: `field-spec-index-contracts`
Branch: `agent/codecs-lazy-samples-prep2-field-spec-index-contracts`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep2-field-spec-index-contracts`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: remove shallow-mutation ambiguity from datasource schema declarations and align index wording with the actual subclass-based implementation before codec and builder APIs depend on these objects.
- Files/modules owned: `src/rphys/data/fields.py`; `src/rphys/io/indexes.py`; focused field/schema/index unit tests; lazy descriptor contract tests; package tests; docstrings in touched modules.
- Behavior implemented: `FieldSpec` becomes a frozen slotted value object while remaining explicitly unhashable; coercion uses `object.__setattr__`; `DataSourceSchema` continues to store `FieldSpec` declarations directly because they are now immutable; `FieldIndex` wording is changed from "protocol" to "base class" or "base interface" without adding registries or structural dispatch.
- Requirements supported: FR-1/FR-3 descriptor compatibility; FR-6 schema/provenance stability; FR-7 import/API boundary.
- Decisions applied: maintainer post-plan refinement for `FieldSpec` immutability and `FieldIndex` terminology; existing Stage 3 no-registry index boundary remains unchanged.
- Examples or demos covered: immutable datasource declarations and explicit index extension boundary.
- Out of scope: public `FieldSpec.to_dict()`, schema manifests, descriptor fingerprints, field-index registries, seconds/spatial indexes, codec behavior, `SampleField`, or `SampleBuilder`.
- Dependencies: Preparation Phase 1 can run before or in parallel for review, but this phase must merge before primary Stage 4 Phase 1 starts.

### Tasks

- Change `FieldSpec` to `@dataclass(frozen=True, slots=True)` and update `__post_init__` coercion with `object.__setattr__`.
- Set `FieldSpec.__hash__ = None` after class definition so hashability remains non-public and attempts to hash fail.
- Add or update tests that `FieldSpec` rejects mutation, preserves value equality, keeps copy/deepcopy value behavior, and remains unhashable.
- Add or update datasource schema tests proving stored `FieldSpec` declarations cannot be mutated through the schema mapping.
- Update `FieldIndex` docstrings and related test/docs wording to call it a base class or base interface, not a `Protocol`.
- Preserve current `FieldIndex` behavior: direct construction fails, `TemporalIndexSlice` is the only supported Stage 3 index, unknown serialized tags fail loudly, and no registry or `from_dict` is added to `FieldIndex`.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| targeted `make test-unit` for fields, datasource schemas, and indexes | Verify immutability, unhashability, schema declaration safety, and index base behavior. | yes |
| `make test-contract` | Verify runtime and lazy descriptor contracts still pass. | yes |
| `make test-package` | Verify public imports and surfaces are unchanged except intentional `FieldContainer` from Prep 1. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: `FieldSpec` is frozen and unhashable; `DataSourceSchema` cannot be mutated through stored declarations; `FieldIndex` behavior remains subclass-based with no registry.
- Design-decision evidence: the cleanup improves descriptor safety without adding serialization, manifests, or extension mechanisms.
- Documentation evidence: docstrings and tests no longer imply `FieldIndex` is a structural protocol.
- Scientific contract evidence: schema declarations are stable value records and index semantics remain field-native, integer, and explicitly limited.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass only if immutability exposes unexpected compatibility pressure
- Implementation/refinement budget: one executor pass; targeted refiner pass if runtime or lazy descriptor contracts regress
- PR review budget: one reviewer pass focused on compatibility and public API wording
- Blocker-resolution budget: return to planning if `FieldSpec` immutability breaks a documented public workflow or if `FieldIndex` needs a real extension protocol
- Pre-submit blocker gate: runtime, datasource schema, and lazy IO contracts remain green
- Merge record: pending

### Risks And Stop Conditions

- Risks: downstream code may have mutated `FieldSpec` after construction, but this conflicts with its value-object role and should be caught early before Stage 4 depends on it.
- Stop conditions: implementation requires public `FieldSpec` serialization, schema snapshots instead of freezing, or a registry/structural protocol for indexes.
- Assumptions: freezing `FieldSpec` is an acceptable compatibility tightening before public downstream use expands.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 1: Codec Public Contract Foundation

Status: pending
Slug: `codec-contract-foundation`
Branch: `agent/codecs-lazy-samples-p1-codec-contract-foundation`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p1-codec-contract-foundation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the Stage 4 IO public surface without implementing runtime lazy samples or full registry operation behavior.
- Files/modules owned: `src/rphys/io/codecs.py`; conditional `src/rphys/io/__init__.py` only if import-boundary tests support package re-export; exercised Stage 4 additions in `src/rphys/errors.py`; package import/export tests; focused IO unit tests for records/errors/imports.
- Behavior implemented: structural/duck-typed `FieldCodec` surface; `CodecCapabilities`; typed datasource-neutral `IOContext`, `LoadContext`, `SaveContext`, `CodecProbeResult`, `CodecLoadResult`, and `CodecSaveResult`; narrow `MetadataSavePolicy`; minimal exercised concrete errors; `SaveContext.target: FieldRef`; intentional lightweight exports from owning modules only.
- Requirements satisfied: FR-1; FR-6 context/provenance shape; FR-7 import/error boundary.
- Decisions applied: DD-1, DD-2, DD-4, DD-5, DD-8, and import-boundary parts of DD-3 and DD-10.
- Examples or demos covered: EX-3 context/save-target shape and EX-6 import boundary.
- Out of scope: resolver matching algorithms beyond construction-level shape, private synthetic codec behavior, `SampleField`, `SampleBuilder`, datasource scanning, datasource-aware codec contexts, export layouts, metadata handler interfaces, real codecs, hidden discovery, and global default registries.
- Dependencies: Preparation Phases 1 and 2; Stage 2 `FieldSpec`/`FieldValue`, Stage 3 `FieldRef`/`FieldView`/`ResourceRef`, broad error bases in `src/rphys/errors.py`, package import tests.

### Tasks

- Add `rphys.io.codecs` with code-backed public names only for the contract records needed by later phases.
- Define typed context/result records with minimal provenance-bearing fields; keep them primitive/reference-based, datasource-neutral, and free of manifest schema policy.
- Define `MetadataSavePolicy` as a small save-context enum with only exercised Stage 4 values: default reference-only behavior and explicit field-metadata inclusion for codecs that support it.
- Add only concrete errors exercised in this phase's tests; keep them under existing broad error bases.
- Update `rphys.io.__all__` only for code-backed names that remain lightweight at package import; otherwise keep canonical imports in `rphys.io.codecs`. Keep root `rphys` unchanged.
- Add focused unit tests for record construction, `SaveContext.target` type, immutability/value behavior where applicable, error inheritance/context, and descriptor non-mutation.
- Add import-boundary assertions that importing Stage 4 IO surfaces does not import heavy optional stacks or datasource modules.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify intentional public exports and lightweight import boundaries. | yes |
| targeted `make test-unit` for codec records/errors/imports | Verify context/result construction, error inheritance/context, and descriptor purity. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: typed context/result records instantiate with Stage 2/3 descriptors; `SaveContext.target` is a `FieldRef`; `MetadataSavePolicy` has code-backed Stage 4 semantics; no descriptor gains load/save behavior.
- Design-decision evidence: DD-1/DD-2/DD-4/DD-5/DD-8 are represented by code-backed names and exercised tests, with no mandatory stateful base class.
- Example/demo evidence: EX-3 and EX-6 have at least construction/import-level coverage.
- Documentation evidence: module/class docstrings describe the codec boundary, explicit save target, and non-goals without implying real codec support.
- Scientific contract evidence: records preserve field/view/resource/provenance references without adding datasource coupling, member, alignment, fingerprint, export layout, or manifest semantics.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass only for blocker findings
- Implementation/refinement budget: one executor pass; one targeted refiner pass if validation or review blocks
- PR review budget: one reviewer pass
- Blocker-resolution budget: return to planning if record shape requires unapproved datasource provenance in codec contexts, manifest, export, metadata handler, or discovery semantics
- Pre-submit blocker gate: no new public behavior outside DD-1/DD-2/DD-4/DD-5/DD-8
- Merge record: pending

### Risks And Stop Conditions

- Risks: over-wide result records, metadata policy values, or unused concrete errors could freeze an API before real codec evidence exists.
- Stop conditions: implementation needs a package tree instead of `rphys.io.codecs` facade, datasource-aware codec contexts, a public fake codec, registry discovery semantics, export target policy, metadata handler interface, or untraced public names.
- Assumptions: minimal typed records can carry enough provenance for phases 2 through 4 and can be extended additively later.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 2: Explicit Registry And Synthetic Codec Operations

Status: pending
Slug: `codec-registry-synthetic-ops`
Branch: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: prove deterministic codec resolution and dependency-light probe/load/save behavior through explicit registry instances.
- Files/modules owned: `src/rphys/io/codecs.py`; tests/support synthetic codec fixture or helper; `tests/unit/rphys/io/**`; `tests/contracts/test_codec_contract.py` or equivalent codec contract file; package tests only if exports change.
- Behavior implemented: `CodecRegistry` registration/resolution; support/capability matching for probe/load/save; typed missing/ambiguous/unsupported/dependency failures; private synthetic codec that probes without loading, loads supported indexed views, rejects unsupported indexes without full-load fallback, saves one logical field, exercises the narrow metadata save policies, and returns typed results.
- Requirements satisfied: FR-2; FR-3; FR-6 codec-side provenance/resource propagation; FR-7; FR-8 codec contract guardrails.
- Decisions applied: DD-2, DD-3, DD-4, DD-5, DD-8, DD-10, DD-11, and codec-operation portions of DD-1.
- Examples or demos covered: EX-2, EX-3, EX-4, and EX-5.
- Out of scope: global discovery, symbolic codec keys, real video/array codecs, public fake codec exports, hidden full-resource fallback, metadata manifest writes, metadata handler interfaces, export orchestration, and runtime `SampleField` integration.
- Dependencies: Primary Phase 1 context/result records and errors.

### Tasks

- Implement explicit registry storage and deterministic resolution that returns exactly one matching codec per operation/view/context.
- Validate structural codec shape at registration or operation boundary with typed diagnostics.
- Implement operation wrappers for probe/load/save that preserve context and wrap operation failures without swallowing dependency or slice semantics.
- Add private tests/support synthetic codec behavior with primitive resources and call counters for no-load assertions.
- Test missing, ambiguous, unsupported operation, unsupported `FieldView.field_index`, dependency-unavailable, and deterministic ordering cases.
- Test save of a logical `FieldValue` or payload to `SaveContext.target`; verify target/resource metadata in `CodecSaveResult`; verify `MetadataSavePolicy.REFERENCE_ONLY` does not persist metadata and `INCLUDE_FIELD_METADATA` persists only explicit field metadata supported by the synthetic codec.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| targeted `make test-unit` for `CodecRegistry` and synthetic codec behavior | Verify deterministic matching, structural acceptance, typed failures, unsupported slices, dependency boundary, probe/load/save results, and no hidden fallback. | yes |
| `make test-contract` for codec probe/load/save contract | Verify executable Stage 4 codec contract with private dependency-light codec. | yes |
| `make test-package` | Verify exports/import boundaries if this phase changes package surface. | conditional |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: no match, one match, ambiguous match, unsupported operation/index, dependency-unavailable, probe-without-load, load, metadata-policy, and save paths are covered.
- Design-decision evidence: DD-3 explicit registry behavior is deterministic; DD-11 fixture remains private to tests/support; no global discovery exists.
- Example/demo evidence: EX-2, EX-3, EX-4, and EX-5 have executable test coverage.
- Documentation evidence: docstrings clarify explicit registry instances, structural codec acceptance, and synthetic-test-only codec status.
- Scientific contract evidence: probe/load/save contexts preserve `FieldView.field_index`, ordered resources, field metadata, and target provenance without datasource-aware codec contexts, manifest writes, metadata handlers, or member/alignment semantics.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass only for blocker findings
- Implementation/refinement budget: one executor pass; one targeted refiner pass if validation or review blocks
- PR review budget: one reviewer pass
- Blocker-resolution budget: return to planning if registry matching needs symbolic names, hidden plugin discovery, priority heuristics not captured by accepted design, or public fake codec support
- Pre-submit blocker gate: no runtime sample behavior and no descriptor mutation
- Merge record: pending

### Risks And Stop Conditions

- Risks: matching predicates may become too broad or too narrow; unsupported slice failures could accidentally become hidden full-load fallback.
- Stop conditions: implementation requires global mutable registry state, symbolic names, public test codec exports, real optional dependencies, export layout policy, or unapproved resource/member binding semantics.
- Assumptions: explicit registry instances are enough for Stage 4 and later config layers can wrap them additively.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 3: Lazy `SampleField` Runtime Compatibility

Status: pending
Slug: `lazy-sample-field-runtime`
Branch: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p3-lazy-sample-field-runtime`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path if runtime compatibility review finds accessor ambiguity; otherwise fast path

### Scope

- Goal: add lazy field handles while preserving loaded `Sample` semantics.
- Files/modules owned: `src/rphys/data/sample_fields.py`; additive compatibility updates in `src/rphys/data/containers.py`; conditional `src/rphys/data/__init__.py` only if import-boundary tests support package re-export; focused data unit tests; runtime/lazy contract tests.
- Behavior implemented: `SampleField` as a `FieldValue`-compatible lazy object stored in `Sample` as the field object, not wrapped as a payload; compatibility with the public `FieldContainer` protocol and `field_items()` surface from Preparation Phase 1; unloaded/loaded/failed state; payload-triggered load exactly once; eager-load path at handle level; retained `CodecLoadResult` or retained error/context; repeated payload access returns retained payload or re-raises retained error; `Sample.field()` returns stored handle without loading; payload-demanding `Sample` access loads only where documented.
- Requirements satisfied: FR-4; FR-6 lazy-field provenance retention; FR-7 runtime import/error boundary.
- Decisions applied: DD-6, DD-7, DD-8, DD-10, DD-12, and loaded-runtime compatibility parts of DD-4.
- Examples or demos covered: EX-1.
- Out of scope: builder request selection, datasource scanning, cross-sample caches, retry/reset APIs, async state, device movement, operation pipelines, public loader handler interfaces, collation redesign, and replacement of loaded `FieldValue` behavior.
- Dependencies: Preparation Phase 1 public `FieldContainer` behavior; Primary Phases 1 and 2 load result/error behavior.

### Tasks

- Implement `SampleField` with inspectable state, stored context/provenance, private loader callback or resolver adapter, retained load result, retained error, and payload access semantics.
- Add eager-load support at the handle level using the same load path as payload access.
- Extend `FieldContainer` annotations only as needed for `SampleField` compatibility while preserving the public method names and loaded-runtime behavior introduced in Preparation Phase 1.
- Update `Sample` acceptance/coercion only as needed to store loaded `FieldValue`, raw payloads, or `SampleField` without forcing load on `field()` and without wrapping `SampleField` as another `FieldValue`'s payload.
- Ensure `Sample.require()` and other payload-demanding paths either load through `.payload` or fail with documented typed context.
- Preserve existing loaded-sample unit and contract behavior, including mutation/copy/role views, public `field_items()`, `FieldContainer` protocol expectations, and LIST collation expectations.
- Add tests for initial state, successful load once, repeated payload access, failed load retention/re-raise, eager path, no-load `field()` access, and loaded sample compatibility.
- Add import-boundary tests or assertions proving `rphys.data` package import stays lightweight if `SampleField` is re-exported; otherwise keep `rphys.data.sample_fields` as the canonical public import home.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| targeted `make test-unit` for `SampleField` and existing data containers/collation | Verify state transitions, payload-triggered loading, retained result/error, eager path, and loaded runtime compatibility. | yes |
| `make test-contract` including `tests/contracts/test_runtime_core_contract.py` and new lazy-field coverage | Verify public runtime contract remains valid with lazy fields added. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: unloaded handles do not load on `field()`; lazy handles are stored as field objects rather than payloads; payload access loads once; eager path uses the same state machine; failed state is inspectable and retained.
- Design-decision evidence: DD-6/DD-7 are tested directly; no `LazySample` fork, retry/reset API, async state, or hidden cache is introduced.
- Example/demo evidence: EX-1 lazy-load behavior is executable at the handle/sample level.
- Documentation evidence: docstrings explain `field()` versus payload access, state values, retained failures, and loaded-sample compatibility.
- Scientific contract evidence: field identity/provenance remains attached to the handle, and loaded values are not silently substituted in a way that erases diagnostics.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass expected if accessor semantics need test clarification
- Implementation/refinement budget: one executor pass; one targeted refiner pass if loaded runtime contracts regress
- PR review budget: one reviewer pass with emphasis on compatibility
- Blocker-resolution budget: return to planning if loaded `Sample` behavior cannot remain additive or if a parallel `LazySample` container becomes necessary
- Pre-submit blocker gate: existing runtime core contract must remain green or any failure must be explicitly accepted before continuing
- Merge record: pending

### Risks And Stop Conditions

- Risks: this is the highest compatibility-risk phase because existing callers may assume `Sample.field()` always returns an already materialized value.
- Stop conditions: implementation requires breaking loaded `Sample` contracts, wrapping lazy handles as payloads, replacing handles with loaded values and losing diagnostics, adding broad cache/retry policy, adding public loader handler interfaces, or changing collation semantics beyond documented payload-demanding behavior.
- Assumptions: `SampleField` can be made compatible with existing `FieldValue` access patterns without changing the meaning of loaded samples.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: `SampleBuilder` Bridge And Provenance Contracts

Status: pending
Slug: `sample-builder-provenance`
Branch: `agent/codecs-lazy-samples-p4-sample-builder-provenance`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p4-sample-builder-provenance`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: build lazy `Sample`s from one `IndexItem` with all/subset/one/probe/eager paths and locked provenance semantics.
- Files/modules owned: `src/rphys/data/sample_builders.py`; conditional `src/rphys/data/__init__.py` only if import-boundary tests support package re-export; builder/provenance unit tests; lazy sample contract tests; optional integration-style vertical slice if needed.
- Behavior implemented: `SampleBuildContext`; `SampleBuilder.build(index_item, requested=None, eager=False)`; `build_one(...)`; `probe(...)`; requested locator normalization; all/subset/one behavior; missing requested locators fail before partial output; probe does not load; eager build uses `SampleField` load path; locator/key/record/metadata/index/resources propagate through builder/sample provenance while codec contexts remain datasource-neutral; compound ordered resources are passed to codecs; descriptors and `IndexItem`s are not mutated.
- Requirements satisfied: FR-5; FR-6; FR-8; integration portions of FR-2, FR-3, and FR-4.
- Decisions applied: DD-3, DD-4, DD-6, DD-7, DD-8, DD-9, DD-10, DD-12, plus private synthetic codec support from DD-11 for validation only.
- Examples or demos covered: EX-1, EX-2, and EX-5.
- Out of scope: bulk datasource indexes, datasource scans, split/view/index manifest construction, item IDs/fingerprints, alignment/member binding semantics, datasource-aware codec contexts, model formatting, caching, device movement, export operations, and save orchestration beyond using codec contexts already defined.
- Dependencies: Preparation Phase 1 public `FieldContainer` behavior and Primary Phases 1 through 3.

### Tasks

- Implement `SampleBuildContext` with explicit registry/context inputs, builder-owned record/item provenance, and no hidden global registry.
- Implement requested-locator normalization and validate missing requests before creating or mutating output samples.
- Build all/subset/one lazy fields from a single `IndexItem`, preserving role-qualified `FieldLocator` and intrinsic `DataKey` separation.
- Wire built fields to `CodecRegistry`/load contexts through `SampleField` without loading unless eager is requested.
- Ensure built `Sample` objects satisfy the public `FieldContainer` protocol and expose lazy handles through `field()`/`field_items()` without private builder or collation hooks.
- Implement probe over all/subset/one requested locators and assert probe call paths never load payloads.
- Propagate `IndexItem.record`, `IndexItem.metadata`, `FieldView.field_index`, `FieldRef.metadata`, schema, locator, and ordered resources into builder/sample provenance, contexts, results, and handles as appropriate without adding `RecordRef` or `IndexItem` fields to codec contexts.
- Add compound multi-resource tests that assert order is preserved and no member/alignment/fingerprint semantics are invented.
- Add no-mutation assertions for descriptors and index items.
- Add import-boundary tests or assertions proving `rphys.data` package import stays lightweight if `SampleBuilder` is re-exported; otherwise keep `rphys.data.sample_builders` as the canonical public import home.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| targeted `make test-unit` for `SampleBuilder` | Verify all/subset/one/probe/eager paths, missing-request prevalidation, provenance propagation, no descriptor mutation, and no datasource scanning behavior. | yes |
| `make test-contract` for lazy sample construction, provenance, compound resources, and failure behavior | Verify Stage 4 bridge definition of done across IO descriptors, codec registry, lazy fields, and runtime samples. | yes |
| optional `make test-integration` | Run only if a single vertical-slice integration test is adopted because unit/contract tests are too fragmented. | conditional |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: one `IndexItem` can build all, subset, and one requested lazy field; missing requests fail before partial output; probe does not load; eager uses `SampleField` load path.
- Design-decision evidence: DD-9 builder scope is enforced; DD-10 provenance is preserved without adding unapproved identity/alignment/member semantics.
- Example/demo evidence: EX-1, EX-2, and EX-5 are covered by contract or integration-style tests.
- Documentation evidence: docstrings explain one-item builder scope, request semantics, eager behavior, no scanning, no model formatting, and no implicit caching.
- Scientific contract evidence: locator/key separation, field index, record provenance, field metadata, item metadata, and ordered resources remain inspectable; codec contexts remain datasource-neutral; unsupported slices fail loudly.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass available because this is the main bridge behavior phase
- Implementation/refinement budget: one executor pass; targeted refiner pass for validation or review blocker
- PR review budget: one reviewer pass with focus on scientific provenance and scope boundaries
- Blocker-resolution budget: return to planning if builder requires datasource index iteration, split semantics, datasource-aware codec contexts, export orchestration, model formatting, cache policy, member/alignment semantics, or new stable item identity
- Pre-submit blocker gate: no partial sample creation on missing requested locators; no probe load; no descriptor mutation; no datasource provenance pushed into codec contexts
- Merge record: pending

### Risks And Stop Conditions

- Risks: phase can grow broad if it absorbs registry/runtime fixes; provenance may be weakened if request normalization collapses locator roles into intrinsic keys or if record provenance is pushed into codec contexts instead of bridge/sample records.
- Stop conditions: implementation needs bulk index behavior, datasource scanning, explicit split selection, datasource-aware codec contexts, model tuple formatting, cache/device behavior, or new public API not traced to FR/DD/EX records.
- Assumptions: the accepted primary Phase 1 through 3 APIs provide enough context to implement builder behavior without redesign.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: Closeout Docs, Examples, And Validation Hardening

Status: pending
Slug: `closeout-docs-validation`
Branch: `agent/codecs-lazy-samples-p5-closeout-docs-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p5-closeout-docs-validation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path unless validation exposes behavioral regressions

### Scope

- Goal: make the implemented Stage 4 contract discoverable, validated, and ready for PR closeout without adding new behavior.
- Files/modules owned: public docstrings and docs touched by Stage 4 APIs; package tests; contract/unit validation hardening; optional glossary updates if public vocabulary changed; final validation evidence in PR body or phase artifact, not in this planning pass.
- Behavior implemented: no new behavior except narrow fixes needed to satisfy accepted phase criteria.
- Requirements satisfied: FR-1 through FR-8 closeout traceability and validation.
- Decisions applied: all DD-1 through DD-12 as implemented evidence; no new decisions.
- Examples or demos covered: EX-1 through EX-6.
- Out of scope: new APIs, real codecs, workflow/template edits, implementation-plan changes during the implementation workflow, datasource/export/training behavior, or broad refactors.
- Dependencies: Preparation Phases 1 and 2 plus Primary Phases 1 through 4.

### Tasks

- Review public docstrings/docs for `FieldContainer`, `FieldSpec` immutability, `FieldIndex` base-interface wording, codec boundary, explicit registry instances, structural codec extension, codec-context datasource neutrality, `field()` versus payload access, lazy state/error retention, save target/metadata policy, compound ordered resources, and non-goals.
- Ensure examples use local/private synthetic codecs and do not document the tests/support codec as production API.
- Refresh package/export expectations after all code-backed Stage 4 names are final.
- Harden tests only where they close gaps against accepted requirements, design decisions, examples, or validation strategy.
- Run required package/unit/contract checks and `git diff --check`.
- Broaden to `make test-summary`, `make test`, `make validate-pr`, and `uv lock --check` before merge or if package/dependency/shared surfaces changed enough to warrant it.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify final exports and lightweight import boundaries. | yes |
| `make test-unit` | Verify IO, data, errors, and existing source-mirrored tests after all phases. | yes |
| `make test-contract` | Verify codec and lazy sample contracts plus existing runtime contracts. | yes |
| `git diff --check` | Catch whitespace and Markdown/code formatting issues. | yes |
| `make test-summary` | Provide broader suite summary before merge when shared/public surfaces changed. | conditional |
| `make test` | Run full suite before merge when feasible or when closeout finds cross-suite risk. | conditional |
| `make validate-pr` | Run PR validation before final merge when feasible. | conditional |
| `uv lock --check` | Verify dependency metadata if dependencies or lock-sensitive metadata changed; expected to remain unchanged. | conditional |

### Acceptance Evidence

- Behavior evidence: all Stage 4 phase criteria are validated together and no closeout patch adds untraced behavior.
- Design-decision evidence: each DD-1 through DD-12 has code/test/doc evidence or remains a private implementation guardrail as approved.
- Example/demo evidence: EX-1 through EX-6 map to package, unit, contract, and optional integration coverage.
- Documentation evidence: public docs/docstrings explain boundaries, canonical focused-module imports, and non-goals without implying unsupported production formats or workflows.
- Scientific contract evidence: validation confirms stable field declarations, provenance, metadata separation, ordered compound resources, fail-loud unsupported slices, datasource-neutral codec contexts, no hidden full-load fallback, no implicit metadata persistence, and no datasource/export/training coupling.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one phase planner pass; one refiner pass only for validation blocker
- Implementation/refinement budget: one executor pass; targeted refiner pass if final checks fail
- PR review budget: one reviewer pass with emphasis on closeout drift and documentation accuracy
- Blocker-resolution budget: return to earlier phase or planning if closeout discovers behavior missing from the accepted plan
- Pre-submit blocker gate: no new behavior mixed into docs/validation closeout
- Merge record: pending

### Risks And Stop Conditions

- Risks: docs/validation closeout can mask behavioral changes if fixes are not traced to earlier phase acceptance criteria.
- Stop conditions: closeout requires new public behavior, public fake codec documentation, workflow/template edits, or design changes not approved in planning.
- Assumptions: behavior phases have already landed and closeout is limited to documentation, examples, validation hardening, and narrow fixes.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: each preparation phase and primary behavior phase runs its targeted package/unit/contract checks plus `git diff --check`; required closeout baseline is `make test-package`, `make test-unit`, `make test-contract`, and `git diff --check`; broaden to `make test-summary`, `make test`, `make validate-pr`, and `uv lock --check` before merge or if implementation touches package metadata, dependency metadata, shared containers, or contracts broadly.
- Docs/template checks: public docstrings/docs must cover `FieldContainer`, public field iteration, frozen/unhashable `FieldSpec`, `FieldIndex` base-interface wording, codec boundary, explicit registry instances, structural codec extension, datasource-neutral codec contexts, `field()` vs payload access, lazy state/error retention, save target and metadata policy, compound ordered resources, canonical focused-module imports, and non-goals; private synthetic codecs must not be presented as production formats.
- Scientific/workflow contract checks: preserve stable field declarations, `FieldLocator`/`DataKey` separation, `FieldRef.schema`, `FieldRef.metadata`, `FieldView.field_index`, `IndexItem.record`, `IndexItem.metadata`, ordered resources, descriptor purity, explicit metadata save policy, fail-loud unsupported slices, no hidden full-load fallback, no cache/discovery/export/training/workflow coupling, no datasource provenance in codec contexts, and no unapproved member/alignment/fingerprint semantics.
- Example/demo checks: EX-1 through EX-6 must map to executable package/unit/contract coverage; optional integration coverage is allowed only when it materially clarifies the vertical slice without broadening scope.
- Manual review focus: public API minimality, field-container compatibility, immutable descriptor declarations, import-boundary cleanliness, deterministic resolution, datasource-neutral codec contexts, lazy access semantics, loaded runtime compatibility, provenance retention, test-support privacy, and phase ownership boundaries.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Initial draft did not explicitly name functional requirements per phase even though the plan-quality gate requested FR traceability. | concern | Added `Requirements satisfied` entries to each primary phase scope while preserving the approved primary five-phase boundaries. | resolved |
| Post-plan interface review found three pre-Stage-4 cleanup issues: lack of a public field-container protocol, mutable `FieldSpec` declarations inside descriptor schemas, and `FieldIndex` wording that implied a structural protocol while implementation is subclass-based. | concern | Added two preparation phases before primary Stage 4 execution: `field-container-protocol` and `field-spec-index-contracts`. | resolved |
| Primary Stage 4 phases need minor dependency and acceptance refinements after the preparation phases. | concern | Updated primary Phase 1 to depend on preparation completion; updated primary Phase 3 to build on `FieldContainer` and public `field_items()`; updated primary Phase 4 to require built samples satisfy `FieldContainer`; updated closeout docs/validation to cover the cleanup surfaces. | resolved |
| Phase order, ownership, validation commands, examples, risks, and stop conditions remain implementation-ready after the two preparation phases. | note | Keep the plan as two preparation phases followed by five primary phases, and return to planning if a phase needs untraced datasource-aware codec contexts, export, cache, model, alignment, member, global registry, metadata handler, public fake-codec behavior, or lazy-field-specific protocol redesign before primary Phase 3. | clear |

Gate result:

- Status: passed after post-revision specialist review; ready for maintainer approval
- Review evidence: implementation plan reviewed against `docs/roadmap/stage-4/planning.md`, the workflow hard gates, passed plan-quality evidence, maintainer-requested interface refinements, two new preparation phases, five primary shaped phases, FR-1 through FR-8, DD-1 through DD-12, and EX-1 through EX-6.
- Accepted risks: `FieldContainer` becomes a new public provisional runtime contract before lazy fields land; `FieldSpec` immutability may catch unsupported downstream mutation early; `SampleField` widens `Sample.field()` expectations by allowing unloaded handles; minimal typed IO records and metadata-policy values may need additive extension when real codecs arrive; registry matching must avoid hidden priority semantics.
- Revisit triggers: return to planning if any phase needs lazy-field-specific protocol redesign before primary Phase 3, datasource-aware codec contexts, datasource scanning, export orchestration, implicit caching, model formatting, alignment/member semantics, public fake codec support, public metadata handler interfaces, global discovery, process-global mutable registry state, new stable item identity, or other public behavior not traced to FR/DQ/DD/EX records.

## Final Approval

- Approval status: pending maintainer approval
- Approved scope: not yet approved for implementation; proposed scope is two preparation phases followed by the five primary Stage 4 phases listed above, with no additional blockers from post-revision specialist review.
- Accepted risks: pending approval; proposed accepted risks are limited to the new provisional `FieldContainer` public contract, `FieldSpec` immutability tightening, documented lazy-field accessor widening, minimal additive codec record/metadata-policy evolution, and deterministic registry matching discipline.
- Deferred items: real codec catalog, optional heavy integrations, datasource discovery/index manifests, operation/export/training orchestration, caches, model formatting, spatial/seconds slicing, multi-member/nested samples, stable item IDs/fingerprints, alignment/member semantics, and workflow/artifact runtime.
