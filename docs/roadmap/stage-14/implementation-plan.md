# Roadmap Stage 14 Implementation Plan

Status: design-reviewed and approved for implementation; Stage 13 dependency
satisfied by plan
Roadmap version: `v14`
Planning document: `docs/roadmap/stage-14/planning.md`
Functionality/design explainer:
`docs/roadmap/stage-14/functionality-behavior-design.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 1 pending execution
Blockers: none for Stage 14 planning. Phase 4 must run on a branch that
contains the completed Stage 13 implementation outputs from PRs #85-#90.

## Summary

- Goal: harden the public object model with private deterministic synthetic fixtures, contract helpers, integration smoke flows, tier conventions, and package/import checks.
- Source functionality-agreement gate: passed; FQ-14-1 through FQ-14-7 locked.
- Approved behavior: helpers remain private under `tests/support`; fixtures are generated, deterministic, CPU-only, and license-safe; narrow goldens are allowed only for public durable artifact contracts; the full scan-to-report smoke tail consumes the completed Stage 13 Sample/Batch-native design.
- Source behavior confirmation: passed and locked.
- Key design constraints: no public testing-helper package; no production fixture APIs; no hidden support runner; no fake Stage 13 tail; no real data, network, GPU, workflow runtime, heavy optional dependency, or profiling requirement in default Stage 14 validation.
- Source design-agreement gate: passed; DQ-14-1 through DQ-14-8 locked.
- Source functionality-agreement queue: FQ-14-1 through FQ-14-7 locked in `docs/roadmap/stage-14/planning.md`.
- Source design-agreement queue: DQ-14-1 through DQ-14-8 locked in `docs/roadmap/stage-14/planning.md`.
- Source future-roadmap/reuse safety review: reviewed; Stage 13 Sample/Batch-native alignment, Stage 15, public helper package, real datasource, golden-manifest, and operation/collection reuse findings resolved or deferred with revisit triggers.
- Examples covered: positive fixture catalog, edge-case fixtures, contract assertions, import-boundary checks, narrow golden manifests, upstream smoke slice, and Stage 13-gated scan-to-report tail.
- Source phase shaping: four phases from planning; Phase 4 is now pending after the Stage 13 implementation plan was marked complete with all phases merged.
- Source plan quality gate: passed with the Stage 13 dependency satisfied by `docs/roadmap/stage-13/implementation-plan.md`; no unresolved or reopened queues.
- Out of scope: public `rphys.testing`, `rphys.fixtures`, or `rphys.datasets`; production placeholder modules; fake Stage 13 behavior; rejected Stage 13 runner/record surfaces; raw datasets; acceptance datasets; workflow runtime; dashboards or plotting backends; performance profiling; broad golden snapshots; Stage 15 optimization.

## Implementation Workflow State

- Implementation-plan quality gate: passed; Stage 13 dependency refreshed
  against the complete Stage 13 implementation plan
- Review pass: completed by managing agent on 2026-05-17
- Refinement pass: Stage 13 alignment and implementation-plan recheck completed
  on 2026-05-18
- Design review: passed by managing agent on 2026-05-18
- Confirmation review: completed by maintainer approval on 2026-05-17
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `private-synthetic-catalog-governance` | pending | `agent/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance` | pending | `tests/support`, first consuming tests, concise support governance docs | Establish private fixture catalog, edge variants, deterministic payload evidence, URI refs, optional fields, and helper privacy governance. | Focused support-consuming tests, `make test-package`, `git diff --check` | Positive catalog and edge fixture examples |
| 2 | `contract-boundaries-goldens` | pending | `agent/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens` | pending | `tests/support` assertion helpers, `tests/contracts`, `tests/package`, targeted integration/golden tests | Turn fixtures into reusable public-object invariants, package/import guardrails, and narrow durable-manifest goldens. | `make test-contract`, `make test-package`, targeted integration checks, `git diff --check` | Contract assertion, import-boundary, and golden manifest examples |
| 3 | `upstream-smoke-validation-tiers` | pending | `agent/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers` | pending | Integration/e2e smoke slice, tier docs/markers, existing Stage 5-12 flow composition | Compose code-backed Stage 5-12 surfaces through one public loader/materialization path and record debug/smoke/signal tier semantics. | `make test-integration`, `make test` if default smoke remains cheap, `make test-e2e` if introduced, `git diff --check` | Upstream root-smoke slice before Stage 13 tail |
| 4 | `stage13-scan-to-report-tail` | pending after Phases 1-3 | `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail` | pending | Stage 13-dependent smoke tail, package checks for code-backed Stage 13 exports, final validation evidence | Complete scan-to-report smoke over the completed Stage 13 Sample/Batch-native behavior. | `make test-package`, `make test-contract`, `make test-integration`, `make test-e2e` if present, `make test-summary`, `make validate-pr`, `uv lock --check`, `git diff --check` | Full scan-to-report smoke through returned `Batch` fields, uncollation, sample artifact reload, collection/metric operations, and report records/fields |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None for implementation-plan drafting. | Plan quality gate passed and was revised on 2026-05-18 against the complete Stage 13 implementation plan. | Treat Stage 13 as complete for roadmap planning; require normal implementation preflight to ensure the Phase 4 branch contains the merged Stage 13 outputs. | resolved |

## Stage 13 Implementation-Plan Recheck

Rechecked on 2026-05-18 against `docs/roadmap/stage-13/implementation-plan.md`.
The Stage 13 implementation plan is the authoritative roadmap artifact for
Stage 14 sequencing. It is marked `Status: complete`, `Current phase: complete
- all phases merged`, and `Blockers: none`. All six Stage 13 phase PRs are
recorded as merged.

| Area | Stage 13 implementation-plan evidence | Phase 4 impact |
| --- | --- | --- |
| Overall status | Stage 13 `Status: complete`; all phases merged; no blockers. | Phase 4 is ordered after Stage 14 Phases 1-3 and starts with a merge/preflight check. |
| Phase 2 | PR #86 merged; removes `MethodOutput`/method-output adapters and `StepOutput`; `Method.predict` and `Learner.step` return `Batch`; training uses plan-owned `TrainingOutputSpec` or equivalent. | Phase 4 should exercise returned-`Batch` fields and must not reintroduce method-output or step-output compatibility surfaces. |
| Phase 3 | PR #87 merged; implements explicit returned-batch uncollation, per-sample artifact export/reload, source `RecordRef`/descriptor evidence, and a narrow multi-record export helper over existing export/save. | Phase 4 should include sample artifact export/reload through normal datasource/index/sample-source behavior. |
| Phase 4 | PR #88 merged; implements runtime sample-collection grouping/sorting/stitching and metric-as-sample/collection operation adapters; public metric observation/result surfaces are removed or made private migration details. | Phase 4 should use field-native metric operation outputs, not `MetricObservation*` or public evaluator-runner surfaces. |
| Phase 5 | PR #89 merged; implements dependency-light visualization/report operation-compatible builders, in-memory report/table/diagnostic renderer records, and report fields/records without public analysis operation/result families. | Phase 4 can complete report evidence through report records/fields while keeping report writers and plotting/dataframe dependencies out of scope. |
| Phase 6 | PR #90 merged; final synthetic examples, docs, package export review, and validation completed. | Phase 4 should harden the Stage 13 synthetic composition rather than expand Stage 13 core behavior. |
| Implementation preflight | Stage 13 plan records merge commits for PRs #85-#90. | Before executing Phase 4, ensure the phase worktree is based on the `develop` state that contains those merged outputs; if the local checkout is stale, sync before opening the phase. |

## Phase 1: Private Synthetic Catalog And Governance

Status: pending
Slug: `private-synthetic-catalog-governance`
Branch: `agent/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the reusable private fixture base and edge-variant vocabulary without adding public APIs.
- Files/modules owned: `tests/support/*`, first consuming tests under `tests/contracts` or `tests/integration`, and concise updates to `tests/README.md` or support docstrings if needed.
- Behavior implemented: generated deterministic positive scenarios for multiple datasources, records, subjects, groups, stable split/group metadata, URI `ResourceRef`s, deterministic video-like fields, waveform fields, timestamp metadata, optional fields, tiny manifest-ready descriptors, and named edge variants with expected failure evidence.
- Decisions applied: DD-14-1, DD-14-2, DD-14-3, DD-14-9, DD-14-10.
- Future-roadmap/reuse constraints: helper modules remain private and refactorable; no public fixture package; no dataset-specific policy; no real datasource shortcuts; no Stage 13 placeholders.
- Examples or demos covered: positive fixture catalog and edge fixture contract examples.
- Out of scope: production modules, `rphys.testing`, `rphys.fixtures`, `rphys.datasets`, broad golden snapshots, real raw data, workflow/runtime code, Stage 13 tail behavior.
- Dependencies: existing `tests/support/synthetic_datasources.py`, `tests/support/lazy_sample_builder_fixtures.py`, `tests/support/synthetic_codecs.py`, `tests/support/__init__.py`, `tests/README.md`, and locked FQ-14-1/FQ-14-2/FQ-14-7.

