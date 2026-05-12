# Roadmap Stage 1 Implementation Plan

Status: implemented
Roadmap version: `v1`
Planning document: `docs/roadmap/stage-1/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: complete
Blockers: none

## Summary

- Goal: implement Milestone 1 shared data vocabulary primitives, constants, locators, and typed diagnostics as the canonical naming layer for later `rphys` stages.
- Approved behavior: strict lowercase ASCII validation, validated `str` subclasses for extensible vocabulary, closed `FieldRole(StrEnum)`, frozen `FieldLocator.parse()`, validator-specific semantic errors, no silent normalization, and submodule-only public imports.
- Key design constraints: stdlib-only, no runtime dependencies, no root or `rphys.data` convenience re-exports, no registries, no runtime containers, no serialization/config integration, no workflow/artifact scope, and no deferred IO/datasource/operation/model/training behavior.
- Examples covered: canonical rPPG `DataKey` examples, role-qualified locator round trips, schema/type separation, grouped metadata constants, split labels, typed diagnostics, no normalization, and import-boundary guardrails.
- Source phase shaping: approved five-phase sketch in `docs/roadmap/stage-1/planning.md`: diagnostic/DataKey foundation; metadata/split vocabularies; schema/type vocabularies; field roles/locators; contract/package/docs hardening.
- Source plan quality gate: passed on 2026-05-12 / R18 with no blocking findings.
- Out of scope: `FieldSpec`, `FieldValue`, `Sample`, `Batch`, collation, lazy IO references, codecs, datasources, operations, transforms, models, losses, metrics, learners, trainers, prediction, evaluation, analysis, workflow runtime, artifact references, registries, root/data exports, runtime dependencies, and config/serialization hooks.

## Implementation Workflow State

- Implementation-plan quality gate: passed 2026-05-12
- Review pass: passed 2026-05-12
- Refinement pass: not required
- Confirmation review: not required
- Automatic merge mode: enabled; this retrofit completed through local phase branches and worktrees, then merged to `develop`
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`
- Execution note: phases 1-5 were implemented sequentially in dedicated
  phase worktrees under `/home/samcantrill/work/rphys-worktrees`. No remote
  GitHub PRs were opened in this local retrofit; each phase has a named branch,
  validation evidence, and a merge record into local `develop`.

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `diagnostic-datakey-foundation` | pr_open | `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-1-diagnostic-datakey-foundation` | [#5](https://github.com/samcantrill/rphys/pull/5) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 1: Diagnostic And DataKey Foundation` | `rphys.errors`, `rphys.data.keys`, optional private lexical helpers, focused unit/package tests | Establish typed diagnostics and `DataKey` grammar | Focused unit tests plus targeted package import checks | Canonical rPPG field keys and invalid key forms |
| 2 | `metadata-split-vocabularies` | pr_open | `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-2-metadata-split-vocabularies` | [#6](https://github.com/samcantrill/rphys/pull/6) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 2: Metadata And Split Vocabularies` | `rphys.data.metadata`, `rphys.data.splits`, focused unit/package tests | Add metadata and split labels without storage or loop behavior | Unit tests for constants/validation and package import checks | Metadata/split context and grouped constants |
| 3 | `schema-type-vocabularies` | pr_open | `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-3-schema-type-vocabularies` | [#9](https://github.com/samcantrill/rphys/pull/9) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 3: Schema And Data Type Vocabularies` | `rphys.data.schemas`, `rphys.data.types`, focused unit/package tests | Add schema identity and backend-agnostic data categories | Unit tests for schema/type grammar and package import checks | Schema/type separation |
| 4 | `field-role-locators` | pr_open | `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-4-field-role-locators` | [#7](https://github.com/samcantrill/rphys/pull/7) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 4: Field Roles And Locators` | `rphys.data.locators`, locator unit tests, targeted contract seeds | Add closed roles and component-preserving locators | Unit tests for roles, parsing, round trips, and component failures | Role-qualified training/prediction locators |
| 5 | `contract-package-docs-hardening` | pr_open | `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-5-contract-package-docs-hardening` | [#8](https://github.com/samcantrill/rphys/pull/8) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 5: Contract, Package, And Documentation Hardening` | `tests/contracts`, `tests/package`, docs/docstrings, cross-phase fixes only | Harden public contract, imports, docs, and validation evidence | `make test-unit`, `make test-package`, `make test-contract`, `uv lock --check`, `git diff --check` | Full approved example set and no runtime/workflow coupling |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Validation and phase-shaping gate is approved; plan quality gate passed; no design decision is blocked; no unresolved `needs maintainer discussion` decision remains; DD-8 has traceability plus adversarial review evidence; DD-9 is no longer auto-approved and is approved as a recorded recommendation. | `docs/roadmap/stage-1/planning.md` approvals, design triage, auto-approved traceability, phase shaping, and plan quality gate | Proceed to implementation-plan quality review, then phase execution through the implementation workflow. | clear |

## Phase 1: Diagnostic And DataKey Foundation

Status: merged
Slug: `diagnostic-datakey-foundation`
Branch: `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-1-diagnostic-datakey-foundation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-1-p1-diagnostic-datakey-foundation`
PR: [#5](https://github.com/samcantrill/rphys/pull/5) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 1: Diagnostic And DataKey Foundation`
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the Stage 1 typed diagnostic baseline and first validated vocabulary primitive.
- Files/modules owned: `src/rphys/errors.py`; `src/rphys/data/keys.py`; optional private `src/rphys/data/_validation.py`; `tests/unit/rphys/test_errors.py`; `tests/unit/rphys/data/test_keys.py`; targeted package tests in `tests/package/`.
- Behavior implemented: validator-specific Stage 1 errors; `DataKey(str)` construction; reserved and custom key grammar; no normalization; exact string-like behavior inherited from `str`; representative key constants if implemented by the approved key module shape.
- Decisions applied: DD-1, DD-3, DD-4, DD-7, DD-8, DD-9.
- Examples or demos covered: `video.rgb`, `signal.bvp.reference`, `timestamps.video.seconds`, `landmarks.face.mediapipe_468`, `mask.face.skin`, `quality.face_visibility`, `custom.demo.embedding`; invalid `inputs/video.rgb`, `Video.RGB`, `video/rgb`, and `video.rgb#source_id`.
- Out of scope: locators, metadata/split constants, schema/type labels, runtime field containers, registries, root or `rphys.data` exports, config/serialization hooks, optional dependencies, and deferred runtime packages.
- Dependencies: Stage 0 broad error classes and empty package homes.

### Tasks

- Add `InvalidDataKeyError`, `InvalidFieldLocatorError`, `InvalidSchemaNameError`, `InvalidDataTypeError`, `InvalidMetadataKeyError`, and `InvalidSplitNameError` without changing Stage 0 error mechanics.
- Implement `DataKey` with strict lowercase ASCII dotted grammar, reserved namespace handling, malformed `custom` rejection, and typed context-rich failures.
- Add private lexical helpers only if duplication justifies them, and keep them primitive, private, stdlib-only, and non-semantic.
- Preserve empty `rphys.__all__` and `rphys.data.__all__`; expose only intentional module-level `__all__` from the owned modules.
- Add focused unit and package coverage for touched surfaces.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify Stage 1 errors and `DataKey` behavior on the unit surface. | yes |
| Targeted `tests/package` invocation or `make test-package` | Verify lightweight imports, error exports, and no root/data re-export expansion. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: accepted/rejected key examples pass; invalid public values raise `InvalidDataKeyError`.
- Design-decision evidence: errors preserve `.message`/`.context`; private helpers remain lexical and unexported; root/data public surfaces remain empty.
- Example/demo evidence: canonical rPPG key examples are covered by tests or docstrings.
- Documentation evidence: module docstrings state keys are intrinsic identities, not roles, locators, schemas, codecs, config paths, or runtime fields.
- Scientific contract evidence: no physiological processing, leakage policy, runtime containers, or workflow/artifact behavior is introduced.

### Phase Workflow State

- Phase execution plan: completed in phase worktree from approved implementation plan
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if public grammar or error taxonomy conflicts with approved decisions
- Pre-submit blocker gate: no helper broadening, no root/data exports, no runtime dependency additions
- Merge record: branch commit merged into local `develop` after validation

### Risks And Stop Conditions

- Risks: over-generalized private helpers; brittle tests over exact error prose; accidental root/data re-exports.
- Stop conditions: implementation requires public normalizers, broad base validator classes, registries, runtime dependency additions, or changed approved error names.
- Assumptions: exact diagnostic prose and final context-key set are implementation details, while high-value context remains required.

### Completion Summary

- Implementation: added Stage 1 validator-specific errors, private lexical
  helpers, `DataKey`, reserved namespace grammar, and focused tests.
- Validation: phase worktree `make test-unit`, `make test-package`, and
  `git diff --check` passed; final validation also passed after all merges.
- PR: no remote PR opened; local branch was used for the phase.
- Merge: merged to local `develop`.
- Follow-up: none.

## Phase 2: Metadata And Split Vocabularies

Status: merged
Slug: `metadata-split-vocabularies`
Branch: `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-2-metadata-split-vocabularies`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-1-p2-metadata-split-vocabularies`
PR: [#6](https://github.com/samcantrill/rphys/pull/6) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 2: Metadata And Split Vocabularies`
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: add descriptive metadata keys and split labels without implying storage, grouping, leakage, or trainer behavior.
- Files/modules owned: `src/rphys/data/metadata.py`; `src/rphys/data/splits.py`; `tests/unit/rphys/data/test_metadata_keys.py`; `tests/unit/rphys/data/test_splits.py`; targeted package tests.
- Behavior implemented: `MetadataKey(str)`; generic/core metadata constants `SOURCE_ID`, `GROUP`, `SPLIT`; rphys domain-context constants `SUBJECT_ID`, `RECORD_ID`, `SAMPLE_ID`; `SplitName(str)`; split constants `TRAIN`, `VALID`, `TEST`, `PREDICT`.
- Decisions applied: DD-1, DD-3, DD-4, DD-6, DD-7, DD-8, DD-9.
- Examples or demos covered: grouped metadata constants, `SPLIT` as metadata that may hold a split label, custom metadata/split names, split labels as partition/usage metadata rather than trainer loop modes.
- Out of scope: datasource records, missing-metadata lookup, leakage checks, grouping algorithms, split construction, trainer/learner loop modes, runtime containers, and convenience re-exports.
- Dependencies: Phase 1 diagnostics and any approved private lexical helper.

### Tasks

- Implement metadata and split validators using the approved strict grammar and direct validator-specific errors.
- Keep metadata constants grouped in documentation/docstrings without making subject, record, or sample metadata mandatory.
- Keep split constants in `rphys.data.splits`; do not place split labels in `rphys.data.metadata`.
- Add unit coverage for constants, extensible names, invalid separators, and non-behavior assertions.
- Extend targeted package import checks for the two new modules.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify metadata and split validation, constants, and typed errors. | yes |
| Targeted `tests/package` invocation or `make test-package` | Verify lightweight submodule imports and empty root/data exports. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: metadata and split constructors enforce approved grammar; constants are validated instances.
- Design-decision evidence: metadata constants are grouped; split constants live only in `rphys.data.splits`; no loop or datasource behavior appears.
- Example/demo evidence: `SOURCE_ID`, `GROUP`, `SPLIT`, `SUBJECT_ID`, `RECORD_ID`, `SAMPLE_ID`, `TRAIN`, `VALID`, `TEST`, and `PREDICT` are covered.
- Documentation evidence: docstrings distinguish metadata from fields, split labels from trainer modes, and constants from policy.
- Scientific contract evidence: no leakage policy, grouping algorithm, missing-value policy, or split construction is implied.

### Phase Workflow State

- Phase execution plan: completed in phase worktree from approved implementation plan
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if metadata constants become policy or split names require loop semantics
- Pre-submit blocker gate: no datasource/trainer behavior, no root/data exports, no runtime dependency additions
- Merge record: branch commit merged into local `develop` after validation

### Risks And Stop Conditions

- Risks: constants may be misread as mandatory metadata or leakage policy; split labels may be coupled to trainer modes.
- Stop conditions: implementation requires storage, missing-metadata lookup, split algorithms, leakage checks, or trainer loop behavior.
- Assumptions: downstream metadata and split names extend through validated constructors, not registries.

### Completion Summary

- Implementation: added `MetadataKey`, grouped metadata constants,
  `SplitName`, split constants, docstrings, and focused tests.
- Validation: phase worktree `make test-unit`, `make test-package`, and
  `git diff --check` passed; final validation also passed after all merges.
- PR: no remote PR opened; local branch was used for the phase.
- Merge: merged to local `develop`.
- Follow-up: none.

## Phase 3: Schema And Data Type Vocabularies

Status: merged
Slug: `schema-type-vocabularies`
Branch: `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-3-schema-type-vocabularies`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-1-p3-schema-type-vocabularies`
PR: [#9](https://github.com/samcantrill/rphys/pull/9) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 3: Schema And Data Type Vocabularies`
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: add schema identity and backend-agnostic data category labels while preserving their separation.
- Files/modules owned: `src/rphys/data/schemas.py`; `src/rphys/data/types.py`; `tests/unit/rphys/data/test_schemas.py`; `tests/unit/rphys/data/test_types.py`; targeted package tests.
- Behavior implemented: `SchemaName(str)` with approved versioned-name grammar; `DataType(str)` with constants for `video`, `signal`, `timestamps`, `landmarks`, `mask`, `embedding`, `label`, `quality`, `annotation`, and `metadata`.
- Decisions applied: DD-1, DD-3, DD-4, DD-5, DD-7, DD-8, DD-9.
- Examples or demos covered: `SchemaName("video.rgb.v1")`, `SchemaName("signal.bvp.v1")`, data category constants, invalid versionless/path-like/codec-like/schema-type-confused values.
- Out of scope: payload schemas, shape/unit validation, coordinate frames, sample rates, codec keys, manifest/config integration, Python/tensor/backend dtype inspection, runtime `FieldSpec`, and optional scientific dependencies.
- Dependencies: Phase 1 diagnostics and any approved private lexical helper. Phase 2 is not required by behavior, but this plan keeps phases sequential for review clarity.

### Tasks

- Implement schema-name validation with strict versioned grammar and typed failures.
- Implement `DataType` in `rphys.data.types` with the approved backend-agnostic constants.
- Document that schema names are interpretation/layout/version labels and data types are category labels, not payload validators or backend dtypes.
- Add unit coverage for constants, valid/invalid schemas, edge versions, and schema/type separation.
- Add targeted package import checks for schemas and types.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify schema/type validators, constants, typed errors, and separation examples. | yes |
| Targeted `tests/package` invocation or `make test-package` | Verify lightweight imports and empty root/data exports. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: schema examples validate; malformed schemas and data types fail with `InvalidSchemaNameError` or `InvalidDataTypeError`.
- Design-decision evidence: `DataType` lives in `rphys.data.types`; constants are broad categories; no backend dtype inspection or schema payload behavior exists.
- Example/demo evidence: schema/type separation examples are covered in unit tests and docstrings.
- Documentation evidence: docs distinguish schema names from data keys, codec keys, manifests, Python dtypes, tensor dtypes, backend dtypes, and payload schemas.
- Scientific contract evidence: no shape, unit, coordinate-frame, sample-rate, or payload-layout validation is implied.

### Phase Workflow State

- Phase execution plan: completed in phase worktree from approved implementation plan
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if schema or data type behavior requires backend/runtime semantics
- Pre-submit blocker gate: no optional dependencies, no payload schema implementation, no config/serialization hooks
- Merge record: branch commit merged into local `develop` after validation

### Risks And Stop Conditions

- Risks: edge grammar debates such as `v0`; accidental conflation of data categories with schema names or backend dtypes.
- Stop conditions: implementation needs payload validation, shape/unit semantics, codec resolution, manifests, or backend dtype imports.
- Assumptions: version-edge choices can be resolved within approved strict grammar and recorded in tests/docstrings.

### Completion Summary

- Implementation: added `SchemaName`, `DataType`, approved category constants,
  schema/type docstrings, and tests for version and backend-dtype separation.
- Validation: phase worktree `make test-unit`, `make test-package`, and
  `git diff --check` passed; final validation also passed after all merges.
- PR: no remote PR opened; local branch was used for the phase.
- Merge: merged to local `develop`.
- Follow-up: none.

## Phase 4: Field Roles And Locators

Status: merged
Slug: `field-role-locators`
Branch: `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-4-field-role-locators`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-1-p4-field-role-locators`
PR: [#7](https://github.com/samcantrill/rphys/pull/7) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 4: Field Roles And Locators`
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: add role-qualified addresses after component vocabularies exist.
- Files/modules owned: `src/rphys/data/locators.py`; `tests/unit/rphys/data/test_locators.py`; targeted package tests; targeted contract examples if useful.
- Behavior implemented: closed `FieldRole(StrEnum)` with `inputs`, `targets`, `source`, `predictions`, `outputs`, `losses`, `objectives`, `metrics`, `metadata`, and `diagnostics`; frozen/slotted `FieldLocator` with components `role`, `key`, and optional `metadata_key`; `FieldLocator.parse()` and `str(locator)` for `<role>/<data-key>[#<metadata-key>]`.
- Decisions applied: DD-2, DD-3, DD-4, DD-7, DD-8, DD-9, plus component decisions from DD-1 and DD-6.
- Examples or demos covered: `inputs/video.rgb`, `targets/signal.bvp.reference`, `predictions/signal.bvp`, `metrics/quality.face_visibility`, `diagnostics/quality.face_visibility#source_id`.
- Out of scope: runtime lookup, mutation, routing, collation, container access, datasource indexing, operation wiring, metadata loading, registries, root/data exports, and normalization.
- Dependencies: Phases 1 and 2. Phase 3 is not behaviorally required for locators but precedes this phase in the sequential plan.

### Tasks

- Implement `FieldRole` as the approved closed role set.
- Implement frozen `FieldLocator` construction, component coercion, parsing, and canonical string formatting.
- Ensure direct component constructors raise their own validator errors, while `FieldLocator.parse()` raises `InvalidFieldLocatorError` for whole-locator syntax or component failures with useful component context.
- Add unit coverage for every role, direct construction, parsing, optional metadata selectors, equality/frozen behavior, bad separators, unknown roles, component failures, and no lookup behavior.
- Add targeted package and, if useful, contract seeds for locator round trips.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify role enum, locator construction, parse/string round trips, component preservation, and failure behavior. | yes |
| Targeted `tests/package` invocation or `make test-package` | Verify lightweight imports and empty root/data exports. | yes |
| Targeted `make test-contract` if contract seeds are added | Verify locator examples expected by later stages. | conditional |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: all approved roles validate; locator examples round trip; parser failures are `InvalidFieldLocatorError`.
- Design-decision evidence: locator stores separate role, `DataKey`, and optional `MetadataKey`; no normalization or runtime lookup occurs.
- Example/demo evidence: role-qualified training/prediction/metric/diagnostic examples are tested.
- Documentation evidence: docstrings state role is runtime addressing context, not intrinsic field identity.
- Scientific contract evidence: locators do not imply data access, mutation, collation, operation routing, metadata loading, or datasource behavior.

### Phase Workflow State

- Phase execution plan: completed in phase worktree from approved implementation plan
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if custom roles, lookup semantics, or public locator normalization become necessary
- Pre-submit blocker gate: no runtime container/access behavior, no registries, no convenience exports
- Merge record: branch commit merged into local `develop` after validation

### Risks And Stop Conditions

- Risks: locator parsing may accidentally normalize values or hide component failures; closed roles may expose pressure for custom roles.
- Stop conditions: implementation requires runtime lookup, role registries, datasource access, container semantics, or a public role-extension API.
- Assumptions: closed role set remains the approved Stage 1 compatibility surface.

### Completion Summary

- Implementation: added closed `FieldRole`, frozen/slotted `FieldLocator`,
  parser/string round trips, component coercion, whole-locator parse errors,
  and locator tests.
- Validation: phase worktree `make test-unit`, `make test-package`, and
  `git diff --check` passed; final validation also passed after all merges.
- PR: no remote PR opened; local branch was used for the phase.
- Merge: merged to local `develop`.
- Follow-up: none.

## Phase 5: Contract, Package, And Documentation Hardening

Status: merged
Slug: `contract-package-docs-hardening`
Branch: `agent/milestone-1-naming-locators-schemas-metadata-errors-phase-5-contract-package-docs-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-1-p5-contract-package-docs-hardening`
PR: [#8](https://github.com/samcantrill/rphys/pull/8) `agent/Milestone 1 Naming, Locators, Schemas, Metadata, And Errors - Phase 5: Contract, Package, And Documentation Hardening`
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: convert the implemented vocabulary into a downstream-safe public contract.
- Files/modules owned: `tests/contracts/`, especially a focused Stage 1 vocabulary contract test; `tests/package/` import/API/dependency guardrails; module docstrings and optional README/docs snippets only if needed; small fixes in Stage 1 modules required by contract/package review.
- Behavior implemented: no new public vocabulary behavior except corrections needed to satisfy the approved Stage 1 contract.
- Decisions applied: DD-4 and DD-9 across the full surface, plus final consistency checks for DD-1 through DD-8.
- Examples or demos covered: full approved example set across keys, locators, schemas/types, metadata/splits, typed diagnostics, no normalization, no runtime/config/workflow/artifact coupling, and empty root/data exports.
- Out of scope: new public APIs, broad integration tests, runtime containers, deferred package behavior, implementation-plan artifact edits from implementation phases, and behavior hidden under hardening.
- Dependencies: Phases 1 through 4.

### Tasks

- Add narrow contract tests for the recorded valid/invalid examples, locator round trips, schema/type separation, metadata/split distinctions, typed diagnostics, no normalization, and deferred-scope assertions.
- Extend package tests for lightweight submodule imports, intentional module `__all__`, empty `rphys.__all__` and `rphys.data.__all__`, unchanged runtime dependencies, no optional stack imports, and no duplicate vocabulary surfaces in deferred package homes.
- Finalize module docstrings and optional user-facing documentation only where needed to make public import paths, grammar, typed errors, and exclusions clear.
- Run final validation and record any command that cannot run with residual risk.
- Stop and return to planning if hardening discovers a need for new public behavior.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify all source-mirrored vocabulary behavior after cross-phase fixes. | yes |
| `make test-package` | Verify package/import/dependency guardrails. | yes |
| `make test-contract` | Verify public Stage 1 compatibility examples and deferred-scope assertions. | yes |
| `uv lock --check` | Verify dependency lock consistency and no unintended runtime dependency drift. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |
| `make test` | Broader regression pass for the stage. | recommended |
| `make test-summary` | Produce test summary evidence when available. | recommended |
| `make validate-pr` | Final PR-level validation before merge. | recommended |

### Acceptance Evidence

- Behavior evidence: unit and contract tests cover every approved public vocabulary family.
- Design-decision evidence: root/data exports remain empty; module `__all__` values are intentional; no registries, runtime dependencies, or deferred behavior appear.
- Example/demo evidence: the approved planning examples are executable contract seeds.
- Documentation evidence: docstrings or docs state import paths, grammar, typed errors, no-normalization behavior, schema/type separation, metadata/split distinctions, and deferred scope.
- Scientific contract evidence: tests/docs assert no shape/unit/sample-rate validation, no backend dtype inspection, no leakage/grouping/split algorithm, no metadata missing-value policy, and no workflow/artifact coupling.

### Phase Workflow State

- Phase execution plan: completed in phase worktree from approved implementation plan
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: expanded because this phase audits the full public contract
- Blocker-resolution budget: return to planning for any new public behavior or scope expansion
- Pre-submit blocker gate: no hidden API expansion under hardening; validation evidence recorded
- Merge record: branch commit merged into local `develop` after validation

### Risks And Stop Conditions

- Risks: hardening may hide new behavior; broad tests may over-specify private implementation details; docs may imply deferred scientific/runtime behavior.
- Stop conditions: contract/package review requires new vocabulary behavior, new public exports, optional dependencies, runtime containers, config/serialization hooks, or workflow/artifact scope.
- Assumptions: final hardening mostly adds cross-cutting tests/docs and small fixes, not new design decisions.

### Completion Summary

- Implementation: added narrow Stage 1 contract tests, package import/API
  guardrails, lightweight submodule import checks, duplicate-vocabulary checks,
  and public docstrings covering grammar and deferred scope.
- Validation: `make test-unit`, `make test-package`, `make test-contract`,
  `make test`, `make test-summary`, `make validate-pr`, `uv lock --check`,
  and `git diff --check` passed.
- PR: no remote PR opened; local branch was used for the phase.
- Merge: merged to local `develop`.
- Follow-up: none.

## Cross-Phase Validation

- Full relevant test command: `make test-unit`, `make test-package`, `make test-contract`, `uv lock --check`, and `git diff --check`; run `make test`, `make test-summary`, and `make validate-pr` before final merge when feasible.
- Docs/template checks: module docstrings and any optional README/docs changes must match approved import paths, grammars, typed errors, no-normalization behavior, schema/type separation, metadata/split distinctions, and deferred scope.
- Scientific/workflow contract checks: assert Stage 1 vocabulary does not implement physiological processing, sampling, alignment, filtering, normalization, leakage policy, grouping algorithms, split construction, metadata missing-value policy, runtime containers, config/serialization, workflow runtime, or artifacts.
- Example/demo checks: use approved planning examples as contract seeds and keep exhaustive edge cases in unit tests.
- Manual review focus: public grammar lock-in, exception names and inheritance, `FieldLocator.parse()` failure ownership, private helper boundaries, empty root/data exports, runtime dependency hygiene, and absence of duplicate vocabularies in deferred packages.

### Final Validation Evidence

| Command/check | Result | Notes |
| --- | --- | --- |
| `make test-unit` | passed | 147 unit tests passed. |
| `make test-package` | passed | 12 package/API tests passed. |
| `make test-contract` | passed | 6 contract tests passed. |
| `make test` | passed | 165 default-suite tests passed. |
| `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` | passed | Direct `uv lock --check` without the repo cache env hit the read-only home cache; rerun with the repository Makefile cache path passed. |
| `git diff --check` | passed | No whitespace errors. |
| `make test-summary` | passed | Wrote `build/test-summary.md`; package/unit/contract passed and integration/e2e/acceptance were not present. |
| `make validate-pr` | passed | Lock check, summary, build, and diff check passed; built source and wheel distributions under ignored `dist/`. |

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No implementation-readiness blocker found. | note | Validation/phase-shaping is approved, plan quality gate passed, all design decisions are approved or reviewed, and auto-approved DD-8 has traceability plus adversarial review evidence. | reviewed |

Gate result:

- Status: pass
- Review evidence: manager review on 2026-05-12 verified traceability from `docs/roadmap/stage-1/planning.md` approvals through R18, preservation of the approved five-phase sketch, bounded ownership, validation alignment, implementation-ready stop conditions, and no hidden scope expansion.
- Accepted risks: exact diagnostic prose/context keys, schema `v0` behavior, and split-name dot handling remain implementation details constrained by approved strict grammar; Phase 5 may reveal small contract/documentation fixes but must not add new public behavior.
- Revisit triggers: implementation needs runtime containers, registries, root or `rphys.data` convenience exports, public normalization helpers, optional/runtime dependencies, serialization/config integration, workflow/artifact scope, datasource/IO/operation/model/loss/metric/training/evaluation behavior, broader scientific semantics, or a contradiction between approved examples and validators.

## Final Approval

- Approval status: approved 2026-05-12 / R19
- Approved scope: five implementation phases: diagnostic/`DataKey` foundation; metadata/split vocabularies; schema/type vocabularies; field roles/locators; contract/package/docs hardening.
- Accepted risks: exact diagnostic prose/context keys, schema `v0` behavior, split-name dot handling, and minor contract/documentation fixes remain implementation details constrained by the approved planning record.
- Deferred items: runtime containers, IO, datasources, operations, transforms, models, losses, metrics, training, prediction, evaluation, analysis, config/serialization integration, workflow/artifact runtime, registries, root/data convenience exports, optional dependencies, and any public behavior not listed in the five approved phases
