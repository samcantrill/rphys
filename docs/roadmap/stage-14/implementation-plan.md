# Roadmap Stage 14 Implementation Plan

Status: approved by maintainer; Phase 4 prerequisite-gated
Roadmap version: `v14`
Planning document: `docs/roadmap/stage-14/planning.md`
Functionality/design explainer:
`docs/roadmap/stage-14/functionality-behavior-design.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: Phase 1 pending execution
Blockers: Phase 4 is blocked in this checkout until the revised Stage 13
Sample/Batch-native artifact, collection/metric, visualization/report, and
recipe behavior is code-backed and approved.

## Summary

- Goal: harden the public object model with private deterministic synthetic fixtures, contract helpers, integration smoke flows, tier conventions, and package/import checks.
- Source functionality-agreement gate: passed; FQ-14-1 through FQ-14-7 locked.
- Approved behavior: helpers remain private under `tests/support`; fixtures are generated, deterministic, CPU-only, and license-safe; narrow goldens are allowed only for public durable artifact contracts; the full scan-to-report smoke tail is prerequisite-gated on real Stage 13 public APIs and the revised Stage 13 Sample/Batch-native design.
- Source behavior confirmation: passed and locked.
- Key design constraints: no public testing-helper package; no production fixture APIs; no hidden support runner; no fake Stage 13 tail; no real data, network, GPU, workflow runtime, heavy optional dependency, or profiling requirement in default Stage 14 validation.
- Source design-agreement gate: passed; DQ-14-1 through DQ-14-8 locked.
- Source functionality-agreement queue: FQ-14-1 through FQ-14-7 locked in `docs/roadmap/stage-14/planning.md`.
- Source design-agreement queue: DQ-14-1 through DQ-14-8 locked in `docs/roadmap/stage-14/planning.md`.
- Source future-roadmap/reuse safety review: reviewed; Stage 13 Sample/Batch-native alignment, Stage 15, public helper package, real datasource, golden-manifest, and operation/collection reuse findings resolved or deferred with revisit triggers.
- Examples covered: positive fixture catalog, edge-case fixtures, contract assertions, import-boundary checks, narrow golden manifests, upstream smoke slice, and Stage 13-gated scan-to-report tail.
- Source phase shaping: four phases from planning, with Phase 4 prerequisite-gated.
- Source plan quality gate: passed with prerequisite gate; no unresolved or reopened queues.
- Out of scope: public `rphys.testing`, `rphys.fixtures`, or `rphys.datasets`; production placeholder modules; fake Stage 13 behavior; rejected Stage 13 runner/record surfaces; raw datasets; acceptance datasets; workflow runtime; dashboards or plotting backends; performance profiling; broad golden snapshots; Stage 15 optimization.

## Implementation Workflow State

- Implementation-plan quality gate: passed with Phase 4 prerequisite gate
- Review pass: completed by managing agent on 2026-05-17
- Refinement pass: Stage 13 alignment documentation revision completed on
  2026-05-18
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
| 4 | `stage13-scan-to-report-tail` | blocked in this checkout | `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail` | pending | Stage 13-dependent smoke tail, package checks for code-backed Stage 13 exports, final validation evidence | Complete scan-to-report smoke only after revised Stage 13 Sample/Batch-native behavior is code-backed and approved. | `make test-package`, `make test-contract`, `make test-integration`, `make test-e2e` if present, `make test-summary`, `make validate-pr`, `uv lock --check`, `git diff --check` | Full scan-to-report smoke through returned `Batch` fields, uncollation, sample artifact reload, collection/metric operations, and report records/fields |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None for implementation-plan drafting. | Plan quality gate passed with prerequisite gate and was revised on 2026-05-18 for Stage 13 Sample/Batch-native alignment. | Keep the Stage 13-dependent smoke tail as a blocked/prerequisite-gated Phase 4 in checkouts where revised Stage 13 behavior is not code-backed; do not fake Sample/Batch-native artifact, collection/metric, visualization/report, or recipe behavior. | resolved for planning |
| Full scan-to-report tail cannot be implemented in this checkout yet. | FQ-14-3, DD-14-5, plan quality gate, current empty `rphys.prediction`, `rphys.evaluation`, and `rphys.analysis` public exports. | Revised Stage 13 behavior must land, be code-backed, and be approved in the active checkout before Phase 4 starts. | blocked for Phase 4 in this checkout |

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

- Risks: overfreezing public artifacts, asserting private details, growing assertion helpers into a framework, or freezing Stage 13 names before code exists.
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
- Decisions applied: DD-14-5 and DD-14-6, excluding the Stage 13 tail until its prerequisite is met.
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
- Stop conditions: completing the flow requires revised Stage 13 Sample/Batch-native artifact, collection/metric, visualization/report, or recipe contracts that are not code-backed in the active checkout; real data; heavy dependencies; or workflow tooling.
- Assumptions: Stage 5-12 code-backed public surfaces are sufficient for an upstream smoke slice.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Stage 13-Gated Scan-To-Report Tail And Final Validation

Status: blocked in this checkout
Slug: `stage13-scan-to-report-tail`
Branch: `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: complete the roadmap root smoke only when revised Stage 13 behavior is code-backed and approved.
- Files/modules owned: Stage 13-dependent integration/e2e smoke tail, package checks for code-backed Stage 13 public exports, final validation summary artifacts, and any scoped tests/docs required by real public-contract gaps.
- Behavior implemented: real Stage 13 returned-`Batch` field semantics, explicit uncollation, sample artifact export/reload, runtime sample-collection grouping/sorting/stitching, metric-as-operation fields, visualization/report records or report fields, and final scan-to-report smoke evidence.
- Decisions applied: DD-14-5, DD-14-6, DD-14-7, and the prerequisite gate in FQ-14-3.
- Future-roadmap/reuse constraints: Stage 13 owns Sample/Batch-native artifact, collection/metric, visualization/report, and recipe behavior; Stage 14 consumes only public Stage 13 APIs; Stage 15 profiling stays separate.
- Examples or demos covered: full scan-to-report smoke through returned `Batch` fields, uncollation, sample artifact reload, collection/metric operations, and report records/fields.
- Out of scope: private Stage 13 stand-ins, skipped fake tail treated as success, placeholder production modules, broad production refactors, real/acceptance datasets, or rejected Stage 13 public runner/record surfaces.
- Dependencies: Phases 1-3 plus approved, code-backed revised Stage 13 behavior. This checkout still has empty public exports for `rphys.prediction`, `rphys.evaluation`, and `rphys.analysis`, so this phase must not start here until the active tree changes or the Stage 13 implementation lands.