### Tasks

- Inventory existing support helpers and preserve or deliberately update consuming tests together with helper changes.
- Add private catalog helpers for deterministic field-role-oriented scenarios rather than dataset-specific shortcuts.
- Add edge-variant helpers that record affected field, sample-rate/timestamp/alignment evidence, and expected failure family.
- Keep concrete imports from support modules; leave `tests/support/__init__.py` empty or minimal unless a narrow reviewed need appears.
- Add first consuming tests that prove the helpers construct real public `rphys` objects and expose provenance.
- Document support privacy, determinism, and no-public-API expectations only where implementation touches the support surface.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Focused `uv run pytest ...` for first consuming tests | Prove catalog and edge helpers work through public-path consumers. | yes |
| `make test-package` | Confirm no public fixture package, root re-export, heavy import, or production `tests.support` leakage. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: consuming tests construct multiple datasource/record/subject/group scenarios and representative edge variants.
- Design-decision evidence: helpers live only under `tests/support`; no production source imports test support; concrete support modules remain private.
- Future-roadmap/reuse evidence: scenarios are field-role oriented and descriptor-based, not real-dataset adapters or downstream APIs.
- Example/demo evidence: positive catalog and negative variant examples are exercised by tests.
- Documentation evidence: support privacy and determinism are visible in touched support docs/docstrings.
- Scientific contract evidence: waveform, timestamp, sample-rate, alignment, missing/short/flat/NaN/inf, and invalid-rate evidence is inspectable.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped refinements
- PR review budget: 1 focused support/test review
- Blocker-resolution budget: escalate only real public-contract gaps; do not add placeholder production code
- Pre-submit blocker gate: no public helper package, no Stage 13 placeholders, no unused helper framework
- Merge record: pending

