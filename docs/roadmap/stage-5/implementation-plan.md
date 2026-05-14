# Roadmap Stage 5 Implementation Plan

Status: approved; ready for Phase 1 execution planning
Roadmap version: `v5`
Planning document: `docs/roadmap/stage-5/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: ready for Phase 1 execution planning
Blockers: none identified by implementation-plan quality review

## Summary

- Goal: implement the Stage 5 datasource discovery, validation, filtering, grouping, split assignment, index construction, durable manifest, and source-aware composite-index foundation around lazy logical fields.
- Source functionality-agreement gate: passed; FQ-1 through FQ-8 are dependency ordered, repo-resolved, and accepted.
- Approved behavior: FR-1 through FR-8 are locked in `planning.md`; Stage 5 wraps Stage 3/4 descriptors and lazy sample construction without mutating descriptor semantics.
- Source behavior confirmation: passed; scan/validation, view/filter, candidate/group/split, index, manifest, composite, diagnostics, and synthetic proof behavior are locked.
- Key design constraints: DD-1 through DD-11 are binding; DQ-1 through DQ-8 are locked; DD-10 is auto-approved only with private-helper guardrails and public-behavior validation.
- Source design-agreement gate: passed; latest DQ-8 lock is one public source-aware `CompositeDataSourceIndex` with ordered flat access over child indexes, source/child identity in `DataSourceIndexEntry` sidecars and manifests, no `IndexItem.metadata` mutation, no public `ConcatDataSourceIndex`, and private helper guardrails.
- Source future-roadmap/reuse safety review: approved; later operations/export/cache/loaders/real datasources remain additive and must not be pulled into Stage 5.
- Examples covered: EX-1 through EX-6 map the synthetic scan-to-sample path, validation report/IO policy, non-mutating filter plus group-disjoint split, manifest round trip, source-aware composite provenance, and public/private boundary checks.
- Source phase shaping: passed; this plan preserves the accepted eight-phase shape.
- Source plan quality gate: passed 2026-05-14; no unresolved queue, blocked decision, stale specialist evidence, or missing adversarial review remains.
- Out of scope: operations, `SampleOp`/`BatchOp`, export/save, derived datasource writing, Torch `Dataset`/DataLoader/cache, training/evaluation/analysis, real datasource-heavy SDK integrations, workflow/runtime orchestration, broad registries, public fake datasource APIs, root exports, parent-package re-export promotion, public `ConcatDataSourceIndex`, seconds/spatial/alignment window semantics, and descriptor or `IndexItem` mutation.

## Implementation Workflow State

- Implementation-plan quality gate: passed 2026-05-14
- Review pass: passed; no findings
- Refinement pass: not needed
- Confirmation review: not required by reviewer
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `public-boundary-errors-fixtures` | pending | `agent/stage-5-p1-public-boundary-errors-fixtures` | pending | `src/rphys/datasources/*` module homes, exercised error scaffolding, private `tests/support` fixture scaffold, package import tests | Establish Stage 5 module boundaries without broad behavior or placeholder API. | `make test-package`; targeted error/package checks; `git diff --check` | EX-6 |
| 2 | `adapters-validation` | pending | `agent/stage-5-p2-adapters-validation` | pending | `rphys.datasources.adapters`, `rphys.datasources.validation`, synthetic scan/validation tests | Implement datasource specs, structural adapters, scan results, validation reports, and explicit IO policy. | `make test-unit`; `make test-contract`; `make test-package` | EX-1, EX-2 |
| 3 | `views-filters-candidates` | pending | `agent/stage-5-p3-views-filters-candidates` | pending | `rphys.datasources.filters`, index-owned candidate construction/selection surface in `rphys.datasources.indexes` | Implement non-mutating pre-index selection and candidate filtering before group/split. | `make test-unit`; `make test-contract` | EX-1, EX-3 |
| 4 | `groups-splits` | pending | `agent/stage-5-p4-groups-splits` | pending | `rphys.datasources.splits` and group/split provenance handoff to index finalization | Implement candidate-level multiple groups, explicit split-group keys, and leakage-safe split assignment. | `make test-unit`; `make test-contract` | EX-3 |
| 5 | `datasource-index-entries` | pending | `agent/stage-5-p5-datasource-index-entries` | pending | `rphys.datasources.indexes` index plans/builders/results, sidecar entries, field-native windows, `SampleBuilder` bridge | Finalize selected/split candidates into ordered lazy `DataSourceIndex` objects. | `make test-unit`; `make test-contract`; `make test-integration` | EX-1 |
| 6 | `index-manifest-codec` | pending | `agent/stage-5-p6-index-manifest-codec` | pending | `rphys.datasources.indexes` manifest/codec/fingerprint/checksum behavior | Persist and reload datasource indexes with schema `rphys.datasource_index.v1`. | `make test-unit`; `make test-contract`; `git diff --check` | EX-4 |
| 7 | `composite-index` | pending | `agent/stage-5-p7-composite-index` | pending | `CompositeDataSourceIndex`, source-aware sidecar entries, composite manifest behavior | Implement the only public Stage 5 combined-index type. | `make test-unit`; `make test-contract`; `make test-package` | EX-5 |
| 8 | `docs-integration-hardening` | pending | `agent/stage-5-p8-docs-integration-hardening` | pending | Public docstrings/docs, synthetic vertical slice, integration hardening, release checks | Tie together EX-1 through EX-6 and verify public, scientific, durable-artifact, and workflow boundaries. | `make test-unit`; `make test-contract`; `make test-integration`; `make test-package`; `git diff --check`; consider `make validate-pr` | EX-1 through EX-6 |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Functionality, behavior confirmation, design agreement, validation and phase shaping, plan quality, future-roadmap/reuse safety, and auto-approved decision evidence are resolved. | `planning.md` Stage Gates, Plan Quality Gate, DQ-1 through DQ-8, DD-1 through DD-11 | No action before implementation-plan review. Reopen only the affected queue if implementation would require changing locked behavior. | resolved |

## Phase 1: Public Boundary, Errors, And Private Synthetic Fixture Scaffold

Status: pending
Slug: `public-boundary-errors-fixtures`
Branch: `agent/stage-5-p1-public-boundary-errors-fixtures`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p1-public-boundary-errors-fixtures`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: create the Stage 5 module homes and diagnostic/test-support scaffold without inventing unimplemented behavior.
- Files/modules owned: likely `src/rphys/datasources/adapters.py`, `validation.py`, `filters.py`, `splits.py`, `indexes.py`; `src/rphys/errors.py` only for exercised errors; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; private `tests/support/synthetic_datasources.py` only as needed.
- Behavior implemented: importable empty-or-minimal modules only where names are backed by behavior in this phase, lightweight imports, concrete error inheritance/context where exercised, private synthetic fixture location.
- Decisions applied: FR-8; DD-1, DD-10, DD-11; DQ-1, DQ-8; EX-6.
- Future-roadmap/reuse constraints: no root `rphys` exports, no new broad `rphys.datasources` re-exports, no `rphys.datasets`, no public fake datasource package, no public helper utilities.
- Examples or demos covered: EX-6 public/private boundary negative checks.
- Out of scope: functional adapters, validation, filters, splits, index builders, manifests, composite indexes, public synthetic adapter, and placeholder public names.
- Dependencies: existing Stage 3/4 descriptors and package import tests.

### Tasks

- Add focused Stage 5 submodule files only where required by implemented behavior and tests.
- Preserve current `rphys.datasources` descriptor re-exports and root `rphys` behavior.
- Add or adjust package import-boundary tests for submodule-first policy and no public synthetic/concat/helper exports.
- Add exercised error classes only when paired with tests that raise them through public behavior.
- Add private synthetic fixture scaffolding under `tests/support` only to support later phases; do not expose it through package exports.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify import boundaries, lightweight imports, and package export policy. | yes |
| Targeted package/error tests | Confirm no root exports, no broad parent re-exports, no `rphys.datasets`, no public fake datasource, no placeholder names, and exercised error context. | yes |
| `git diff --check` | Verify whitespace/Markdown hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: Stage 5 submodules import without heavy optional dependencies and no unimplemented public placeholders appear.
- Design-decision evidence: DD-1 and DQ-1 submodule-first policy is enforced by tests.
- Future-roadmap/reuse evidence: root/parent exports remain conservative and promotion stays additive for later stages.
- Example/demo evidence: EX-6 negative import checks pass.
- Documentation evidence: any public module docstring marks provisional boundaries and avoids private helper names.
- Scientific contract evidence: no descriptor semantics, runtime sample behavior, or IO policy is changed in this phase.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one focused planning pass
- Implementation/refinement budget: one implementation pass plus at most one refinement pass
- PR review budget: one boundary/API review
- Blocker-resolution budget: reopen DQ-1 or DQ-8 only if public-surface constraints cannot be satisfied
- Pre-submit blocker gate: no placeholder public APIs
- Merge record: pending

### Risks And Stop Conditions

- Risks: adding public names before behavior exists; broad convenience exports becoming accidental contract.
- Stop conditions: any need for root exports, parent re-export promotion, public fake datasource, public helper module, public `ConcatDataSourceIndex`, or source-code behavior outside boundary scaffolding.
- Assumptions: concrete error names can be chosen locally when they do not alter locked behavior.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 2: Specs, Adapters, Scan Results, And Validation Reports

Status: pending
Slug: `adapters-validation`
Branch: `agent/stage-5-p2-adapters-validation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p2-adapters-validation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement the descriptor-only discovery and validation entrypoint for datasource scans.
- Files/modules owned: `src/rphys/datasources/adapters.py`; `src/rphys/datasources/validation.py`; exercised errors in `src/rphys/errors.py`; `tests/unit/rphys/datasources/test_adapters.py`; `tests/unit/rphys/datasources/test_validation.py`; likely contract tests and private `tests/support/synthetic_datasources.py`.
- Behavior implemented: `DataSourceSpec`, structural/importable `DataSourceAdapter.scan(spec)`, `DataSourceScanResult`, `ValidationIssue`, `DataSourceValidationReport`, `ValidationIOPolicy` with `no_io`, `probe_only`, and `explicit_validation_io`, synthetic scan/validation evidence, warnings/rejections, invalid input failures.
- Decisions applied: FR-1, FR-2, FR-8; DD-2, DD-3, DD-11; DQ-2, DQ-3; EX-1, EX-2.
- Future-roadmap/reuse constraints: adapters are explicit importable objects, not registry-discovered; scan results do not depend on or contain `DataSourceView`; no real dataset SDKs or hidden full payload decode.
- Examples or demos covered: EX-1 scan source evidence and EX-2 validation report/IO policy.
- Out of scope: filters/views, candidate construction, group/split, index finalization, manifests, alias registries, symbolic plugin discovery.
- Dependencies: Phase 1.

### Tasks

- Define primitive/descriptive scan and validation records around existing `DataSourceRef`, `RecordRef`, `FieldRef`, and schema/resource descriptors.
- Implement structural adapter protocol behavior and synthetic adapter fixture behavior without mandatory inheritance.
- Validate missing fields/resources/metadata/schema and rejected IDs/counts through structured report records.
- Enforce explicit IO policy and reject hidden full-load fallback attempts through public behavior.
- Keep validation issue codes provisional diagnostic strings, not stable enum taxonomy.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run adapter and validation unit tests. | yes |
| `make test-contract` | Verify public scan/validation behavior and structural adapter contract. | yes |
| `make test-package` | Confirm imports remain lightweight and submodule-first. | yes |
| Targeted tests for scan/view separation | Ensure scan result does not import or contain `DataSourceView`. | yes |

### Acceptance Evidence

- Behavior evidence: synthetic scan emits descriptor refs, scan metadata, source provenance, validation evidence, warnings, and rejections without payload loading.
- Design-decision evidence: DD-2 scan/view separation and DD-3 minimal structured validation reports are tested.
- Future-roadmap/reuse evidence: real adapters can later reuse explicit spec/adapter/report contracts without registry or SDK coupling.
- Example/demo evidence: EX-1 and EX-2 are represented in focused tests.
- Documentation evidence: docstrings explain descriptor-only scan behavior, primitive report context, and provisional issue codes.
- Scientific contract evidence: validation reports preserve missing/invalid datasource, record, field, resource, schema, and metadata evidence with explicit failure behavior.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass if scan/report shape drifts
- PR review budget: one adapter/validation API review
- Blocker-resolution budget: reopen DQ-2 or DQ-3 only if scan/view separation or report shape cannot hold
- Pre-submit blocker gate: scan result cannot depend on filters/views
- Merge record: pending

### Risks And Stop Conditions

- Risks: overfitting issue taxonomy, mixing scan and view responsibilities, accidentally adding registry semantics.
- Stop conditions: need for real datasource SDK dependencies, hidden payload decode, stable issue-code enum, adapter alias registry, or `DataSourceView` in scan results.
- Assumptions: exact field names in scan/report records are implementation details if they preserve locked basics and primitive/descriptive serialization.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 3: Non-Mutating Views, Filter Chains, And Index-Candidate Selection

Status: pending
Slug: `views-filters-candidates`
Branch: `agent/stage-5-p3-views-filters-candidates`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p3-views-filters-candidates`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement staged non-mutating selection before group/split and final index entry emission.
- Files/modules owned: `src/rphys/datasources/filters.py`; candidate-related portions of `src/rphys/datasources/indexes.py`; `tests/unit/rphys/datasources/test_filters.py`; `tests/unit/rphys/datasources/test_index_candidates.py`; relevant contract tests.
- Behavior implemented: `DataSourceViewPlan`, `DataSourceView`, view builder/result, structural filters and `FilterChain`, `FilterResult`, typed pre-index target records as needed, `IndexCandidate`, candidate construction/result/view, candidate filters.
- Decisions applied: FR-3, FR-5, FR-8; DD-4, DD-7, DD-10; DQ-4, DQ-6 preconditions; EX-1, EX-3.
- Future-roadmap/reuse constraints: selection stays descriptor/candidate based; no runtime `SampleOp`, payload transforms, hidden IO, split-conditioned filtering, durable identity before finalization, or broad candidate protocol.
- Examples or demos covered: EX-1 staged synthetic selection and EX-3 pre-index/candidate filter ordering.
- Out of scope: group/split assignment, final `DataSourceIndex` sidecar identity, manifest codec, composite index, seconds/spatial/alignment semantics.
- Dependencies: Phases 1-2.

### Tasks

- Implement non-mutating view/result records from scan/view inputs.
- Implement structural filters with explicit IO policy and deterministic reporting.
- Implement filter chains over typed target units without one untyped universal target.
- Implement index-owned `IndexCandidate` records with prospective locator-to-`FieldView` mappings, source/window provenance, primitive metadata, and validation/probe evidence.
- Test the order: scan/validation -> pre-index selection -> candidate construction -> candidate filtering.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run filter and candidate unit tests. | yes |
| `make test-contract` | Verify non-mutation, structural filter contract, and candidate-order behavior. | yes |
| Targeted mutation tests | Assert original refs, field views, index candidates, and `IndexItem.metadata` are not mutated. | yes |

### Acceptance Evidence

- Behavior evidence: filters produce new views/results with included/excluded counts and reasons while originals remain unchanged.
- Design-decision evidence: DD-4 typed selection and DQ-4 ordering are covered by explicit tests.
- Future-roadmap/reuse evidence: Stage 6/7 loaded-data routing remains separate and candidate extension stays additive for later window/alignment work.
- Example/demo evidence: EX-1 and EX-3 selection order is demonstrated.
- Documentation evidence: docstrings explain typed target ownership, candidate provisionality, and IO policy.
- Scientific contract evidence: candidate records represent prospective loadable units without split assignment, payloads, runtime samples, transforms, or durable entry identity.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass if candidate shape grows too broad
- PR review budget: one selection/candidate review
- Blocker-resolution budget: reopen DQ-4 or DQ-6 only if the stage order or field-native candidate assumptions fail
- Pre-submit blocker gate: `IndexCandidate` must not carry split assignment, payloads, runtime samples, or final entry identity
- Merge record: pending

### Risks And Stop Conditions

- Risks: candidate record becomes too broad, filters drift into runtime operations, private helpers become tested as public API.
- Stop conditions: need for split-conditioned filters, payload materialization, runtime `SampleOp` coupling, durable identity before finalization, or seconds/alignment semantics.
- Assumptions: pre-index target records can remain layer-owned implementation details unless exposed through public filter behavior.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Candidate-Level Groups And Split Assignment

Status: pending
Slug: `groups-splits`
Branch: `agent/stage-5-p4-groups-splits`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p4-groups-splits`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement leakage-safe group and split behavior over selected index candidates.
- Files/modules owned: `src/rphys/datasources/splits.py`; group/split provenance handoff types consumed by `src/rphys/datasources/indexes.py`; `tests/unit/rphys/datasources/test_splits.py`; relevant contract tests.
- Behavior implemented: `GroupPlan`, `GroupBuilder`, `GroupResult`, `SplitPlan`, `SplitBuilder`, `SplitResult`, multiple named groups, explicit split-group keys, required-group missing/ambiguous policy, explicit assignments or explicit ratios plus seed if implemented, leakage detection, counts/warnings/rejections, non-split analysis-group preservation.
- Decisions applied: FR-4, FR-8; DD-5; DQ-5; EX-3.
- Future-roadmap/reuse constraints: group/split plans are library objects, not trainer/evaluator modes or workflow stages; later training/evaluation consumes split/group metadata rather than redefining leakage.
- Examples or demos covered: EX-3 group-disjoint split and analysis-group preservation.
- Out of scope: project-specific split recipes, implicit ratios, split-conditioned candidate filtering, final index persistence, trainer/evaluator loop semantics.
- Dependencies: Phases 1-3.

### Tasks

- Implement group extraction from selected-candidate metadata/provenance.
- Implement explicit split-group selection and group-disjoint split assignment.
- Fail loudly by default for missing/ambiguous required groups and leakage.
- Preserve non-split groups for downstream analysis metadata.
- Record counts, warnings, rejections, split/group provenance, and deterministic seeded assignment evidence where ratio assignment exists.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run group/split unit tests. | yes |
| `make test-contract` | Verify scientific split contract and failure behavior. | yes |
| Determinism tests if ratios are implemented | Confirm explicit ratios plus seed are reproducible and no implicit ratios exist. | yes, if ratio assignment exists |

### Acceptance Evidence

- Behavior evidence: selected candidates receive multiple groups and explicit split assignments with counts matching loadable candidate population.
- Design-decision evidence: DD-5 fail-loud group-disjoint policy is tested.
- Future-roadmap/reuse evidence: split and non-split groups remain recoverable for later loaders, loss/metric analysis, and evaluation.
- Example/demo evidence: EX-3 leakage failure, missing group policy, and analysis group preservation are demonstrated.
- Documentation evidence: docstrings explain group vs split, selected-candidate scope, required/optional groups, and override policy if implemented.
- Scientific contract evidence: subject/source leakage is detected over selected candidates by explicit split-group key(s), not inferred from split names or trainer modes.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass for scientific-contract edge cases
- PR review budget: one scientific split/leakage review
- Blocker-resolution budget: reopen DQ-5 only if candidate-level group/split cannot express required provenance
- Pre-submit blocker gate: no implicit ratios and no split-conditioned filtering
- Merge record: pending

### Risks And Stop Conditions

- Risks: strict defaults may feel verbose for prediction-like flows; analysis groups may be confused with split-disjoint keys.
- Stop conditions: need for trainer/evaluator mode semantics, project-specific recipes, implicit ratios, random candidate splits under group-disjoint mode, or post-split filtering.
- Assumptions: exact policy names are implementation details if the fail-loud defaults and explicit override semantics remain intact.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: DataSourceIndex Construction, Sidecar Entries, And SampleBuilder Bridge

Status: pending
Slug: `datasource-index-entries`
Branch: `agent/stage-5-p5-datasource-index-entries`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p5-datasource-index-entries`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: finalize selected/split candidates into ordered lazy datasource indexes compatible with Stage 4 `SampleBuilder`.
- Files/modules owned: `src/rphys/datasources/indexes.py`; `tests/unit/rphys/datasources/test_indexes.py`; `tests/contracts/test_datasource_index_contract.py`; likely `tests/integration/test_synthetic_datasource_to_sample_builder.py`.
- Behavior implemented: `IndexPlan`, `IndexBuilder`, `IndexResult`, `IndexBuildReport`, `DataSourceIndex`, sidecar `DataSourceIndexEntry` or equivalent, `entry_at(position)` and/or entries view, ordered length/item access/iteration, field-native whole-record and `TemporalIndexSlice` windows, missing-field failures, split/group/window/source provenance, `SampleBuilder` bridge.
- Decisions applied: FR-5, FR-8; DD-4, DD-5, DD-6, DD-7; DQ-4, DQ-5, DQ-6; EX-1.
- Future-roadmap/reuse constraints: sidecar entries become later cache/export/loader identity inputs while `IndexItem` remains pure for sample building.
- Examples or demos covered: EX-1 synthetic scan-to-lazy-sample path.
- Out of scope: manifest codec, composite index, seconds/spatial/alignment inference, payload loads, transforms, cache/export/Torch behavior, identity in `IndexItem.metadata`.
- Dependencies: Phases 1-4.

### Tasks

- Implement index plan/build/finalize behavior over selected and split candidates.
- Emit ordered `IndexItem`s containing `FieldView`s only.
- Store durable identity, fingerprint, position, group/split/window/source provenance in sidecar entries.
- Expose item-yielding `__getitem__` and iteration plus explicit entry access.
- Test existing `SampleBuilder` compatibility with returned `IndexItem`s.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run index builder and access unit tests. | yes |
| `make test-contract` | Verify `DataSourceIndex`, entry sidecar, field-native window, and purity contracts. | yes |
| `make test-integration` | Verify synthetic index item works with existing `SampleBuilder`. | yes |

### Acceptance Evidence

- Behavior evidence: `len`, `__getitem__`, iteration, and entry access work with stable positions and recoverable identity/provenance.
- Design-decision evidence: DD-6 sidecar identity and DD-7 field-native windows are enforced.
- Future-roadmap/reuse evidence: later cache/export/loaders can inspect entry identity without changing `IndexItem`.
- Example/demo evidence: EX-1 reaches lazy sample construction through existing `SampleBuilder`.
- Documentation evidence: docstrings distinguish item access from entry/provenance access and state field-native window limits.
- Scientific contract evidence: index items stay payload-free, transform-free, role-qualified, and do not claim seconds/alignment/spatial semantics.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass for item-vs-entry ergonomics
- PR review budget: one index contract review
- Blocker-resolution budget: reopen DQ-6 only if identity cannot remain outside `IndexItem`
- Pre-submit blocker gate: no `IndexItem.metadata` mutation for identity/source/composite data
- Merge record: pending

### Risks And Stop Conditions

- Risks: two access modes may confuse users; field-native windows may be pressured into seconds/alignment behavior.
- Stop conditions: need to add `item_id`/fingerprint to `IndexItem`, wrapper-returning item access as default, hidden caches, payload loading, or non-field-native window semantics.
- Assumptions: exact sidecar field names can be chosen during implementation if they preserve locked identity/provenance basics.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 6: Manifest Codec, Durable Schema, Fingerprints, And Checksums

Status: pending
Slug: `index-manifest-codec`
Branch: `agent/stage-5-p6-index-manifest-codec`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p6-index-manifest-codec`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: persist and reload datasource indexes through the locked schema-versioned manifest and fingerprint policy.
- Files/modules owned: manifest/codec portions of `src/rphys/datasources/indexes.py` or a private implementation submodule if needed; `tests/unit/rphys/datasources/test_index_manifests.py`; `tests/contracts/test_datasource_index_manifest_contract.py`; optional tiny golden manifest fixtures.
- Behavior implemented: `DataSourceIndexManifest`, `DataSourceIndexCodec`, JSON/JSONL-like read/write, schema version `rphys.datasource_index.v1`, exact descriptor/resource preservation, deterministic canonical JSON with sorted keys and explicit separators, SHA-256 stable content fingerprints, optional full-manifest checksum, volatile report exclusion, unsupported version/fingerprint/ambiguity rejection.
- Decisions applied: FR-6, FR-8; DD-6, DD-8; DQ-6, DQ-7; EX-4.
- Future-roadmap/reuse constraints: cache/export/loader stages can use stable fingerprints later, but Stage 5 does not implement cache manifests, materialized-data manifests, export-derived manifests, path normalization, or migration framework.
- Examples or demos covered: EX-4 manifest round trip with stable content fingerprints.
- Out of scope: pickle, backend-specific canonicalization, path normalization, cache invalidation policy beyond stable datasource-index content fingerprints, manifest migrations beyond rejecting unsupported versions.
- Dependencies: Phase 5.

### Tasks

- Define the manifest envelope and index codec behavior around exact descriptor dicts and sidecar entry identity.
- Implement deterministic content fingerprint generation over explicit stable subsets.
- Keep full-manifest checksum separate from content fingerprints and exclude volatile report fields unless explicitly declared as invalidation inputs.
- Implement rejection paths for unsupported schema versions, ambiguous manifests, and fingerprint mismatches.
- Consider tiny golden fixtures after schema shape is implemented and reviewable.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run manifest/codec/fingerprint unit tests. | yes |
| `make test-contract` | Verify durable artifact contract and rejection behavior. | yes |
| `git diff --check` | Verify manifest fixtures/docs do not introduce whitespace problems. | yes |
| Golden fixture checks | Guard schema regressions if tiny fixtures are added. | optional unless fixtures are added |

### Acceptance Evidence

- Behavior evidence: manifest round trip reloads equivalent lazy entries and preserves exact descriptor/resource fields.
- Design-decision evidence: DD-8 schema/fingerprint policy is enforced, including no pickle and volatile-report exclusion.
- Future-roadmap/reuse evidence: cache/export/loaders can later consume stable fingerprints without inheriting full-manifest checksum semantics.
- Example/demo evidence: EX-4 covers round trip, unsupported version rejection, fingerprint mismatch, and no-pickle behavior.
- Documentation evidence: docstrings state schema token, stable subset policy, checksum distinction, exact-resource preservation, and path-normalization deferral.
- Scientific contract evidence: durable provenance includes split/group/window/source identity without modifying descriptor or `IndexItem` schemas.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass for artifact-shape review
- PR review budget: one persistence/schema review
- Blocker-resolution budget: reopen DQ-7 only if exact-resource or split-fingerprint policy cannot be implemented
- Pre-submit blocker gate: no pickle and no path normalization
- Merge record: pending

### Risks And Stop Conditions

- Risks: durable schema mistakes are costly; fingerprint subset ambiguity could weaken later cache/export reuse.
- Stop conditions: need for descriptor schema-version fields, path normalization as hidden behavior, single all-fields fingerprint over volatile reports, pickle persistence, cache/export manifest behavior, or a migration framework.
- Assumptions: optional golden fixtures are useful only once the schema is stable enough to review.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 7: Source-Aware CompositeDataSourceIndex

Status: pending
Slug: `composite-index`
Branch: `agent/stage-5-p7-composite-index`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p7-composite-index`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: implement the single public Stage 5 source-aware combined-index type.
- Files/modules owned: composite portions of `src/rphys/datasources/indexes.py`; `tests/unit/rphys/datasources/test_composite_indexes.py`; relevant manifest contract tests and package boundary tests.
- Behavior implemented: `CompositeDataSourceIndex`, ordered flat access over child `DataSourceIndex` objects, source-aware sidecar entries, source key, child index ID/fingerprint, child local position, global position, optional child metadata, composite fingerprint/order behavior, composite manifest round trip.
- Decisions applied: FR-7, FR-8; DD-6, DD-8, DD-9, DD-10; DQ-6, DQ-7, DQ-8; EX-5.
- Future-roadmap/reuse constraints: later samplers/cache/loaders can inspect child/source identity but must own weighted sampling, cache orchestration, batch planning, and nested/multi-member samples themselves.
- Examples or demos covered: EX-5 source-aware composite provenance.
- Out of scope: public `ConcatDataSourceIndex`, weighted sampling, nested multi-member `IndexItem`s, cache orchestration, batch planning, source identity in `IndexItem.metadata`.
- Dependencies: Phases 5-6.

### Tasks

- Implement ordered flat item access and iteration over child indexes.
- Preserve source/child/local/global provenance in sidecar entries and manifests.
- Make child order affect composite fingerprint.
- Ensure `IndexItem` objects are returned unchanged and metadata is not stamped with source identity.
- Assert no public concat export exists.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Run composite index unit tests. | yes |
| `make test-contract` | Verify composite, entry, manifest, and fingerprint behavior. | yes |
| `make test-package` | Confirm no public `ConcatDataSourceIndex` export and private helpers stay private. | yes |

### Acceptance Evidence

- Behavior evidence: composite length/item access/iteration are ordered and flat; entry access preserves source/child/local/global identity.
- Design-decision evidence: latest DQ-8 lock is enforced by tests.
- Future-roadmap/reuse evidence: composite exposes provenance for later loaders/cache without owning sampler/cache/batch behavior.
- Example/demo evidence: EX-5 proves child order, manifest round trip, no provenance flattening, and no `IndexItem.metadata` mutation.
- Documentation evidence: docstrings state composite-only Stage 5 behavior, ordered flat access, and concat deferral.
- Scientific contract evidence: multi-source composition remains traceable and cannot silently flatten child provenance.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one pass
- Implementation/refinement budget: one implementation pass plus one refinement pass for DQ-8 conformance
- PR review budget: one composite/provenance review
- Blocker-resolution budget: reopen DQ-8 only if composite-only ordered flat semantics cannot satisfy source provenance
- Pre-submit blocker gate: no public concat and no source identity in `IndexItem.metadata`
- Merge record: pending

### Risks And Stop Conditions

- Risks: users may expect a concat name from roadmap prose; composite may attract sampler/cache features.
- Stop conditions: need for separate public concat API, weighted sampling, batch planning, cache behavior, nested samples, anonymous list-copy composition, or child provenance in `IndexItem.metadata`.
- Assumptions: a future concat alias/class remains additive only if later evidence justifies the public API surface.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 8: Documentation, Examples, Integration Hardening, And Release Checks

Status: pending
Slug: `docs-integration-hardening`
Branch: `agent/stage-5-p8-docs-integration-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p8-docs-integration-hardening`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: verify Stage 5 end-to-end behavior and align docs/docstrings with implemented object names and locked scientific contracts.
- Files/modules owned: public docstrings in `src/rphys/datasources/**`; focused docs or glossary wording only if needed; integration tests such as `tests/integration/test_synthetic_datasource_flow.py`; package/contract hardening tests.
- Behavior implemented: no new feature behavior beyond Phases 1-7; synthetic integration path for scan -> validation -> view/filter -> candidate/filter -> group/split -> index -> manifest -> composite -> `SampleBuilder`; docs for public/provisional/private boundaries and deferrals.
- Decisions applied: FR-1 through FR-8; DD-1 through DD-11; DQ-1 through DQ-8; EX-1 through EX-6.
- Future-roadmap/reuse constraints: docs must explicitly defer operations/export/cache/training/workflow ownership, real datasource-heavy SDKs, seconds/spatial/alignment windows, public fake datasets, public concat, and parent/root export promotion.
- Examples or demos covered: EX-1 through EX-6.
- Out of scope: new public features, workflow/runtime docs beyond deferrals, implementation-plan changes unless requested by the implementation-plan review gate.
- Dependencies: Phases 1-7.

### Tasks

- Add or revise docstrings for public Stage 5 objects with shapes, provenance, IO policy, field-native slices, grouping/split semantics, manifest/fingerprint policy, and composite-only behavior.
- Add integration coverage for the synthetic vertical slice and manifest/composite proof.
- Verify package, unit, contract, and integration suites relevant to Stage 5.
- Check that docs/tests do not import private helpers or publicize private synthetic fixtures.
- Record residual risks and revisit triggers in phase handoff/PR body.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify datasource unit coverage after all phases. | yes |
| `make test-contract` | Verify public contracts and durable artifact behavior. | yes |
| `make test-integration` | Verify synthetic vertical slice and `SampleBuilder` bridge. | yes |
| `make test-package` | Verify package import and public/private boundaries. | yes |
| `git diff --check` | Verify whitespace/Markdown hygiene. | yes |
| `make validate-pr` | Broader pre-merge confidence for shared public behavior. | recommended before final Stage 5 merge |

### Acceptance Evidence

- Behavior evidence: synthetic path covers scan, validation, filtering, candidates, group/split, index, manifest, composite, and lazy sample construction.
- Design-decision evidence: all DD/DQ obligations are either covered by tests or explicit docs review.
- Future-roadmap/reuse evidence: deferrals and revisit triggers are documented without creating downstream runtime ownership.
- Example/demo evidence: EX-1 through EX-6 have matching tests or docs.
- Documentation evidence: docs/docstrings align with final implemented names and stability labels.
- Scientific contract evidence: provenance, leakage, IO policy, window semantics, and manifest fingerprint/checksum behavior are inspectable and reproducible.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: one expanded planning pass
- Implementation/refinement budget: one implementation pass plus refinement as required by integration failures
- PR review budget: one full Stage 5 integration/docs review
- Blocker-resolution budget: reopen only the affected FQ/DQ row if docs/integration reveal behavior drift from locked decisions
- Pre-submit blocker gate: EX-1 through EX-6 traceability must remain complete
- Merge record: pending

### Risks And Stop Conditions

- Risks: docs lag final object names; integration tests expose phase drift or unassigned validation obligations.
- Stop conditions: required docs imply new behavior not implemented in earlier phases, or validation requires changing locked FR/DQ/DD behavior.
- Assumptions: `docs/GLOSSARY.md` changes are optional and should happen only if public wording would otherwise be ambiguous.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: `make test-unit`, `make test-contract`, `make test-integration`, `make test-package`, and `git diff --check` across the completed phase set; run `make validate-pr` before final Stage 5 merge or when shared public behavior across phases is integrated.
- Docs/template checks: verify module docstrings and any docs/glossary edits state descriptor purity, IO policy, field-native window limits, group/split leakage semantics, manifest schema/fingerprint/checksum policy, source-aware composite-only behavior, private fixture/helper boundaries, and explicit deferrals.
- Scientific/workflow contract checks: no hidden full-load fallback, no descriptor mutation, no `IndexItem.metadata` identity/source mutation, no split-conditioned filtering, no implicit split ratios, no seconds/spatial/alignment claims, no operations/export/cache/training/workflow ownership.
- Example/demo checks: EX-1 through EX-6 must remain traceable to tests or docs by Phase 8.
- Manual review focus: public import surface, scan/view separation, validation report primitive shape, candidate stage ordering, leakage failure behavior, item-vs-entry access, manifest durable schema, composite provenance, private helper/test-support leakage, and future-roadmap deferrals.

## Traceability Matrix

| Planning item | Primary phases | Required evidence |
| --- | --- | --- |
| FR-1 datasource discovery specs and adapters | 2, 8 | Synthetic scan contract, descriptor purity, source provenance, no full decode |
| FR-2 validation reports and IO policy | 2, 8 | Structured issues, rejected IDs/counts, no-IO/probe/explicit IO policy, typed failures |
| FR-3 non-mutating views and filters | 3, 8 | View/filter reports, immutability checks, deterministic filter chains, candidate filtering order |
| FR-4 grouping and split assignment with leakage checks | 4, 8 | Multiple groups, explicit split-group keys, missing/ambiguous policy, leakage failure, analysis groups |
| FR-5 index plans/builders/results and `DataSourceIndex` | 3, 5, 8 | Candidate construction, field-native windows, item access, sidecar entries, `SampleBuilder` integration |
| FR-6 durable index manifest and codec round trip | 6, 8 | `rphys.datasource_index.v1`, exact resource preservation, canonical JSON/SHA-256, rejection paths |
| FR-7 source-aware composite datasource indexes | 7, 8 | Ordered flat composite access, child/source/local/global provenance, child-order fingerprint effects |
| FR-8 boundary, diagnostics, public contract, synthetic proof | 1 through 8 | Package boundaries, exercised errors, no placeholders, private fixtures/helpers, synthetic vertical slice |
| DD-1 / DQ-1 public/import surface | 1, 8 | Submodule-first imports, no root/parent broad re-exports, no `rphys.datasets` |
| DD-2 / DQ-2 adapter scan result shape | 2 | `DataSourceScanResult` independent from `DataSourceView` |
| DD-3 / DQ-3 validation report schema | 2 | Minimal structured issues with provisional codes |
| DD-4 / DQ-4 views/filter/candidate pipeline | 3 | Pre-index filters before candidate construction; candidate filters before group/split |
| DD-5 / DQ-5 group/split policy | 4 | Candidate-level groups and explicit group-disjoint split policy |
| DD-6 / DQ-6 index-entry identity | 5, 7 | Sidecar entries; item-yielding `DataSourceIndex` access; no `IndexItem.metadata` identity |
| DD-7 / DQ-6 window scope | 3, 5 | Whole-record and explicit field-native `TemporalIndexSlice` only |
| DD-8 / DQ-7 manifest/fingerprint policy | 6, 7 | Exact descriptor/resource preservation, content fingerprints separate from checksums, no pickle |
| DD-9 / DQ-8 composite semantics | 7 | One public `CompositeDataSourceIndex`; no public concat; source-aware entry/manifest provenance |
| DD-10 / DQ-8 private helper boundaries | 1, 3, 6, 7, 8 | Helpers module-local, not exported, not documented, not asserted directly by tests |
| DD-11 / DQ-1 synthetic proof placement | 1, 2, 8 | Private `tests/support` fixture only; no public synthetic datasource API |
| EX-1 synthetic scan to lazy sample | 2, 3, 4, 5, 8 | Integration path through existing `SampleBuilder` |
| EX-2 validation report and IO policy | 2 | Validation report and IO-policy unit/contract coverage |
| EX-3 non-mutating filter plus group-disjoint split | 3, 4 | Filter/candidate order and leakage-safe split tests |
| EX-4 manifest round trip | 6 | Manifest reload equivalence and fingerprint/checksum tests |
| EX-5 source-aware composite provenance | 7 | Child/source/local/global provenance and no concat export tests |
| EX-6 public/private boundary | 1, 7, 8 | Package import tests and private-helper/fixture privacy checks |

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No blocking, major, or minor findings. | none | No refinement required; proceed to phase execution planning after maintainer approval. | passed |

Gate result:

- Status: passed 2026-05-14 / implementation-plan quality review.
- Review evidence: `rphys_plan_reviewer` found the plan traceable, phase-bounded, and consistent with the approved Stage 5 planning baseline. The reviewer confirmed no Functionality Agreement or Design Agreement queue needs reopening and no implementation-plan blocker remains.
- Accepted risks: exact object field names beyond locked basics, concrete error names, optional golden fixtures, and exact test filenames remain implementation details for phase plans.
- Revisit triggers: reopen the relevant FQ/DQ row if implementation would require descriptor mutation, hidden IO, root exports, broad parent re-exports, public synthetic fixtures, public `ConcatDataSourceIndex`, non-field-native windows, cache/export/training/workflow ownership, identity inside `IndexItem.metadata`, or source/child identity stamped into `IndexItem.metadata`.

## Final Approval

- Approval status: approved 2026-05-14
- Approved scope: eight-phase Stage 5 implementation plan covering public boundary/errors/fixtures; adapters/validation; views/filters/candidates; groups/splits; `DataSourceIndex` sidecar entries and `SampleBuilder` bridge; manifest codec/fingerprints; source-aware `CompositeDataSourceIndex`; docs/integration hardening.
- Accepted risks: exact object field names beyond locked basics, concrete error names, optional golden fixtures, exact test filenames, and explicit-ratio split assignment only if implemented remain phase-level implementation details.
- Deferred items: real datasource SDK integrations, adapter alias/registry policy, parent/root export promotion, public testing-helper package, public concat alias/class, seconds/spatial/alignment windows, payload-quality validation, cache/export/prepared-data manifests, Torch loaders/cache, operations/training/evaluation/workflow runtime, descriptor schema/fingerprint fields, and path normalization/canonical storage policy.
