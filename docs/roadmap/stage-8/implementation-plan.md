# Roadmap Stage 8 Implementation Plan

Status: implemented; all phases merged
Roadmap version: `v8`
Planning document: `docs/roadmap/stage-8/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: all phases merged
Blockers: none for implementation-plan drafting

## Summary

- Goal: Implement Stage 8 save/export operations and descriptor-only derived datasource assembly as a small, sequential set of reviewable phases. Stage 8 exports declared runtime fields through existing codec save contracts, returns typed in-memory export evidence, preserves link/copy lineage, and assembles derived datasource descriptors without rescanning output directories.
- Source functionality-agreement gate: `docs/roadmap/stage-8/planning.md` Stage Gates and Stage Readbacks record functionality agreement as passed on 2026-05-15; FQ-0 through FQ-8 are locked or repo-resolved.
- Approved behavior: explicit export request/layout/policy records; side-effect-free `CodecSelectionOperation`; side-effecting `SaveOperation`; typed `FieldExportResult`, `RecordExportResult`, `ExportResult`, and `ExportReport`; descriptor-only `DerivedDataSourceAssembly`/`DerivedDataSourceBuilder`; public link/copy lineage evidence; fail-loud unsupported behavior.
- Source behavior confirmation: `docs/roadmap/stage-8/planning.md` Behavior Confirmation, accepted from resolved FQ-0 through FQ-8.
- Key design constraints: public names use full `Operation`; `rphys.ops.export` owns export specs, policies, layouts, operations, result records, and report records; `rphys.datasources.derived` is descriptor-only and must not own save/export execution; `CodecSelectionOperation` and `SaveOperation` must satisfy the landed Stage 7 `OperationStep` contract and return `OperationResult`.
- Source design-agreement gate: `docs/roadmap/stage-8/planning.md` Design Agreement Queue, Design Decisions, Design Decision Triage, Maintainer Decision Packets, and Stage Gates record DQ-1, DQ-2, DQ-3, DQ-5, DQ-6, and DQ-7 as locked; DQ-4 and DQ-8 are non-blocking recorded recommendations.
- Source functionality-agreement queue: FQ-0 through FQ-8, with FQ-0 locked by maintainer naming clarification and FQ-1 through FQ-8 repo-resolved.
- Source design-agreement queue: DQ-1 through DQ-8, dependency ordered after design implication review, with no unresolved `needs maintainer discussion` item.
- Source future-roadmap/reuse safety review: Stage 8 must leave Stage 9 cache/loading, Stage 13 prediction/evaluation, Stage 14 smoke artifacts, and Stage 15 materialization/cache schemas additive; durable report schemas, durable derived manifest schemas, and public storage adapters are deferred with explicit revisit triggers.
- Examples covered: OperationStep export composition, synthetic datasource/index/sample to derived datasource reload, no-write selection preflight, idempotency conflict/skip/replace matrix, codec save contract preservation, descriptor-only derived datasource assembly, link/copy lineage preservation, and optional prediction-like field pressure.
- Source phase shaping: `docs/roadmap/stage-8/planning.md` Phase Shaping locks five phases: export primitives/layout/policy/result records; OperationStep selection preflight; SaveOperation through codec save and idempotency; link/copy lineage/private local helpers; descriptor-only derived datasource assembly and final synthetic round trip.
- Source plan quality gate: `docs/roadmap/stage-8/planning.md` Plan Quality Gate records status passed with no blocking findings for implementation-plan drafting.
- Out of scope: code implementation in this plan; `docs/roadmap.md`; abbreviated public `*Op` aliases; root `rphys` exports; public report `to_dict`, JSON, or report-file schemas; durable derived datasource manifest wire schemas; `DataSourceIndexManifest` reuse for derived datasources; output rescans; storage adapter protocols; cache/materialization manifests; prediction runners, metrics, analysis reports, training hooks, workflow runtime, raw datasets, and heavy optional imports.

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: completed 2026-05-15 / managing agent
- Refinement pass: not required
- Confirmation review: completed 2026-05-15 / managing agent
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `export-primitives` | merged | `agent/stage-8-p1-export-primitives` | [#55](https://github.com/samcantrill/rphys/pull/55) | `src/rphys/ops/export.py` or package equivalent; `tests/unit/rphys/ops/`; `tests/contracts/`; package import tests | Establish data-only export request, layout, policy, outcome, result, and report records without writing files. | Targeted unit/contract tests for layout, fingerprint, idempotency, result aggregation, public imports; `git diff --check`. | Idempotency matrix; typed in-memory report records. |
| 2 | `selection-preflight` | merged | `agent/stage-8-p2-selection-preflight` | [#56](https://github.com/samcantrill/rphys/pull/56) | `rphys.ops.export`; operation contract tests; selection unit tests | Add no-write `CodecSelectionOperation` and prove landed `OperationStep` compatibility. | Contract/unit tests for `OperationStep`, `OperationPipeline`, no side effects, missing/ambiguous/unsupported inputs. | OperationStep export composition; selection preflight produces no writes. |
| 3 | `save-operation` | merged | `agent/stage-8-p3-save-operation` | [#57](https://github.com/samcantrill/rphys/pull/57) | `rphys.ops.export`; synthetic codec fixtures; save/codec contract tests | Implement `SaveOperation` through existing codec save contracts and explicit idempotency outcomes. | Unit/contract tests for pipeline output forwarding, `SaveContext(target=FieldRef)`, `CodecSaveResult`, conflict/skip/replace/write, typed failures. | Codec save contract preservation; idempotency matrix. |
| 4 | `link-copy-lineage` | merged | `agent/stage-8-p4-link-copy-lineage` | [#58](https://github.com/samcantrill/rphys/pull/58) | Private local helpers under export implementation; lineage/local-link tests; package boundary tests | Add explicit link/copy policy behavior and public ordered source/target `ResourceRef` lineage while keeping helpers private. | Unit tests for linked/copied counts, missing lineage, unsupported/cross-protocol failures, explicit fallback, private helper imports; `make test-package`. | Link/copy lineage preservation. |
| 5 | `derived-datasource-roundtrip` | merged | `agent/stage-8-p5-derived-datasource-roundtrip` | [#59](https://github.com/samcantrill/rphys/pull/59) | `src/rphys/datasources/derived.py`; derived datasource unit tests; Stage 8 integration test; docs/package tests | Assemble successful export results into descriptor-only derived datasources and prove the synthetic export-to-reload vertical slice. | Unit/integration tests for no-rescan assembly, no source mutation, no index-manifest reuse, derived index/load; package/docs checks; final broad suite as scope warrants. | Synthetic datasource/index/sample to exported derived datasource reload; optional prediction-like field dry run. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None for implementation-plan drafting. Validation and phase shaping passed, plan quality passed, required specialist evidence is present, no design decision is blocked, no `needs maintainer discussion` decision is unresolved, and auto-approved DD-10 has traceability plus adversarial review evidence. | `docs/roadmap/stage-8/planning.md` Stage Gates, Design Decision Triage, Future Roadmap And Reuse Safety Review, Validation Strategy, Phase Shaping, Plan Quality Gate | No action before drafting phases. Carry phase stop conditions for scope expansion attempts. | cleared |

## Phase 1: Export Primitives, Layout, Policy, And Result Records

Status: merged
Slug: `export-primitives`
Branch: `agent/stage-8-p1-export-primitives`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p1-export-primitives`
PR: [#55](https://github.com/samcantrill/rphys/pull/55)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: Establish the public, data-only export surface with deterministic target derivation, explicit policy/outcome vocabulary, typed in-memory result/report records, and no file-writing behavior.
- Files/modules owned: `src/rphys/ops/export.py` or an equivalent `rphys.ops.export` package; focused `tests/unit/rphys/ops/test_export_layout.py`, `tests/unit/rphys/ops/test_export_policy.py`, `tests/unit/rphys/ops/test_export_results.py`; possible `tests/contracts/test_export_result_contract.py`; package import/export tests.
- Behavior implemented: `ExportSpec`, `ExportTarget`, `OutputLayout`, `ExportPolicy`, `IdempotencyPolicy`, outcome vocabulary, stable export-spec fingerprint helper, deterministic target `FieldRef` derivation, typed `FieldExportResult`, `RecordExportResult`, `ExportResult`, and `ExportReport`, plus count aggregation and focused exercised errors.
- Decisions applied: DD-1 public ownership; DD-3 minimal deterministic layout/fingerprint/idempotency; DD-6 typed in-memory records only; DD-9 focused exercised errors; DD-10 private helper placement.
- Future-roadmap/reuse constraints: keep Stage 9/15 cache/materialization identity and Stage 13 report/evaluation schemas out of Phase 1; durable report serialization stays deferred.
- Examples or demos covered: idempotency conflict/skip/replace matrix at the data-model level; typed in-memory export report counts.
- Out of scope: `CodecSelectionOperation`, `SaveOperation`, filesystem writes, link/copy helpers, derived datasource assembly, report `to_dict`/JSON/report-file schemas, durable derived manifest schemas, root exports, and shorthand `*Op` aliases.
- Dependencies: Stage 8 planning gates passed; existing `DataSourceRef`, `RecordRef`, `FieldRef`, `ResourceRef`, and codec metadata policy types.

### Tasks

- Add the Stage 8 export records in the owning export module with code-backed public names and concise docstrings for shape, stability, and non-durable schema boundaries.
- Implement deterministic layout/fingerprint behavior using only approved stable primitive inputs: requested fields, codec/schema requests, metadata-save policy, layout version, and output-shaping policy.
- Exclude timestamps, file existence, Python object identity, codec registry identity/order, target root/resource, and workflow/runtime state from fingerprints.
- Implement fail-on-existing-target as the default idempotency policy at the policy/result vocabulary level; represent skip, replace, link, copy, write, and failed outcomes explicitly.
- Implement count aggregation over typed in-memory records without adding public serialization helpers.
- Add focused exercised errors only where tests need them; avoid broad placeholder error hierarchies.
- Add import/package tests proving only owning modules export code-backed names and no `SaveOp`/`CodecSelectionOp` aliases or root `rphys` exports are introduced.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/ops/test_export_layout.py tests/unit/rphys/ops/test_export_policy.py tests/unit/rphys/ops/test_export_results.py` | Prove deterministic layout, fingerprint inclusion/exclusion, policy/outcome vocabulary, and result/report count aggregation. | yes |
| `uv run pytest tests/contracts/test_export_result_contract.py` | Protect typed in-memory result/report contract if the contract test is added in this phase. | yes, if file exists |
| `make test-package` | Protect public import surface, lightweight imports, no root exports, and no shorthand aliases. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: target refs are deterministic; approved fingerprint inputs affect identity; excluded unstable inputs do not; result/report counts cover written, skipped, linked, copied, replaced, and failed states.
- Design-decision evidence: public records live under `rphys.ops.export`; report records have no public `to_dict`, JSON, or report-file schema.
- Future-roadmap/reuse evidence: no cache keys, materialization manifests, prediction/evaluation report schemas, or storage adapters are introduced.
- Example/demo evidence: idempotency and result-count examples are code-backed by unit/contract tests.
- Documentation evidence: docstrings identify in-memory-only records and Stage 8 deferrals.
- Scientific contract evidence: target identity, idempotency, and failure vocabulary are explicit and inspectable.

### Phase Workflow State

- Phase execution plan: create one worktree from `develop`, implement only export primitives/results, open one scoped PR.
- Planning/refinement budget: 1 planning round; split if public errors or fingerprint mechanics grow beyond the phase.
- Implementation/refinement budget: 1 implementation pass plus focused test fixes.
- PR review budget: 1 review pass.
- Blocker-resolution budget: block and return to planning if primitive records require durable schemas or public helper/protocol promotion.
- Pre-submit blocker gate: no write execution, no report serialization, no derived assembly, no root exports.
- Merge record: record PR link, validation commands, and accepted residual risks after merge.

### Risks And Stop Conditions

- Risks: fingerprint surface may become too broad; error taxonomy may grow beyond exercised behavior; public result records may imply durable schema semantics.
- Stop conditions: implementation attempts to add public `to_dict`, JSON, report files, cache keys, storage protocols, root exports, shorthand aliases, or derived manifest schemas; implementation cannot express deterministic targets without broad public templating.
- Assumptions: existing descriptor/ref records are sufficient for target derivation; stable primitive fingerprint content is enough for Stage 8 export identity.

### Completion Summary

- Implementation: added `rphys.ops.export` data-only records for export specs,
  targets, output layouts, policies, outcomes, field/record/export results, and
  typed in-memory reports. The phase also added deterministic target
  `FieldRef` derivation and stable schema-versioned spec fingerprints without
  save execution, codec selection, link/copy helpers, derived assembly, root
  exports, shorthand aliases, or public report serialization helpers.
- Validation: `uv run pytest tests/unit/rphys/ops/test_export_layout.py tests/unit/rphys/ops/test_export_policy.py tests/unit/rphys/ops/test_export_results.py`; `uv run pytest tests/contracts/test_export_result_contract.py`; `make test-package`; `make validate-pr`; `make test-summary`; and `git diff --check` passed locally.
- PR: [#55](https://github.com/samcantrill/rphys/pull/55)
- Merge: merged to `develop` on 2026-05-15; merge commit `6d77857ccb28dd68020c3eb358e3b659ca9d022e`.
- Follow-up: Phase 2 owns no-write codec selection and `OperationStep`
  compatibility over the Phase 1 records.

## Phase 2: OperationStep Selection Preflight

Status: merged
Slug: `selection-preflight`
Branch: `agent/stage-8-p2-selection-preflight`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p2-selection-preflight`
PR: [#56](https://github.com/samcantrill/rphys/pull/56)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: Add side-effect-free `CodecSelectionOperation` as a public `OperationStep` implementation and prove compatibility with the landed Stage 7 operation foundation.
- Files/modules owned: `src/rphys/ops/export.py`; `src/rphys/ops/__init__.py` only if owning-package re-export is narrowly approved and code-backed; `tests/contracts/test_export_operation_contract.py`; `tests/unit/rphys/ops/test_export_selection.py`.
- Behavior implemented: `CodecSelectionOperation` exposes `name`, an `OperationContract`, callable/run semantics, returns `OperationResult`, validates requested fields, derives target refs, checks codec/schema/metadata-save policy support, and returns minimal selection evidence for later save.
- Decisions applied: DD-1 full `Operation` naming; DD-2 public `OperationStep` implementation; DD-4 no-write selection; DD-10 private helper placement.
- Future-roadmap/reuse constraints: do not pre-lock specialized `SampleOperation`/`BatchOperation` inheritance; keep Stage 13 prediction preflight possible by treating fields generically.
- Examples or demos covered: OperationStep export composition; selection preflight produces no writes.
- Out of scope: actual saves, link/copy, derived datasource assembly, new sample/batch operation bases, separate export executor, raw-output execution bypass, durable selection schema.
- Dependencies: Phase 1; landed Stage 7 `OperationStep`, `OperationContract`, `OperationResult`, and `OperationPipeline`.

### Tasks

- Implement `CodecSelectionOperation` directly against `OperationStep` with full public naming and no shorthand aliases.
- Define minimal selection output needed by `SaveOperation` without making a durable wire schema.
- Validate field presence, target derivation, codec support, schema request compatibility, and metadata-save policy compatibility.
- Prove selection calls no codec `save`, link/copy helper, manifest writer, datasource scan, or filesystem write.
- Add contract tests for `isinstance(selection, OperationStep)`, operation contract shape, `OperationResult` return, and `OperationPipeline` acceptance with a tiny downstream step if `SaveOperation` is not yet present.
- Add failure tests for missing fields, invalid targets, unsupported or ambiguous codecs, and unsupported metadata policy.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/contracts/test_export_operation_contract.py tests/unit/rphys/ops/test_export_selection.py` | Prove `OperationStep` compatibility, `OperationResult` return, no-write preflight behavior, and selection failures. | yes |
| `uv run pytest tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py` | Guard Stage 6/7 operation foundation behavior while adding export operation steps. | yes |
| `make test-contract` | Exercise operation contract surfaces when the phase changes public operation behavior. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: selection validates save intent and target refs without creating files, links, copies, manifests, or datasource scans.
- Design-decision evidence: `CodecSelectionOperation` satisfies `OperationStep` and returns `OperationResult`.
- Future-roadmap/reuse evidence: no sample/batch inheritance requirement, separate executor, or prediction/evaluation behavior is added.
- Example/demo evidence: operation pipeline accepts selection and forwards `.output` through a downstream proof.
- Documentation evidence: docstrings identify selection as preflight/planning only.
- Scientific contract evidence: intended targets/codecs/schemas are inspectable before any durable side effects.

### Phase Workflow State

- Phase execution plan: branch from `develop` after Phase 1 merges; implement pure selection only; open one scoped PR.
- Planning/refinement budget: 1 planning round focused on selection evidence stability.
- Implementation/refinement budget: 1 implementation pass plus contract/unit test fixes.
- PR review budget: 1 review pass.
- Blocker-resolution budget: block if the landed `OperationStep` cannot support selection without a raw-output bypass.
- Pre-submit blocker gate: no writes, no link/copy, no manifest write, no datasource scan, no durable selection schema.
- Merge record: record PR link, validation commands, and any compatibility notes after merge.

### Risks And Stop Conditions

- Risks: selection evidence could become a de facto durable schema; codec support checks may tempt codec API broadening.
- Stop conditions: implementation bypasses `OperationResult`, creates a separate export executor, requires new Stage 7 sample/batch bases, writes files, scans outputs, or broadens codec save semantics.
- Assumptions: existing codec registry/support behavior is sufficient for preflight checks.

### Completion Summary

- Implementation: added `RecordExportRequest`, `SelectedFieldExport`,
  `ExportSelection`, and pure `CodecSelectionOperation` as a public
  `OperationStep` implementation. Selection validates requested field values,
  deterministic targets, schema requests, metadata-save policy support, codec
  request matching, and unique save-capable codec resolution without writes.
- Validation: `uv run pytest tests/contracts/test_export_operation_contract.py tests/unit/rphys/ops/test_export_selection.py`; `uv run pytest tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py`; `make test-contract`; `make test-package`; `make validate-pr`; `make test-summary`; and `git diff --check` passed locally.
- PR: [#56](https://github.com/samcantrill/rphys/pull/56)
- Merge: merged to `develop` on 2026-05-15; merge commit `f996ba1e81fce712c003ee80cf6c2eb90aa4fca8`.
- Follow-up: Phase 3 owns `SaveOperation`, filesystem idempotency checks,
  codec `save` calls, and partial-failure behavior.

## Phase 3: SaveOperation Through Codec Save And Idempotency

Status: merged
Slug: `save-operation`
Branch: `agent/stage-8-p3-save-operation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p3-save-operation`
PR: [#57](https://github.com/samcantrill/rphys/pull/57)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: Implement side-effecting `SaveOperation` as a public `OperationStep` that writes declared fields through existing codec save contracts and returns typed export results in `OperationResult.output`.
- Files/modules owned: `src/rphys/ops/export.py`; synthetic codec fixtures only if narrow additions are needed; `tests/unit/rphys/ops/test_export_save.py`; `tests/contracts/test_export_codec_contract.py`; operation contract tests extended from Phase 2.
- Behavior implemented: `SaveOperation` consumes selection/planned export inputs, reads declared runtime fields, applies fail/skip/replace/write idempotency behavior, creates one `SaveContext(target=FieldRef, metadata_policy=...)` per field, calls `CodecRegistry.save`, propagates `CodecSaveResult`, records typed field/record/export outcomes and failures, and declares operation side effects as secondary summary evidence.
- Decisions applied: DD-2 `OperationStep`; DD-3 idempotency; DD-5 codec save preservation; DD-6 result/report evidence; DD-9 focused typed errors/failures.
- Future-roadmap/reuse constraints: prediction-like fields later use the same path; no cache/materialization identity, report serialization, or workflow retry/resume semantics.
- Examples or demos covered: codec save contract preservation; idempotency conflict/skip/replace/write matrix; pipeline output forwarding.
- Out of scope: link/copy helpers except placeholder policy errors if needed; derived datasource assembly; durable report files; codec API broadening; datasource mutation.
- Dependencies: Phases 1 and 2.

### Tasks

- Implement `SaveOperation` as a public full-name `OperationStep` with `OperationResult.output` carrying `RecordExportResult` or `ExportResult`.
- Preserve pipeline forwarding by testing `OperationPipeline([selection, save])` over synthetic export inputs.
- Implement codec write execution only through `CodecRegistry.save(value, SaveContext(target=FieldRef, metadata_policy=...))`.
- Implement default existing-target conflict and explicit skip, replace, and write outcomes with correct counts.
- Define the manager-synthesized partial-failure default narrowly: invalid specs/layouts/policies and target conflicts abort; per-field codec failures may become typed failed-result evidence only when explicit partial-failure policy allows continuation.
- Preserve `CodecSaveResult` evidence in `FieldExportResult`; join export provenance outside codec results.
- Add failure tests for missing selected fields, codec save failures, invalid idempotency combinations, and no source descriptor mutation.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/ops/test_export_save.py tests/contracts/test_export_codec_contract.py tests/contracts/test_export_operation_contract.py` | Prove save execution, codec contract preservation, `OperationStep` compatibility, pipeline output forwarding, and idempotency behavior. | yes |
| `uv run pytest tests/contracts/test_codec_contract.py` | Guard existing Stage 4 codec save contract. | yes |
| `make test-unit` | Broaden over source-mirrored unit tests after adding side-effecting export behavior. | yes |
| `make test-contract` | Broaden over public operation/codec contracts. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: save writes declared fields through codecs, records typed outcomes/failures, and counts conflict/skip/replace/write behavior correctly.
- Design-decision evidence: no datasource/export state is added to `SaveContext`; codecs do not write manifests; `OperationResult.output` is primary export evidence.
- Future-roadmap/reuse evidence: no prediction runner, metric, cache key, materialization manifest, durable report file, or workflow retry engine is introduced.
- Example/demo evidence: operation pipeline selection-to-save works with synthetic codec fixtures.
- Documentation evidence: docstrings describe save side effects, idempotency, and partial-failure boundaries.
- Scientific contract evidence: field identity, target refs, codec save result, metadata policy, and failure causes remain inspectable.

### Phase Workflow State

- Phase execution plan: branch from `develop` after Phase 2 merges; implement save and focused tests; open one scoped PR.
- Planning/refinement budget: 1 planning round for partial-failure policy details.
- Implementation/refinement budget: 1 implementation pass plus test fixes.
- PR review budget: 1 review pass.
- Blocker-resolution budget: block if save requires changing Stage 4 codec save semantics or Stage 7 `OperationStep` result forwarding.
- Pre-submit blocker gate: no codec API broadening, no codec manifest writes, no durable report schema, no derived assembly, no datasource mutation.
- Merge record: record PR link, validation commands, and partial-failure policy evidence after merge.

### Risks And Stop Conditions

- Risks: partial-failure behavior can drift into workflow semantics; idempotency checks may accidentally depend on filesystem state in fingerprinting; save may tempt multi-field codec operations.
- Stop conditions: implementation broadens `SaveContext` with datasource/export state, bypasses `CodecRegistry.save`, exposes workflow retry/resume behavior, introduces public durable schemas, or bypasses `OperationStep`/`OperationResult`.
- Assumptions: explicit idempotency policy is enough for Stage 8; codec failures can be represented as typed raised errors or failed-result evidence without new workflow semantics.

### Completion Summary

- Implementation: added side-effecting `SaveOperation` as a public
  `OperationStep` implementation consuming `ExportSelection`. The operation
  applies write idempotency, calls `CodecRegistry.save` only through
  `SaveContext(target=FieldRef, metadata_policy=...)`, preserves
  `CodecSaveResult` evidence, and returns typed `RecordExportResult` output.
- Validation: `uv run pytest tests/unit/rphys/ops/test_export_save.py tests/contracts/test_export_codec_contract.py tests/contracts/test_export_operation_contract.py`; `uv run pytest tests/contracts/test_codec_contract.py`; `make test-unit`; `make test-contract`; `make test-package`; `make validate-pr`; `make test-summary`; and `git diff --check` passed locally.
- PR: [#57](https://github.com/samcantrill/rphys/pull/57)
- Merge: merged to `develop` on 2026-05-15; merge commit `5357da9b9dd18a4e837dff23788581049af31746`.
- Follow-up: Phase 4 owns link/copy materialization, ordered lineage
  behavior, and unsupported-protocol failures.

## Phase 4: Link/Copy Lineage And Private Local Helpers

Status: merged
Slug: `link-copy-lineage`
Branch: `agent/stage-8-p4-link-copy-lineage`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p4-link-copy-lineage`
PR: [#58](https://github.com/samcantrill/rphys/pull/58)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: Add explicit link/copy policy behavior and public ordered source/target `ResourceRef` lineage in export results while keeping filesystem helpers private and local-only.
- Files/modules owned: private helpers inside `src/rphys/ops/export.py` or a private local export submodule; `tests/unit/rphys/ops/test_export_lineage.py`; `tests/unit/rphys/ops/test_export_local_links.py`; package import-boundary tests.
- Behavior implemented: link/copy outcomes and counts, ordered source/target `ResourceRef` lineage in `FieldExportResult`, fail-loud missing lineage, unsupported protocols, cross-protocol behavior, and symlink-to-copy fallback only under explicit policy with copied outcome.
- Decisions applied: DD-3 explicit link/copy outcomes; DD-8 public lineage evidence/private local helper scope; DD-10 no premature protocols.
- Future-roadmap/reuse constraints: second storage backends can reuse result semantics later through an additive adapter; Phase 4 must not introduce the adapter before a second backend exists.
- Examples or demos covered: link/copy lineage preservation and fail-loud unsupported behavior.
- Out of scope: public storage adapter protocols, cloud/object storage support, codec-only link/copy, silent fallback, derived datasource assembly, workflow retry/resume.
- Dependencies: Phases 1 and 3; Phase 2 if link/copy remains operation-driven through selection evidence.

### Tasks

- Add private local filesystem helpers for link and copy operations, with no public helper exports.
- Extend policy handling to request link/copy outcomes explicitly and to distinguish linked/copied from codec writes.
- Require ordered source and target `ResourceRef` lineage for link/copy results.
- Fail loudly for missing source lineage, unsupported protocols, cross-protocol link/copy, and symlink failure when copy fallback is not explicit.
- Implement explicit symlink-to-copy fallback only when policy requests it; count the result as copied, not linked.
- Add package/import tests proving helpers are not exported and no storage adapter protocol is public.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/ops/test_export_lineage.py tests/unit/rphys/ops/test_export_local_links.py` | Prove lineage records, link/copy outcomes, fail-loud unsupported behavior, and explicit fallback behavior. | yes |
| `make test-package` | Prove private helpers are not public and import boundaries remain lightweight. | yes |
| `make test-unit` | Broaden over export unit behavior after filesystem helper changes. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: linked/copied outcomes are distinguishable from codec writes; source/target `ResourceRef`s are ordered and inspectable; unsupported behavior fails loudly.
- Design-decision evidence: helper implementation stays private and local-filesystem-only; no public storage protocol or hidden fallback is introduced.
- Future-roadmap/reuse evidence: result semantics are backend-neutral enough for a future adapter, but no adapter is exposed in Stage 8.
- Example/demo evidence: tests cover missing lineage, unsupported protocol, cross-protocol rejection, and explicit fallback.
- Documentation evidence: docstrings or docs explain link/copy lineage and local-helper limitations.
- Scientific contract evidence: link/copy provenance is public result evidence and cannot be inferred only from target files.

### Phase Workflow State

- Phase execution plan: branch from `develop` after Phase 3 merges; implement private local helpers and lineage tests; open one scoped PR.
- Planning/refinement budget: 1 planning round focused on platform symlink capability.
- Implementation/refinement budget: 1 implementation pass plus platform-safe test fixes.
- PR review budget: 1 review pass.
- Blocker-resolution budget: block if link/copy requires public storage adapters or codec context changes.
- Pre-submit blocker gate: no public storage protocols, no cloud/object storage claims, no silent fallback, no codec-only hidden link/copy.
- Merge record: record PR link, validation commands, platform capability notes, and accepted residual risk after merge.

### Risks And Stop Conditions

- Risks: symlink behavior varies by platform; helper code may grow into a de facto adapter; lineage evidence may be incomplete for synthetic fixtures.
- Stop conditions: implementation exposes storage adapter/protocol APIs, silently falls back from symlink to copy, supports unsupported protocols by best effort, hides lineage in codec results only, or requires changing codec save contracts.
- Assumptions: local filesystem fixtures are sufficient for Stage 8; platform-specific symlink tests can be capability-gated.

### Completion Summary

- Implementation: added private local-file link/copy helpers and routed
  `SaveOperation` link/copy materialization policies through them while
  preserving ordered source/target `ResourceRef` lineage in
  `FieldExportResult`.
- Validation: `uv run pytest tests/unit/rphys/ops/test_export_lineage.py tests/unit/rphys/ops/test_export_local_links.py`; `make test-package`; `make test-unit`; `make validate-pr`; `make test-summary`; and `git diff --check` passed locally.
- PR: [#58](https://github.com/samcantrill/rphys/pull/58)
- Merge: merged to `develop` on 2026-05-15; merge commit `4d25adaa6380fe243bd2b6e99edfe4ebdaf3bffd`.
- Follow-up: Phase 5 owns descriptor-only derived datasource assembly and the
  final synthetic export-to-reload vertical slice.

## Phase 5: Descriptor-Only Derived Datasource Assembly And Final Synthetic Round Trip

Status: merged
Slug: `derived-datasource-roundtrip`
Branch: `agent/stage-8-p5-derived-datasource-roundtrip`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p5-derived-datasource-roundtrip`
PR: [#59](https://github.com/samcantrill/rphys/pull/59)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: Convert successful export results into descriptor-only derived datasource assemblies and prove the full synthetic Stage 8 export-to-reload vertical slice.
- Files/modules owned: `src/rphys/datasources/derived.py`; `src/rphys/datasources/__init__.py` only for narrow code-backed owning-package exports if needed; `tests/unit/rphys/datasources/test_derived.py`; `tests/integration/test_stage8_export_derived_datasource_flow.py`; package/docs checks.
- Behavior implemented: `DerivedDataSourceAssembly`, `DerivedDataSourceBuilder`, derived `DataSourceRef`, ordered derived `RecordRef`s, assembly evidence from successful `FieldExportResult`s, source descriptor immutability, no-rescan assembly, normal indexing/loading through existing machinery, and optional prediction-like field pressure.
- Decisions applied: DD-1 descriptor-only `rphys.datasources.derived`; DD-6 in-memory export records; DD-7 no-rescan derived assembly with existing ref serialization; future-roadmap safety findings for Stage 9/13/14/15.
- Future-roadmap/reuse constraints: no durable derived datasource manifest wire schema; no `DataSourceIndexManifest` reuse; Stage 9/15 materialization manifests and Stage 13 prediction/evaluation remain later additive work.
- Examples or demos covered: synthetic datasource/index/sample to exported derived datasource reload; descriptor assembly without manifest collision; optional prediction-like field dry run.
- Out of scope: save/export execution under datasources, output rescans, source descriptor mutation, cache/materialization manifests, prediction runners, metrics, analysis reports, durable derived manifest round trip.
- Dependencies: Phases 1 through 4.

### Tasks

- Implement descriptor-only `DerivedDataSourceAssembly` and `DerivedDataSourceBuilder` under `rphys.datasources.derived`; do not add a public derived manifest writer surface in Stage 8.
- Consume successful export results and assemble new derived `RecordRef`s and a derived `DataSourceRef` using existing ref serialization semantics.
- Preserve source datasource/record identity as assembly evidence where needed without mutating source descriptors.
- Reject empty/no-success assemblies and invalid result combinations with focused exercised errors.
- Prove no output directory scanning and no `DataSourceIndexManifest` reuse.
- Add integration coverage from synthetic datasource/index/sample through selection, save, optional link/copy where appropriate, derived assembly, index, and reload through existing sample machinery.
- Add docs/docstrings showing explicit operation-driven export, descriptor-only assembly, in-memory-only reports, and deferred durable schemas.
- Run package/import checks to prove datasource modules do not own save/export execution and imports remain lightweight.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_derived.py tests/integration/test_stage8_export_derived_datasource_flow.py` | Prove descriptor-only derived assembly and the final synthetic export-to-reload round trip. | yes |
| `uv run pytest tests/integration/test_stage5_synthetic_datasource_flow.py` | Guard existing Stage 5 datasource/index/sample baseline while adding derived assembly. | yes |
| `make test-integration` | Broaden over integration behavior after the final vertical slice lands. | yes |
| `make test-package` | Protect public imports, lightweight boundaries, no root exports, and descriptor-only datasource module behavior. | yes |
| `rg -n "SaveOp|CodecSelectionOp|to_dict|JSON|DataSourceIndexManifest|report file" docs src tests` | Review for accidental shorthand names or public durable schema implications; findings may be acceptable only when they are existing planning text or explicit deferral language. | yes |
| `make test` | Final broad regression for the completed Stage 8 surface, unless PR scope justifies a narrower documented substitution. | yes |
| `git diff --check` | Catch whitespace and patch hygiene issues. | yes |

### Acceptance Evidence

- Behavior evidence: successful export results produce derived refs; derived refs index/load through existing machinery; failed/skipped fields follow explicit policy; no output rescan is required.
- Design-decision evidence: `rphys.datasources.derived` remains descriptor-only; no save/export execution, durable derived manifest schema, or `DataSourceIndexManifest` reuse appears.
- Future-roadmap/reuse evidence: Stage 9/15 and Stage 13 remain additive through derived refs and normal field export, not new Stage 8 cache/prediction/evaluation contracts.
- Example/demo evidence: integration test proves synthetic datasource/index/sample to export to derived datasource reload; optional prediction-like field remains ordinary field export if included.
- Documentation evidence: public docs/docstrings record operation-driven export, descriptor-only assembly, in-memory-only report records, and durable-schema deferrals.
- Scientific contract evidence: source/target refs, lineage, idempotency, codec save evidence, and assembly provenance remain recoverable from typed records/descriptors.

### Phase Workflow State

- Phase execution plan: branch from `develop` after Phase 4 merges; implement derived assembly and final integration proof; open one scoped PR.
- Planning/refinement budget: 1 planning round, with an expanded path allowed for integration fixture gaps.
- Implementation/refinement budget: 1 implementation pass plus integration fixture/test fixes.
- PR review budget: 1 review pass, with extra focus on datasource/export dependency direction.
- Blocker-resolution budget: block if normal reload requires output scans, Stage 5 index manifest repurposing, or a new durable derived manifest schema.
- Pre-submit blocker gate: no save/export code under datasources, no durable derived manifest wire schema, no output rescan, no cache/materialization/prediction/evaluation behavior.
- Merge record: record PR link, validation commands, final Stage 8 residual risks, and deferred schema/storage revisit triggers.

### Risks And Stop Conditions

- Risks: Stage 5 sample-builder fixtures may need small support additions; descriptor-only assembly may be insufficient for cross-process reload; integration scope could grow.
- Stop conditions: implementation reuses `DataSourceIndexManifest` as a derived datasource manifest, adds output directory rescans, introduces public durable manifest schemas, moves save/export execution into datasources, or adds prediction runner/metric/cache/materialization behavior.
- Assumptions: existing `DataSourceRef`/`RecordRef` serialization and synthetic Stage 5 flow can support the Stage 8 vertical slice.

### Completion Summary

- Implementation: added descriptor-only `rphys.datasources.derived` with
  `DerivedDataSourceAssembly` and `DerivedDataSourceBuilder`; successful
  export evidence now assembles derived `DataSourceRef` and ordered
  `RecordRef`s without output rescans or durable derived manifests.
- Validation: targeted derived tests, Stage 5 baseline, `make test-integration`,
  `make test-package`, `make test`, `make validate-pr`, `make test-summary`,
  `uv lock --check` through validation, grep gate, and `git diff --check`
  passed locally.
- PR: [#59](https://github.com/samcantrill/rphys/pull/59).
- Merge: squash merged to `develop` at
  `abbeb405d456b7321b8a6c8bb3511dc5fb3f9f68`.
- Follow-up: durable derived datasource manifest schemas, cross-process
  derived manifest interchange, storage adapter protocols, cache/materialization
  manifests, prediction/evaluation/report behavior, and public report
  serialization remain deferred.

## Cross-Phase Validation

- Full relevant test command: run phase-targeted tests before each PR; run `make test-unit`, `make test-contract`, `make test-integration`, `make test-package`, and `git diff --check` by the final phase; run `make test`, `make test-summary`, `make validate-pr`, and `uv lock --check` before final Stage 8 completion or document why a narrower set was accepted.
- Docs/template checks: keep docs and docstrings aligned with full `Operation` names, in-memory-only report records, descriptor-only derived assembly, no `DataSourceIndexManifest` reuse, no output rescans, no public storage adapter, and no root exports. Use targeted `rg` checks in Phase 5.
- Scientific/workflow contract checks: prove deterministic target identity, explicit idempotency, typed failure/result evidence, source/target lineage, no hidden overwrite, no log-only evidence, no datasource/trainer/metric implicit artifacts, and no workflow retry/resume runtime.
- Example/demo checks: maintain tests for OperationStep composition, no-write selection, codec save preservation, idempotency outcomes, link/copy lineage, derived datasource reload, and optional prediction-like field pressure if fixture complexity remains low.
- Manual review focus: dependency direction between `rphys.ops.export`, `rphys.io.codecs`, and `rphys.datasources.derived`; public API naming; durable schema deferrals; partial-failure boundaries; import weight; private helper containment; future-roadmap revisit triggers.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| No readiness blocker for drafting phases. | note | Planning gates, validation/phase shaping, plan quality, specialist evidence, decision traceability, and adversarial review evidence are recorded in `planning.md`. | resolved |
| Manager review completed. | note | The implementation plan was reviewed against the passed Stage 8 planning gates, validation strategy, phase shaping, and workflow approval rules; no clear planning issue required refinement. | resolved |
| Partial-failure policy remains an implementation-level risk. | concern | Phase 3 narrows the default: invalid specs/layouts/policies and target conflicts abort; per-field failures can be result evidence only under explicit partial-failure policy. Reopen DQ-8 only if implementation promotes this into broader durable workflow semantics. | accepted risk |
| Platform symlink behavior may be fragile. | concern | Phase 4 requires conservative local fixtures and capability-gated symlink checks; copy/fail-loud behavior remains required. | accepted risk |
| Derived descriptor assembly may expose cross-process reload pressure. | concern | Phase 5 blocks durable derived manifest schemas in Stage 8 and records the Stage 9/15 or downstream cross-process reload revisit trigger. | accepted risk |

Gate result:

- Status: approved.
- Review evidence: this plan maps the passed Stage 8 planning gates to five sequential implementation phases with ownership, behavior, decisions, future-roadmap constraints, examples, validation, acceptance evidence, risks, assumptions, and stop conditions. Managing-agent review found no remaining blocker or material maintainer question.
- Accepted risks: partial-failure policy details, platform-specific symlink behavior, integration fixture complexity, optional sample/batch adaptation, future durable report schema pressure, future durable derived manifest pressure, and future storage adapter pressure.
- Revisit triggers: implementation needs public helper/protocol/storage-adapter promotion; implementation proposes replacing existing codec save semantics; implementation bypasses `OperationStep`/`OperationResult`; implementation introduces report serialization, derived manifest wire schemas, output rescans, `DataSourceIndexManifest` reuse, cache/materialization schemas, prediction/evaluation/training behavior, or root/shorthand public exports.

## Final Approval

- Approval status: approved 2026-05-15 / managing agent.
- Approved scope: Stage 8 only across the five phases listed above. Phase execution should proceed through `.codex/workflows/roadmap-version-implementation.md` using one isolated worktree per phase.
- Accepted risks: partial-failure policy details, platform symlink behavior, fixture complexity, optional sample/batch adaptation, and future additive schema/adapter revisit pressure.
- Deferred items: durable `ExportReport` serialization, public report `to_dict`/JSON/report-file schema, durable derived datasource manifest wire schema, `DataSourceIndexManifest` reuse for derived datasources, output rescans, public storage adapter/protocols, cache/materialization manifests, prediction/evaluation/metric/reporting behavior, training/workflow artifact runtime, broad sample/batch specialization, concrete codec catalog, and heavy optional dependencies.