### Risks And Stop Conditions

- Risks: helper sprawl, hidden fixture policy, dataset-specific shortcuts, or support code not used by public-path tests.
- Stop conditions: catalog requires a public API decision, real data, production fixtures, or fake Stage 13 behavior.
- Assumptions: generated deterministic fixtures can cover the required catalog without broad checked-in artifacts.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 2: Contract Boundaries And Durable Goldens

Status: pending
Slug: `contract-boundaries-goldens`
Branch: `agent/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: convert the fixture base into reusable executable public-object invariants and import-boundary checks.
- Files/modules owned: private assertion helpers under `tests/support`, contract tests under `tests/contracts`, package/import tests under `tests/package`, targeted integration tests, and narrow golden fixture files only where public durable artifact contracts require them.
- Behavior implemented: focused assertions for selectors, refs/manifests, field refs/views, sample builders, operation replay, save/export/derived datasource round trips, cache determinism/invalidation, sample source/prepared data/batch-cost metadata, and Method/Loss/Objective/Metric/Learner/Trainer boundaries.
- Decisions applied: DD-14-4, DD-14-7, DD-14-8, with DD-14-1 guardrails.
- Future-roadmap/reuse constraints: assertions remain boundary-specific and private; public helper extraction remains deferred; future artifact schemas get separate approved goldens.
- Examples or demos covered: contract assertion, import-boundary, and golden manifest examples.
- Out of scope: broad scenario runner, helper registry, private implementation snapshots, placeholder public exports, optional-heavy checks that require installing extra stacks.
- Dependencies: Phase 1, existing contract/package tests, Stage 5/8 manifest/export evidence, locked FQ-14-4/FQ-14-6/FQ-14-7.

### Tasks

- Add or consolidate small private assertion helpers only where repeated public-object invariants justify them.
- Add consuming contract/integration tests that keep public construction visible and use helpers for repeated checks.
- Harden package/import checks for code-backed exports and forbidden absences, including no `rphys.testing`, no public helper leakage, no root convenience exports, and no heavy optional imports.
- Add narrow golden manifest/fingerprint examples only for durable public artifact contracts, omitting loaded arrays, open handles, and private helper internals.
- Route any uncovered real public-contract gap as a scoped fix or follow-up; do not pre-plan production changes.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-contract` | Validate public-object invariants and narrow durable artifact contracts. | yes |
| `make test-package` | Validate public API/import boundaries and forbidden package absences. | yes |
| Targeted `make test-integration` or `uv run pytest ...` | Validate round-trip contracts that require integration evidence. | yes, where touched |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: public invariant failures identify the owning boundary clearly.
- Design-decision evidence: assertion helpers are private, small, and not a scenario runner.
- Future-roadmap/reuse evidence: package checks keep future public helper extraction behind a separate roadmap decision.
- Example/demo evidence: selector/ref/manifest/field/sample/operation/export/cache/model-boundary examples are covered.
- Documentation evidence: any touched support docs preserve private-helper governance.
- Scientific contract evidence: serialized evidence preserves public fields, schema, fingerprints, provenance, and no-loaded-payload constraints.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped boundary fixes
- PR review budget: review by contract family
- Blocker-resolution budget: production changes only for real public-contract gaps with tests/docs
- Pre-submit blocker gate: no private snapshots, no broad runner, no placeholder exports
- Merge record: pending

