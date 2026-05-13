# Roadmap Stage 3 Implementation Plan

Status: approved; phase execution ready
Roadmap version: `v3`
Planning document: `docs/roadmap/stage-3/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 2 pending
Blockers: none

## Summary

- Goal: implement Milestone 3 lazy references and index items as dependency-free, serializable descriptors for resources, fields, field-native temporal views, datasource provenance, schema declarations, and future sample-builder inputs.
- Source functionality-agreement gate: passed in `docs/roadmap/stage-3/planning.md`; FQ-1 through FQ-8 are repo-resolved.
- Approved behavior: `ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, `FieldView`, `DataSourceRef`, `RecordRef`, `DataSourceSchema`, and `IndexItem` are pure lazy IO descriptors with typed fail-loud diagnostics and no payload loading.
- Source behavior confirmation: passed; FR-1 through FR-8 are locked.
- Key design constraints: focused public submodules; package re-exports only for implemented names; no root `rphys` re-exports; immutable value descriptors; explicit primitive `to_dict()` and `from_dict()`; no public registries; no schema-version fields; no descriptor fingerprints; no stable datasource-index item identity; no `FieldRef.member`; no `IndexItem.item_id`; optional mapping defaults use `None` in Python signatures while preserving empty-mapping semantics.
- Source design-agreement gate: passed; DQ-1 through DQ-7 are maintainer approved, and DQ-8 is a recorded recommendation.
- Source functionality-agreement queue: FQ-1 through FQ-8 are resolved and locked.
- Source design-agreement queue: DQ-1 through DQ-7 are locked; DQ-8 has no approval requirement.
- Examples covered: EX-1 RGB video plus BVP field views; EX-2 datasource record with leakage metadata and minimal schema; EX-3 role-qualified `IndexItem`; EX-4 primitive descriptor round trip; EX-5 negative extension and coupling exclusions.
- Source phase shaping: accepted P1 public surface/errors, P2 IO descriptors/indexes/views, P3 datasource refs/schema, P4 `IndexItem`, P5 contract examples/docs/final validation.
- Source plan quality gate: passed; no blockers, stale specialist evidence, unresolved queue packets, or missing review evidence.
- Out of scope: codecs, codec registries, load/save contexts, `SampleBuilder`, lazy `SampleField`, runtime `Sample` construction, datasource adapters/builders/indexes/manifests, filters, split builders, validation reports, transforms, export, training adapters, runtime samples, seconds/spatial slices, multi-member items, schema-version fields, fingerprints, stable datasource-index item identity, `FieldRef.member`, `IndexItem.item_id`, and root `rphys` re-exports.

## Implementation Workflow State

- Implementation-plan quality gate: passed; maintainer approved phase execution on 2026-05-13 by requesting implementation under `.codex/workflows/roadmap-version-implementation.md`
- Review pass: automatic Stage 11 implementation-planning pass completed; approval blocker cleared by maintainer request on 2026-05-13
- Refinement pass: not started
- Confirmation review: not started
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Readiness Check

| Condition | Evidence | Result |
| --- | --- | --- |
| Functionality-agreement review and behavior-confirmation gates passed | `Stage Gates` records both gates as passed; `Behavior Confirmation` locks FR-1 through FR-8. | pass |
| Design-agreement gate passed | `Stage Gates` records design agreement as passed; DQ-1 through DQ-7 are locked. | pass |
| Validation and phase-shaping decision gate resolved | `Stage Gates`, `Validation Strategy`, and `Phase Shaping` record VN-1 through VN-9 and P1 through P5 with no queue reopening. | pass |
| Plan quality gate passed | `Plan Quality Gate` result is passed with no blocking findings. | pass |
| Required specialist-pass handoffs present and current | Plan quality evidence lists current context scaffold, functionality mapper, design proposer, design implication reviewer, validation planner, and plan-quality reviewer contributions. | pass |
| Design implication/coherence/examples review completed after design proposal | Change log records design proposal, then design implication review, with EX-1 through EX-5 and DD-10 auto-approval overturned. | pass |
| Plan quality review checked specialist evidence and unresolved packets | Plan quality rows explicitly check specialist evidence, staleness, manager-only replacement, and queue packet finality. | pass |
| No high-impact agreement-queue item unresolved or reopened | FQ-1 through FQ-8 are repo-resolved; DQ-1 through DQ-7 are approved; DQ-8 is a recommendation. | pass |
| No design decision is blocked | Design Decision Triage records no blocked decisions. | pass |
| No unresolved `needs maintainer discussion` decision | Plan quality records no unresolved `needs maintainer discussion` packets. | pass |
| No approval-worthy decision is merely pending or ready | DQ-1 through DQ-7 have recorded maintainer approvals; DQ-8 is not approval-worthy. | pass |
| Maintainer-judgment packets have recorded answers | Change log records maintainer approvals for DQ-1 through DQ-7 on 2026-05-13. | pass |
| Auto-approved decisions are traceable and adversarially reviewed | No auto-approved decisions remain; DD-10 was overturned, and DD-11 is a recorded recommendation with adversarial review evidence. | pass |