### Tasks

- Recheck Stage 13 implementation and approval status before opening the phase.
- Verify revised Stage 13 Sample/Batch-native behavior is code-backed; if not, keep the phase blocked in that checkout.
- Extend the upstream smoke through real Stage 13 public APIs only.
- Refresh package/import checks for code-backed Stage 13 exports without freezing placeholders.
- Capture final validation summaries and residual risks.
- Route any production change as a scoped Stage 13/public-contract fix with tests/docs; do not implement Stage 13 behavior inside Stage 14 tests.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| Stage 13 public-contract prerequisite check | Confirm revised Stage 13 behavior is code-backed and approved in the active checkout, including returned-`Batch` field semantics, uncollation, sample artifact reload, collection/metric operations, and report records/fields where exported. | yes |
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
- Design-decision evidence: no fake tail, placeholders, or private Stage 13 stand-ins are present.
- Future-roadmap/reuse evidence: Stage 13 remains the contract owner and Stage 15 profiling remains deferred.
- Example/demo evidence: full root synthetic smoke example is executable and validated.
- Documentation evidence: final validation notes record prerequisite satisfaction and accepted risks.
- Scientific contract evidence: returned prediction fields, uncollation policy, sample artifact reload, collection/metric operations, visualization/report records or fields, provenance, and failure semantics are preserved.