### Risks And Stop Conditions

- Risks: overfreezing public artifacts, asserting private details, growing assertion helpers into a framework, or freezing names that are not present in the real public package surface.
- Stop conditions: validation requires broad production refactor, public helper API, or fake Stage 13 contracts.
- Assumptions: current public contracts can be hardened through tests and private helpers without new production surfaces.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 3: Upstream Synthetic Smoke And Validation Tiers

Status: pending
Slug: `upstream-smoke-validation-tiers`
Branch: `agent/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: compose code-backed Stage 5-12 surfaces through a root-smoke upstream slice using one public loader/materialization path.
- Files/modules owned: integration or e2e smoke tests, already-proven private smoke assembly helpers, validation-tier docs/markers/target notes where needed, and existing Stage 5/8/9/10/12 integration-flow consumers.
- Behavior implemented: synthetic scan, filter/group/split, index manifest, lazy `SampleBuilder`, `SampleOperationPipeline`, `BatchCollater`, trivial public `Method` or learner slice, and export/reload where code-backed before the Stage 13 tail.
- Decisions applied: DD-14-5 and DD-14-6, with the Stage 13 tail reserved for Phase 4.
- Future-roadmap/reuse constraints: Stage 15 may profile this shape later but must not change semantics; tiers are validation groupings only; no workflow runtime ownership.
- Examples or demos covered: upstream root-smoke slice and debug/smoke/signal tier semantics.
- Out of scope: claiming scan-to-report completion, fake Stage 13 tail, alternate smoke loader, workflow tooling, network/GPU/real-data requirements, performance profiling.
- Dependencies: Phases 1-2, existing Stage 5/8/9/10/12 integration flows, DD-14-5/DD-14-6, and code-backed public APIs through Stage 12.

### Tasks

- Compose one reviewable upstream smoke flow through public APIs and private fixtures already validated in Phases 1-2.
- Label the upstream smoke explicitly incomplete before the Stage 13 tail.
- Ensure debug, smoke, and signal tiers differ only by breadth/cost and use the same public loader/materialization path.
- Keep default smoke local, CPU-only, deterministic, and free of external data, network, GPU, heavy optional dependencies, workflow tooling, and private project code.
- Add validation notes or suite placement guidance where tests introduce or rely on tier semantics.
- Route only real public-contract gaps as scoped fixes; do not add production placeholders.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-integration` | Validate the upstream synthetic smoke composition through public APIs. | yes |
| `make test` | Confirm default smoke remains cheap enough for ordinary local validation, if included in default suite. | yes, if default suite is touched |
| `make test-e2e` | Validate e2e placement, if an e2e suite is introduced for the upstream smoke. | yes, if introduced |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: upstream smoke passes through scan/filter/split/index/sample/operation/batch/method/export surfaces without alternate loaders.
- Design-decision evidence: the flow is explicitly incomplete before Stage 13 and does not claim scan-to-report coverage.
- Future-roadmap/reuse evidence: tier semantics are validation-only and compatible with later Stage 15 profiling.
- Example/demo evidence: root-smoke upstream example is covered by an integration/e2e test.
- Documentation evidence: suite/marker/target guidance is updated only where needed.
- Scientific contract evidence: loader/materialization, sampling, field roles, provenance, and metric-view assumptions stay explicit.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped refinements
- PR review budget: integration-flow review
- Blocker-resolution budget: stop before Stage 13 tail if contracts are absent
- Pre-submit blocker gate: no fake Stage 13 tail, no alternate loader, no workflow runtime
- Merge record: pending