Readiness result: passed. No implementation readiness blocker prevents phase creation.

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `public-surface-errors` | merged | `agent/stage-3-p1-public-surface-errors` | [#16](https://github.com/samcantrill/rphys/pull/16) | `rphys.errors`, package import-boundary expectations, package/error tests | Establish typed diagnostics and public-surface guardrails | `make test-package`; focused error unit tests; `git diff --check` | EX-5 coupling/import exclusions |
| 2 | `io-descriptors-indexes` | pending | `agent/stage-3-p2-io-descriptors-indexes` | pending | `src/rphys/io/`, IO unit tests, IO contract examples | Implement resource, field, index, slice, and view descriptors | `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | EX-1, EX-4, EX-5 |
| 3 | `datasource-refs-schemas` | pending | `agent/stage-3-p3-datasource-refs-schemas` | pending | datasource refs/schema modules and tests | Implement datasource provenance and declaration-only schema descriptors | `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | EX-2, EX-4, EX-5 |
| 4 | `index-item-composition` | pending | `agent/stage-3-p4-index-item-composition` | pending | `src/rphys/datasources/index_items.py`, index-item tests, contract example updates | Implement role-qualified lazy item composition | `make test-unit`; `make test-contract`; `make test-package`; `git diff --check` | EX-3, EX-4, EX-5 |
| 5 | `lazy-reference-hardening` | pending | `agent/stage-3-p5-lazy-reference-hardening` | pending | contract tests, docs/docstrings, package boundary checks, final validation evidence | Prove the full Stage 3 chain and exclusions | focused suites plus `make test`, `make test-summary`, `make validate-pr`, `uv lock --check`, `git diff --check` | EX-1 through EX-5 |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| No readiness blocker found. | Stage 11 readiness check against `docs/roadmap/stage-3/planning.md` | None before phase execution; maintainer approval is recorded in the Final Approval section. | resolved |

## Phase 1: Public Surface And Diagnostics

Status: merged
Slug: `public-surface-errors`
Branch: `agent/stage-3-p1-public-surface-errors`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p1-public-surface-errors`
PR: [#16](https://github.com/samcantrill/rphys/pull/16)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish intentional Stage 3 typed diagnostics and import-boundary guardrails before descriptor behavior spreads.
- Files/modules owned: `src/rphys/errors.py`; `src/rphys/io/__init__.py`; `src/rphys/datasources/__init__.py`; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; `tests/unit/rphys/test_errors.py`. Descriptor submodules are introduced in P2 through P4 only when they contain implemented descriptor behavior.
- Behavior implemented: package import boundaries and diagnostic conventions are guarded before descriptor behavior exists; concrete descriptor errors are added only in the descriptor phases that raise them; package surfaces re-export implemented names only; root `rphys.__all__` remains empty.
- Decisions applied: DD-1, DD-8, DD-11; DQ-1 and DQ-8.
- Examples or demos covered: EX-5 import and coupling exclusions.
- Out of scope: placeholder descriptor modules, descriptor constructor behavior, serialization, IO semantics, datasource provenance, `IndexItem`, codecs, builders, manifests, and runtime samples.
- Dependencies: Stage 1/2 package and error conventions.

### Tasks

- Preserve broad error-base behavior and add only any concrete error class that is directly exercised by P1 behavior; otherwise defer descriptor-specific concrete errors to P2 through P4.
- Keep `rphys.io.__all__` and `rphys.datasources.__all__` limited to implemented public names; do not add descriptor submodules or exports before code-backed descriptor behavior exists.
- Update package tests for exact public surfaces, submodule imports, no root re-exports, and no duplicated Stage 1 vocabulary exports.
- Update error tests for `__all__`, inheritance, readable message, and context preservation.
- Establish lightweight import expectations for Stage 3 package homes; defer concrete submodule import checks to the phases that introduce those submodules.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify public import/export and lightweight import boundaries. | yes |
| `make test-unit` focused on `tests/unit/rphys/test_errors.py` | Verify broad error-base behavior and any P1-exercised concrete error, if one is added. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: `rphys.io` and `rphys.datasources` package imports remain lightweight while diagnostics still preserve readable messages and structured context.
- Design-decision evidence: no root `rphys` re-exports, no placeholder descriptor modules or exports, and only exercised concrete errors are public.
- Example/demo evidence: EX-5 no-coupling checks are represented in package tests.
- Documentation evidence: package/module docstrings identify package homes without promising codecs, builders, registries, or runtime hooks.
- Scientific contract evidence: no IO loading, probing, slice semantics, datasource scanning, or sample construction appears in the public surface.

### Phase Workflow State

- Phase execution plan: complete in `docs/roadmap/stage-3/phases/public-surface-errors.md`
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: return to planning if approved public module homes or error names need to change from DQ-1.
- Pre-submit blocker gate: no root exports, placeholder public modules or names, heavy optional imports, workflow/artifact packages, codecs, builders, registries, or unexercised errors.
- Merge record: pending

### Risks And Stop Conditions

- Risks: adding public names or modules before behavior exists would freeze placeholders; over-specific errors can become compatibility burden; package tests may need careful transition from currently empty deferred packages.
- Stop conditions: implementation requires changing approved public homes, adding root exports, or adding broad placeholder diagnostics.
- Assumptions: later phases add descriptor modules and public names as code-backed exports when they implement descriptor behavior.

### Completion Summary

- Implementation: tightened Stage 3 package-home docstrings and package/error tests without adding descriptor modules, descriptor exports, root exports, or concrete Stage 3 errors.
- Validation: `make test-package`, `make test-unit`, and `git diff --check` passed before PR submission.
- PR: [#16](https://github.com/samcantrill/rphys/pull/16) opened against `develop`.
- Merge: merged into `develop` as `5876867` at 2026-05-13T05:39:02Z.
- Follow-up: P2 through P4 own replacing deferred-name guards with code-backed descriptor exports and concrete descriptor errors only where behavior raises them.

## Phase 2: IO Descriptors And Temporal Indexes

Status: pending
Slug: `io-descriptors-indexes`
Branch: `agent/stage-3-p2-io-descriptors-indexes`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p2-io-descriptors-indexes`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement the dependency-free lazy IO descriptor chain below datasource refs.
- Files/modules owned: `src/rphys/io/resources.py`; `src/rphys/io/fields.py`; `src/rphys/io/indexes.py`; `src/rphys/io/__init__.py`; concrete IO/index errors exercised by this phase; `tests/unit/rphys/io/test_resources.py`; `tests/unit/rphys/io/test_fields.py`; `tests/unit/rphys/io/test_indexes.py`; targeted package and contract tests.
- Behavior implemented: `ResourceRef(uri, protocol, storage_options={})`; `FieldRef(key, resources, schema=None, metadata={})`; narrow `FieldIndex`; `TemporalIndexSlice(start, stop, step=1)`; `FieldView(field_ref, field_index=None)`; strict construction; immutable/value semantics; primitive serialization; field-native half-open index semantics.
- Decisions applied: DD-2, DD-3, DD-4, DD-5, DD-8, DD-10, DD-11; DQ-2, DQ-3, DQ-4, DQ-8.
- Examples or demos covered: EX-1 field views with different temporal indexes; EX-4 primitive descriptor serialization; EX-5 negative coupling checks.
- Out of scope: datasource refs/schema/index items; codec resolution; `SampleBuilder`; seconds/spatial indexes; URI parsing; resource probing; load/save/build methods; hidden registries; resource canonicalization; fingerprints; `FieldRef.member`.
- Dependencies: P1 public-surface and diagnostic guardrails.

### Tasks

- Implement immutable descriptor objects with strict construction, copied mappings/sequences, value equality, and no broad public hash guarantee.
- Use `None` defaults for optional mapping parameters in Python signatures, then materialize copied empty mappings internally; `{}` in planning text means empty-default semantics, not a mutable public default.
- Coerce approved vocabulary values to `DataKey`, `SchemaName`, and `MetadataKey` where applicable.
- Implement explicit primitive `to_dict()` and `from_dict()` for IO descriptors with stable key spelling and no schema-version fields.
- Implement Stage 3-only private reconstruction for supported `FieldIndex` classes; unknown index type tags must fail loudly.
- Validate `TemporalIndexSlice` as field-native half-open `[start, stop)` with non-negative bounds and positive step; accept `step > 1` as descriptor data.
- Assert exclusions: no `member`, role, payload, handles, codec/probe/load/save/build behavior, URI parsing, seconds/spatial axes, implicit alignment, or public registry.
- Preserve `FieldRef.resources` ordering as descriptor data only; do not attach implicit member, selector, priority, canonicalization, or multi-resource binding semantics in Stage 3.
- Add unit and contract coverage for construction, invalid input, equality, mapping/resource isolation, serialization, and coupling exclusions.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify IO descriptor construction, validation, equality, isolation, and serialization. | yes |
| `make test-contract` | Verify public IO examples and serialization contracts. | yes |
| `make test-package` | Verify public imports and no heavy optional imports. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: IO descriptors construct valid examples, reject invalid inputs with approved typed errors, and round-trip through primitive dicts.
- Design-decision evidence: `ResourceRef` has explicit protocol and uninterpreted URI; `FieldRef` has no `member`; `TemporalIndexSlice` is field-native; `FieldView` is role-free.
- Example/demo evidence: RGB and BVP field views can carry different numeric indexes without implying alignment.
- Documentation evidence: docstrings explain fields, primitive serialization, no handles/payloads, field-native index semantics, and Stage 4/5 deferrals.
- Scientific contract evidence: no resampling, padding, temporal alignment, seconds conversion, spatial indexing, or full-load fallback is introduced.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: expanded because serialization key spelling and temporal semantics are compatibility-sensitive.
- Blocker-resolution budget: return to planning if IO descriptors require codec loading, URI parsing, registry dispatch, seconds/spatial indexes, schema-version fields, fingerprints, or `FieldRef.member`.
- Pre-submit blocker gate: no handles, arrays, payloads, probes, load/save/build methods, public registries, root exports, schema-version fields, fingerprints, or member fields.
- Merge record: pending

### Risks And Stop Conditions

- Risks: primitive dict key spelling becomes durable; private index reconstruction can become a hidden registry; temporal slice semantics can be misread as cross-field alignment.
- Stop conditions: future index support cannot be represented without changing DQ-3/DQ-4, or validation requires runtime codec behavior.
- Assumptions: future codecs will interpret `ResourceRef.uri` internals and unsupported access behavior without changing Stage 3 descriptor meaning.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 3: Datasource Refs And Schema Descriptors

Status: pending
Slug: `datasource-refs-schemas`
Branch: `agent/stage-3-p3-datasource-refs-schemas`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p3-datasource-refs-schemas`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement provenance-bearing datasource and record descriptors plus a minimal declaration-only datasource schema.
- Files/modules owned: `src/rphys/datasources/refs.py`; `src/rphys/datasources/schemas.py`; `src/rphys/datasources/__init__.py`; concrete datasource/schema errors exercised by this phase; `tests/unit/rphys/datasources/test_refs.py`; `tests/unit/rphys/datasources/test_schemas.py`; targeted package and contract tests.
- Behavior implemented: `DataSourceRef(datasource_id, source=None, schema=None, metadata={})`; `RecordRef(datasource, record_id, fields, metadata={})`; `DataSourceSchema(fields, metadata={})`; mandatory IDs; non-empty field maps; metadata key coercion; primitive serialization; schema declarations using `DataKey -> FieldSpec`.
- Decisions applied: DD-2, DD-3, DD-6, DD-7, DD-8, DD-10, DD-11; DQ-2, DQ-3, DQ-5, DQ-6, DQ-8.
- Examples or demos covered: EX-2 datasource record with leakage metadata and minimal schema; EX-4 serialization; EX-5 coupling exclusions.
- Out of scope: `IndexItem`; datasource adapters; scans; filters; grouping; splits as trainer loop mode; builders; validation reports; expected/observed schema distinctions; manifest codecs; schema-version fields; fingerprints; stable datasource-index identity.
- Dependencies: P1 public-surface and diagnostic guardrails and P2 IO descriptors.

### Tasks

- Implement datasource and record descriptor classes with immutable/value semantics and strict copied metadata/field mappings.
- Use `None` defaults for optional metadata mappings in Python signatures, then materialize copied empty mappings internally.
- Require non-empty `RecordRef.fields` keyed by intrinsic `DataKey -> FieldRef` and validate each mapping key against its `FieldRef.key`.
- Implement `DataSourceSchema(fields, metadata={})` with non-empty `DataKey -> FieldSpec` declarations and key/spec consistency.
- Preserve leakage-sensitive values such as `source_id`, `subject_id`, `split`, and `group` as metadata, not first-class constructor fields.
- Implement primitive round trips for datasource refs, record refs, and schemas with no schema-version, fingerprint, validation-status, manifest, or expected/observed fields.
- Add tests that prevent scanning, filter mutation, builder behavior, validation reports, and payload validation from entering Stage 3.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify datasource refs, record refs, schemas, metadata coercion, field consistency, and serialization. | yes |
| `make test-contract` | Verify datasource provenance/schema examples. | yes |
| `make test-package` | Verify public imports remain intentional and lightweight. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: datasource and record descriptors preserve mandatory identity, non-empty field presence, and primitive metadata.
- Design-decision evidence: no fingerprint, schema-version, validation evidence/status, expected/observed split, scanning, filtering, or builder behavior exists.
- Example/demo evidence: synthetic record examples carry subject/split/group/source metadata and schema declarations without loading data.
- Documentation evidence: docstrings distinguish declaration-only schema from validation evidence or observed payload facts.
- Scientific contract evidence: leakage metadata remains inspectable and stable record identity is preserved before windowing.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: expanded because provenance and schema scope affect later datasource stages.
- Blocker-resolution budget: return to planning if datasource descriptors require fingerprints, schema-version fields, expected/observed validation reports, scans, filters, builders, or first-class subject/split/group fields.
- Pre-submit blocker gate: no manifest fields, fingerprints, datasource adapter behavior, validation status, expected/observed split, mutation APIs, or `IndexItem`.
- Merge record: pending

### Risks And Stop Conditions

- Risks: metadata-only leakage context is less discoverable than first-class fields; `FieldSpec` reuse can blur declaration versus runtime payload meaning; serialization shape creates compatibility pressure for Stage 5 manifests.
- Stop conditions: implementation cannot preserve required provenance without adding first-class provenance fields or stable fingerprints.
- Assumptions: Stage 5 datasource validation and index manifests can wrap these descriptors without changing constructor semantics.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Role-Qualified IndexItem Composition

Status: pending
Slug: `index-item-composition`
Branch: `agent/stage-3-p4-index-item-composition`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p4-index-item-composition`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: implement the pure lazy IO item unit consumed later by `SampleBuilder`.
- Files/modules owned: `src/rphys/datasources/index_items.py`; `src/rphys/datasources/__init__.py`; concrete index-item errors exercised by this phase; `tests/unit/rphys/datasources/test_index_items.py`; targeted contract and package tests.
- Behavior implemented: `IndexItem(fields, record, metadata={})` with non-empty `FieldLocator -> FieldView` mapping, mandatory `RecordRef`, primitive metadata, locator/view key consistency, record field membership checks, different field-native indexes per field, primitive serialization, and explicit non-alignment.
- Decisions applied: DD-2, DD-3, DD-5, DD-6, DD-8, DD-9, DD-10, DD-11; DQ-2, DQ-3, DQ-4, DQ-5, DQ-7, DQ-8.
- Examples or demos covered: EX-3 role-qualified future supervised sample; EX-4 serialization; EX-5 coupling exclusions.
- Out of scope: runtime `Sample`, `FieldValue`, lazy `SampleField`, `SampleBuilder`, transforms, augmentations, export, training, stochastic/nested/multi-member items, `item_id`, fingerprints, datasource-index identity, index manifests, implicit alignment.
- Dependencies: P2 IO descriptors and P3 datasource refs/schema descriptors.

### Tasks

- Implement immutable/value `IndexItem` with copied field and metadata mappings.
- Use a `None` default for optional metadata in the Python signature, then materialize a copied empty mapping internally.
- Coerce mapping keys to `FieldLocator` and values to `FieldView` where appropriate.
- Require a mandatory `RecordRef` and reject empty field mappings.
- Validate locator `DataKey` equals `FieldView.field_ref.key`.
- Validate every view field key is present in `record.fields`.
- Implement primitive serialization round trips with no `item_id`, fingerprint, payload, transform, runtime sample, or manifest fields.
- Add unit and contract coverage for different per-field indexes and explicit no-alignment behavior.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` | Verify `IndexItem` constructor, validation, mapping isolation, serialization, and failure cases. | yes |
| `make test-contract` | Verify role-qualified lazy item examples. | yes |
| `make test-package` | Verify public imports and no hidden coupling. | yes |
| `git diff --check` | Patch hygiene. | yes |

### Acceptance Evidence

- Behavior evidence: role-qualified `FieldLocator -> FieldView` items preserve mandatory record provenance and reject inconsistent mappings.
- Design-decision evidence: no `item_id`, fingerprint, runtime sample, payload, transform, training, export, or datasource-index identity is present.
- Example/demo evidence: future supervised item maps `inputs/video.rgb` and `targets/signal.bvp.reference` to different views without constructing a `Sample`.
- Documentation evidence: docstrings state `IndexItem` is pure lazy IO and does not imply cross-field alignment.
- Scientific contract evidence: runtime role is separated from intrinsic field identity, and provenance survives windowing requests.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: expanded because `IndexItem` is the Stage 4 sample-builder input.
- Blocker-resolution budget: return to planning if implementation requires optional record provenance, `item_id`, fingerprints, runtime sample construction, nested/multi-member items, or implicit alignment.
- Pre-submit blocker gate: no runtime `Sample`/`FieldValue` dependency, sample builder, transforms, augmentations, training/export hooks, fingerprints, `item_id`, or manifest behavior.
- Merge record: pending

### Risks And Stop Conditions

- Risks: manual/synthetic examples require verbose record setup; stable item identity pressure may reappear before Stage 5; key-consistency checks may expose gaps in earlier descriptors.
- Stop conditions: `IndexItem` cannot be validated without redefining record provenance, field membership, or item identity.
- Assumptions: Stage 4 consumes `IndexItem` as input and Stage 5 adds stable datasource-index identity externally if needed.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 5: Contract Examples, Docs, And Final Validation Hardening

Status: pending
Slug: `lazy-reference-hardening`
Branch: `agent/stage-3-p5-lazy-reference-hardening`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p5-lazy-reference-hardening`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: prove the complete Stage 3 descriptor graph, public documentation, and coupling exclusions after implementation phases have landed.
- Files/modules owned: `tests/contracts/test_lazy_reference_contract.py` or equivalent; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; public docstrings in Stage 3 modules; `docs/GLOSSARY.md` only if implementation wording must be aligned; final validation evidence.
- Behavior implemented: executable examples for `DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem`, primitive serialization round trips across the graph, and negative checks for forbidden runtime/codec/datasource/workflow coupling.
- Decisions applied: all approved DD-1 through DD-9 plus recorded recommendations DD-10 and DD-11.
- Examples or demos covered: EX-1 through EX-5.
- Out of scope: new Stage 3 behavior beyond defect fixes; real datasets; hardware/network access; heavy optional dependencies; integration/e2e/acceptance tests unless a prior phase expands behavior beyond descriptors.
- Dependencies: P1 through P4.

### Tasks

- Add or finalize contract tests demonstrating EX-1 through EX-5 through public imports only.
- Review public docstrings for descriptor fields, primitive serialization, field-native index semantics, no implicit alignment, provenance/leakage metadata scope, declaration-only schema behavior, and Stage 4/5 deferrals.
- Update `docs/GLOSSARY.md` only if implementation names or wording diverge from existing vocabulary.
- Harden package/import tests for submodules, exact `__all__`, no root exports, no heavy optional imports, and no workflow/artifact packages.
- Run focused and broad validation commands; record any command that cannot run with the reason and residual risk.
- Keep defect fixes scoped to owning modules from P1 through P4 rather than broad refactors.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-package` | Verify public import/export and lightweight import boundaries. | yes |
| `make test-unit` | Verify all Stage 3 unit behavior after hardening fixes. | yes |
| `make test-contract` | Verify lazy-reference public examples and negative coupling checks. | yes |
| `make test` | Verify repository test suite. | yes |
| `make test-summary` | Produce repository test summary evidence. | yes |
| `make validate-pr` | Run repository pre-submit validation. | yes |
| `uv lock --check` | Verify lockfile remains current. | yes |
| `git diff --check` | Patch hygiene. | yes |
| `make test-integration` | Optional unless implementation connects descriptors to Stage 2 runtime behavior beyond contract examples. | no |

### Acceptance Evidence

- Behavior evidence: complete descriptor graph examples pass through public APIs.
- Design-decision evidence: tests/docstrings preserve all exclusions, including no codecs/builders/manifests/runtime samples, no schema-version fields, no fingerprints, no `FieldRef.member`, no `IndexItem.item_id`, and no root exports.
- Example/demo evidence: EX-1 through EX-5 are covered by contract and package tests.
- Documentation evidence: public docstrings and any glossary edits make scientific/workflow semantics inspectable without adding new scope.
- Scientific contract evidence: field-native slicing, non-alignment, provenance, leakage metadata, and declaration-only schema behavior are explicit.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: expanded because this phase records final validation and public contract evidence.
- Blocker-resolution budget: return to planning if final examples require codec loading, sample building, datasource scanning, schema-version fields, fingerprints, stable item identity, seconds/spatial slices, or multi-member items.
- Pre-submit blocker gate: no new behavior beyond defect fixes and documentation/validation hardening.
- Merge record: pending

### Risks And Stop Conditions

- Risks: final contract examples can reveal earlier cross-phase defects; broad validation may expose unrelated failures; docs may accidentally promise Stage 4/5 behavior.
- Stop conditions: executable examples cannot cover approved behavior without adding deferred capabilities.
- Assumptions: implementation phases produce enough public API for examples without real datasets or optional dependencies.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: focused phases require `make test-package`, `make test-unit`, `make test-contract`, and `git diff --check`; P5 requires those plus `make test`, `make test-summary`, `make validate-pr`, and `uv lock --check`.
- Docs/template checks: public docstrings must cover shapes, serialization, no handles/payloads, field-native index semantics, non-alignment, provenance/leakage metadata, declaration-only schema behavior, and deferrals; update `docs/GLOSSARY.md` only if implementation wording diverges.
- Scientific/workflow contract checks: validate no implicit temporal alignment, resampling, padding, seconds/spatial indexing, codec loading, datasource scanning, sample building, transforms, export, training, workflow artifacts, schema-version fields, fingerprints, or stable item identity.
- Example/demo checks: EX-1 through EX-5 must be executable through public imports in unit/contract/package tests by P5.
- Manual review focus: public import compatibility, primitive serialization key spelling, private helper leakage, typed error taxonomy, metadata-only leakage provenance, `ResourceRef.uri` deferral, `IndexItem` purity, and Stage 4/5 handoff boundaries.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Final implementation-plan approval is not yet recorded. | blocker for execution | Maintainer approved this implementation plan by requesting phase execution under `.codex/workflows/roadmap-version-implementation.md` on 2026-05-13. | resolved |
| Public API/error names and primitive serialization keys are compatibility-sensitive. | concern | Keep P1 and P2 narrow, add concrete descriptor errors only with behavior that raises them, require package/unit/contract evidence, and return to planning if approved names or wire shapes need to change. | accepted guardrail |
| Metadata-only leakage provenance is less discoverable than first-class fields. | concern | P3 must document metadata scope, test metadata key coercion, and preserve Stage 5 deferral for richer validation/reporting. | accepted guardrail |
| `IndexItem` identity pressure may reappear before Stage 5. | concern | P4 must keep `record` mandatory and reject `item_id`/fingerprints; return to planning if implementation proves stable identity is required. | accepted guardrail |
| Future index and alignment semantics could be constrained by Stage 3 serialization. | concern | P2 must serialize only supported Stage 3 index types, fail loudly on unknown index tags, and avoid documenting third-party `FieldIndex` serialization extension until a later design approves temporal/seconds/spatial/alignment semantics. | accepted guardrail |
| Stage 5 manifests, fingerprints, canonicalization, and cache keys must wrap descriptors rather than expand them retroactively. | concern | P3 through P5 must keep schema versions, fingerprints, canonical resource identity, stable item identity, cache keys, and manifest envelopes out of Stage 3 descriptor fields; later stages should attach those externally. | accepted guardrail |
| Deferred self-supervised and contrastive workflows must not bend Stage 3 `IndexItem` into a multi-member container. | concern | P4/P5 must keep `IndexItem` single-record and pure lazy IO; wider-window workflows remain expressible through `TemporalIndexSlice` plus later `SampleAugmentation`, while true multi-member behavior requires a later higher-order contract. | accepted guardrail |
| Python signatures must not expose mutable empty defaults. | concern | P2 through P4 should implement optional mapping defaults with `None` and copy into empty mappings internally; planning shorthand like `metadata={}` and `storage_options={}` denotes semantics only. | accepted guardrail |
| `FieldRef.resources` ordering must not become implicit binding policy. | concern | P2 should preserve resource order for round trips but avoid member, selector, priority, canonicalization, or multi-resource binding semantics; Stage 4 codecs and Stage 5 manifests own interpretation and canonicalization. | accepted guardrail |

Gate result:

- Status: passed
- Review evidence: Stage 11 readiness check passed; plan converted accepted P1 through P5 shaping without adding deferred behavior. Post-plan specialist reviews checked public interface simplification and future-roadmap compatibility against Stage 4, Stage 5, later operations/export/training/evaluation/analysis, deferred multi-view workflows, and future index/alignment semantics.
- Accepted risks: compatibility pressure on public import/error names and primitive serialization keys; metadata-only leakage context; single-record `IndexItem` shape; deferred URI interpretation, canonicalization, schema-version envelopes, fingerprints, cache-key identity, expected/observed validation evidence, stable datasource-index item identity, and future seconds/spatial/alignment indexes.
- Revisit triggers: any phase requires codecs/builders/manifests/runtime samples, schema-version fields, fingerprints, stable datasource-index item identity, `FieldRef.member`, `IndexItem.item_id`, root exports, seconds/spatial slices, or multi-member index items.

## Final Approval

- Approval status: approved by maintainer request on 2026-05-13.
- Approved scope: P1 through P5 above.
- Accepted risks: compatibility pressure on public import/error names and primitive serialization keys; metadata-only leakage context; single-record `IndexItem` shape; deferred URI interpretation, canonicalization, schema-version envelopes, fingerprints, cache-key identity, expected/observed validation evidence, stable datasource-index item identity, and future seconds/spatial/alignment indexes.
- Deferred items: codecs/builders/manifests/runtime samples; Stage 3 schema-version fields; descriptor fingerprints; stable datasource-index item identity; `FieldRef.member`; `IndexItem.item_id`; root `rphys` re-exports; seconds/spatial slices; multi-member/nested items; datasource validation reports; expected-versus-observed schema evidence.