### Phase Workflow State

- Phase execution plan: pending until prerequisite clears in the active checkout
- Planning/refinement budget: hold until revised Stage 13 behavior lands, then 1 planner/reviewer cycle
- Implementation/refinement budget: 1 implementation pass plus scoped prerequisite refinements
- PR review budget: full smoke-tail and package-boundary review
- Blocker-resolution budget: prerequisite only; no fake substitute
- Pre-submit blocker gate: revised Stage 13 public behavior must be code-backed and approved
- Merge record: pending

### Risks And Stop Conditions

- Risks: accidental fake completion, freezing placeholder Stage 13 exports, reintroducing rejected Stage 13 runner/record surfaces, or broad production refactors under a test-hardening phase.
- Stop conditions: revised Stage 13 behavior remains absent, unapproved, or ambiguous in the active checkout; full tail requires private stand-ins; implementation requires real datasets or heavy optional dependencies.
- Assumptions: Stage 13 defines the Sample/Batch-native artifact, collection/metric, visualization/report, and recipe behavior consumed by the final tail.

### Completion Summary

- Implementation: blocked in this checkout pending revised Stage 13 code-backed behavior
- Validation: blocked in this checkout pending revised Stage 13 code-backed behavior
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: `make test-package`, `make test-contract`, `make test-integration`, `make test-summary`, `make validate-pr`, `uv lock --check`, and `git diff --check`; add `make test` and `make test-e2e` when the touched surface enters those suites.
- Docs/template checks: update `tests/README.md`, support docstrings, and phase validation summaries only when implementation touches support behavior, tier semantics, or prerequisite state.
- Scientific/workflow contract checks: verify deterministic fixture provenance, field roles, sample rates, timestamps, alignment evidence, fail-loud edge behavior, public loader/materialization use, and absence of real-data/network/GPU/heavy-dependency/workflow requirements.
- Example/demo checks: positive catalog, edge variants, contract assertions, import-boundary checks, golden manifests, upstream smoke slice, and final Stage 13-aligned scan-to-report tail when unblocked.
- Manual review focus: support privacy, no public helper package, no fake Stage 13 behavior, no support-level runner, no broad goldens, no unplanned production changes.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Phase 4 is blocked in this checkout until revised Stage 13 behavior is code-backed and approved. | blocker for Phase 4 only | Keep Phase 4 blocked and prerequisite-gated in checkouts where Stage 13 has not landed; earlier phases may proceed without pretending the report tail is complete. | accepted |
| Stage 14 production changes are not planned. | concern | If tests expose a real public-contract gap, route it as a scoped fix with tests/docs or a follow-up decision. | accepted |
| Private helpers could grow into a hidden framework. | concern | Review support helpers with first consuming tests and reject unused runners/registries. | accepted |

Gate result:

- Status: approved by maintainer with Phase 4 blocked in this checkout.
- Review evidence: this plan is derived from the passed Stage 14 plan quality gate, preserves the Stage 13 prerequisite gate, and uses roadmap-compliant branch/worktree slugs.
- Accepted risks: Stage 14 can start test-support and upstream smoke hardening before the Stage 13 tail is code-backed in a checkout, provided Phase 4 remains blocked there.
- Revisit triggers: Stage 13 implementation lands; `docs/roadmap.md` changes Stage 14 or Stage 13 scope; public testing-helper package is requested; smoke requires real data/heavy dependencies/workflow tooling; tests expose a real public-contract ambiguity.

## Final Approval

- Approval status: approved by maintainer on 2026-05-17.
- Approved scope: Phases 1-3 are approved for implementation; Phase 4 is conditionally scoped but blocked in this checkout until revised Stage 13 behavior is code-backed and approved.
- Accepted risks: Phase 4 prerequisite gating is accepted.
- Deferred items: public testing-helper package, real datasource smoke, acceptance dataset checks, Stage 15 profiling/data-path optimization, broad golden snapshots, and the Stage 13-dependent smoke tail until revised code-backed Stage 13 behavior exists in the active checkout.