### Risks And Stop Conditions

- Risks: smoke grows too broad, brittle, slow, or accidentally claims full scan-to-report completion.
- Stop conditions: completing the upstream slice would require implementing the
  Stage 13 tail inside Phase 3, real data, heavy dependencies, or workflow
  tooling.
- Assumptions: Stage 5-12 code-backed public surfaces are sufficient for an upstream smoke slice.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Stage 13-Gated Scan-To-Report Tail And Final Validation

Status: pending after Phases 1-3
Slug: `stage13-scan-to-report-tail`
Branch: `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: complete the roadmap root smoke over the completed Stage 13
  Sample/Batch-native behavior.
- Files/modules owned: Stage 13-dependent integration/e2e smoke tail, package checks for code-backed Stage 13 public exports, final validation summary artifacts, and any scoped tests/docs required by real public-contract gaps.
- Behavior implemented: real Stage 13 returned-`Batch` field semantics, explicit uncollation, sample artifact export/reload, runtime sample-collection grouping/sorting/stitching, metric-as-operation fields, visualization/report records or report fields, and final scan-to-report smoke evidence.
- Decisions applied: DD-14-5, DD-14-6, DD-14-7, and the Stage 13
  merge/preflight check in FQ-14-3.
- Future-roadmap/reuse constraints: Stage 13 owns Sample/Batch-native artifact, collection/metric, visualization/report, and recipe behavior; Stage 14 consumes only public Stage 13 APIs; Stage 15 profiling stays separate.
- Examples or demos covered: full scan-to-report smoke through returned `Batch` fields, uncollation, sample artifact reload, collection/metric operations, and report records/fields.
- Out of scope: private Stage 13 stand-ins, skipped fake tail treated as success, placeholder production modules, broad production refactors, real/acceptance datasets, or rejected Stage 13 public runner/record surfaces.
- Dependencies: Phases 1-3 plus the completed Stage 13 implementation plan.
  Phase 4 execution must use a worktree based on the `develop` state containing
  Stage 13 PRs #85-#90, because the smoke tail consumes those merged public
  contracts rather than recreating them.

### Tasks

- Before opening the phase, verify the worktree includes the merged Stage 13
  outputs recorded in `docs/roadmap/stage-13/implementation-plan.md`, especially
  PRs #85-#90.
- Exercise `Method.predict` and learner step behavior as ordinary returned
  `Batch` values, with no method-output or step-output compatibility shims.
- Exercise sample artifact handoff: predicted/test/evaluation fields are
  explicitly uncollated to per-sample artifacts, exported through existing
  export/save and derived datasource behavior, and reloaded through generic
  datasource/sample paths.
- Exercise metric/evaluation-like behavior through ordinary fields and
  collection/metric operations rather than public `MetricObservation*`,
  `MetricResult`, or evaluator-runner surfaces.
- Exercise analysis/report behavior through dependency-light report records,
  report fields, visualization descriptors, or recipe examples, with no
  plotting/dataframe/file-writer dependency in core imports.
- Extend the upstream smoke through real Stage 13 public APIs only.
- Refresh package/import checks for code-backed Stage 13 exports without freezing placeholders.
- Capture final validation summaries and residual risks.
- Route any production change as a scoped Stage 13/public-contract fix with tests/docs; do not implement Stage 13 behavior inside Stage 14 tests.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Stage 13 merge/preflight check | Confirm the Phase 4 worktree includes the completed Stage 13 outputs recorded in `docs/roadmap/stage-13/implementation-plan.md`, including PRs #85-#90. | yes |
| Legacy-surface absence check | Confirm old public `MethodOutput*`, `apply_method_output`, `StepOutput`, `StepPrediction`, `MetricObservation*`, `MetricResult`, and evaluator/runner-style names remain absent from public exports. | yes |
| `make test-package` | Validate code-backed imports and forbidden package/import absences. | yes |
| `make test-contract` | Validate Stage 14 contract hardening plus Stage 13 public-contract consumers. | yes |
| `make test-integration` | Validate scan-to-report smoke or its integration placement. | yes |
| `make test-e2e` | Validate e2e smoke if the full tail lives there. | yes, if present |
| `make test-summary` | Produce validation summary evidence. | yes |
| `make validate-pr` | Run full PR validation for the completed Stage 14 scope. | yes |
| `uv lock --check` | Confirm dependency lock consistency. | yes |
| `git diff --check` | Catch whitespace/formatting issues. | yes |

### Acceptance Evidence

- Behavior evidence: complete scan-to-report flow uses real Stage 13 public APIs and public loader/materialization paths.
- Design-decision evidence: no fake tail, placeholders, private Stage 13
  stand-ins, or unapproved legacy public surfaces are present.
- Future-roadmap/reuse evidence: Stage 13 remains the contract owner and Stage 15 profiling remains deferred.
- Example/demo evidence: full root synthetic smoke example is executable and validated.
- Documentation evidence: final validation notes record Stage 13 merge/preflight evidence and accepted risks.
- Scientific contract evidence: returned prediction fields, uncollation policy, sample artifact reload, collection/metric operations, visualization/report records or fields, provenance, and failure semantics are preserved.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped preflight refinements
- PR review budget: full smoke-tail and package-boundary review
- Blocker-resolution budget: sync/stale-branch issues only; no fake substitute
- Pre-submit blocker gate: worktree includes completed Stage 13 outputs and
  keeps rejected Stage 13 surfaces absent
- Merge record: pending

### Risks And Stop Conditions

- Risks: accidental fake completion, stale phase worktree missing Stage 13
  merges, building on old public method/learner/metric observation surfaces, or
  broad production refactors under a test-hardening phase.
- Stop conditions: the phase worktree does not contain the completed Stage 13
  outputs; full tail requires private stand-ins; implementation relies on
  `MethodOutput*`, `StepOutput`, `MetricObservation*`, `MetricResult`, or
  evaluator/runner surfaces; implementation requires real datasets or heavy
  optional dependencies.
- Assumptions: Stage 13 defines the Sample/Batch-native artifact, collection/metric, visualization/report, and recipe behavior consumed by the final tail.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: `make test-package`, `make test-contract`, `make test-integration`, `make test-summary`, `make validate-pr`, `uv lock --check`, and `git diff --check`; add `make test` and `make test-e2e` when the touched surface enters those suites.
- Docs/template checks: update `tests/README.md`, support docstrings, and phase validation summaries only when implementation touches support behavior, tier semantics, or Stage 13 dependency state.
- Scientific/workflow contract checks: verify deterministic fixture provenance, field roles, sample rates, timestamps, alignment evidence, fail-loud edge behavior, public loader/materialization use, and absence of real-data/network/GPU/heavy-dependency/workflow requirements.
- Example/demo checks: positive catalog, edge variants, contract assertions, import-boundary checks, golden manifests, upstream smoke slice, and final Stage 13-aligned scan-to-report tail.
- Manual review focus: support privacy, no public helper package, no fake Stage 13 behavior, no support-level runner, no broad goldens, no unplanned production changes.
- Continuous behavior-validation checks: every concrete fixture, datasource,
  public object, operation, metric/report example, or smoke segment added during
  a phase should include deterministic expected facts, failure behavior,
  provenance evidence, and suite placement. Do not rely on the final smoke path
  as the only proof for a newly introduced example.

| Surface | Required behavior evidence | Typical suite |
| --- | --- | --- |
| Data objects and fields | Identity, field roles, metadata, temporal slices, sample rate, timestamps, alignment, dtype/shape, optional masks/quality fields, serialization boundaries. | `tests/contracts`, targeted unit tests |
| Datasources, refs, indexes, and manifests | Scan output, record/sample refs, URI refs, lazy materialization, no loaded arrays/open handles in durable metadata, cache keys, derived datasource reload, invalid descriptor failures. | `tests/contracts`, `tests/integration` |
| Sample builders and materialization | Probe/build subset behavior, field selection, missing-field diagnostics, temporal slice handling, provenance, cache determinism. | `tests/contracts`, `tests/integration` |
| Operations and pipelines | Input/output field contracts, deterministic replay, stochastic replay evidence where applicable, parameter provenance, dtype/shape behavior, failure diagnostics, pipeline composition. | `tests/contracts`, `tests/integration` |
| Methods, learners, losses, objectives, and metrics | Public boundary behavior, returned `Batch` fields where applicable, target exclusion/pass-through policy, metric field outputs, invalid input diagnostics. | `tests/contracts`, `tests/unit`, `tests/integration` |
| Export, save, artifact reload, and reports | Manifest/fingerprint stability where public, explicit uncollation, sample-granular artifacts, derived datasource reload, report records/fields, no plotting/dataframe/file-writer dependency in core paths. | `tests/contracts`, `tests/integration`, optional `tests/e2e` |

## Design Review Approval

Reviewed on 2026-05-18 against `docs/roadmap.md` Milestone 14,
`docs/roadmap/stage-14/planning.md`,
`docs/roadmap/stage-14/functionality-behavior-design.md`, and the complete
Stage 13 implementation plan.

| Check | Result | Evidence | Approval note |
| --- | --- | --- | --- |
| Roadmap scope | pass | Phases cover private synthetic fixtures, contract helpers, integration/smoke flow, validation tiers, and public API/import checks. | No production fixture package, real datasource work, profiling, workflow runtime, or broad golden snapshot scope is introduced. |
| Stage 13 dependency handling | pass | Phase 4 consumes completed Stage 13 PRs #85-#90 through a merge/preflight check. | The plan does not recreate Stage 13 behavior in tests or depend on rejected runner/record surfaces. |
| Public API and import boundaries | pass | Package checks are required in Phases 1, 2, and 4; `rphys.testing`, `rphys.fixtures`, placeholder exports, root convenience exports, and heavy optional imports stay forbidden. | Public surface hardening is tied to code-backed names only. |
| Private support design | pass | Helpers remain under `tests/support`, are validated through first consuming tests, and cannot become a public helper framework. | Phase 1 and Phase 2 ownership keeps helper growth reviewable. |
| Scientific contract coverage | pass | Fixtures and validation require sample rates, timestamps, alignment, waveform evidence, edge variants, provenance, uncollation, artifact reload, metric fields, and report records. | Failure behavior remains explicit and inspectable. |
| Phase shape and reviewability | pass | Four sequential phases separate fixture governance, contract/package/golden hardening, upstream smoke/tier semantics, and Stage 13 scan-to-report completion. | Each phase has owned files, stop conditions, acceptance evidence, and validation commands. |
| Future-roadmap safety | pass | Stage 15 profiling, public helper extraction, real datasource smoke, acceptance datasets, and report writers remain deferred with revisit triggers. | Stage 14 hardens correctness without pulling later roadmap work forward. |

Design review findings:

- Blocking findings: none.
- Non-blocking watch items: keep Phase 1 helpers paired with consuming tests;
  keep Phase 2 goldens limited to durable public manifests/fingerprints; require
  Phase 4 preflight and legacy-surface absence checks before claiming the full
  scan-to-report smoke.
- Approval decision: approved for implementation workflow execution, starting
  with Phase 1.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Stage 13 dependency is satisfied by the completed Stage 13 implementation plan, but Phase 4 must run on a worktree containing those merged outputs. | preflight requirement | Require a Stage 13 merge/preflight check before Phase 4 execution; do not rebuild or fake Stage 13 behavior inside Stage 14. | accepted |
| Stage 14 production changes are not planned. | concern | If tests expose a real public-contract gap, route it as a scoped fix with tests/docs or a follow-up decision. | accepted |
| Private helpers could grow into a hidden framework. | concern | Review support helpers with first consuming tests and reject unused runners/registries. | accepted |

Gate result:

- Status: approved by maintainer and passed design review, with Stage 13
  dependency refreshed as satisfied by the completed Stage 13 implementation
  plan.
- Review evidence: this plan is derived from the passed Stage 14 plan quality
  gate, the complete Stage 13 implementation plan, and roadmap-compliant
  branch/worktree slugs.
- Accepted risks: Phase 4 still needs a branch/preflight check to ensure the
  phase worktree contains the Stage 13 PR #85-#90 outputs.
- Revisit triggers: `docs/roadmap.md` changes Stage 14 or Stage 13 scope; public testing-helper package is requested; smoke requires real data/heavy dependencies/workflow tooling; tests expose a real public-contract ambiguity; the Phase 4 worktree does not contain the completed Stage 13 outputs.

## Final Approval

- Approval status: approved by maintainer on 2026-05-17 and approved by
  managing-agent design review on 2026-05-18.
- Approved scope: Phases 1-4 are scoped for implementation in order; Phase 4
  consumes the completed Stage 13 outputs after Phases 1-3 and branch preflight.
- Accepted risks: Phase 4 depends on the Stage 13 merged outputs and must fail
  preflight on a stale worktree.
- Deferred items: public testing-helper package, real datasource smoke,
  acceptance dataset checks, Stage 15 profiling/data-path optimization, and
  broad golden snapshots.
