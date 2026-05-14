# Phase 2 Execution Plan: Specs, Adapters, Scan Results, And Validation Reports

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: datasource scan specs, structural adapters, validation reports, and IO policy
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Specs, Adapters, Scan Results, And Validation Reports
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 2: Specs, Adapters, Scan Results, And Validation Reports`
- Branch: `agent/stage-5-p2-adapters-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p2-adapters-validation`
- Phase execution plan path: `docs/roadmap/stage-5/phases/adapters-validation.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 2 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path due public API and validation-report shape
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path review; no implementation refinement required after validation passed
- Setup limitations: no subagent delegation was used in this session
- Blockers: none

## Objective

Implement descriptor-only datasource scan specs, structural adapter behavior, primitive scan results, validation issues/reports, and explicit validation IO policy without adding registries, view/filter coupling, or hidden payload loading.

## Full-Plan Context

Phase 2 is the discovery and validation foundation consumed by later Stage 5 phases. Views, filters, candidates, groups, splits, indexes, manifests, and composite indexes remain out of scope and must remain additive in later phase PRs.

## Source Phase Summary

- Goal: implement discovery and validation entrypoints over descriptor refs.
- Required scope: `DataSourceSpec`, structural `DataSourceAdapter`, `DataSourceScanResult`, `ValidationIssue`, `DataSourceValidationReport`, `ValidationIOPolicy`, private synthetic adapter fixture, and scan/validation tests.
- Required checkpoints: scan result independent from `DataSourceView`, no adapter registry, no real SDK dependency, and explicit IO policy guardrails.
- Acceptance criteria: synthetic scan emits descriptor refs, primitive scan metadata, validation evidence, warnings, and rejections; validation reports preserve issue context and reject hidden IO.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: Phase 1 established empty Stage 5 submodules with no parent exports.
- Existing tests or harness behavior: package tests protect root/parent exports and heavy imports; unit and contract suites already cover Stage 3/4 descriptors.
- Import-boundary or dependency constraints: `validation.py` may consume `adapters.py`, but scan results must not import `filters.py` or any view layer.

## Phase Isolation State

- Control checkout dirty-state review: only unrelated untracked docs remain in the control checkout.
- Dedicated branch/worktree status: created from current `develop` at `/home/samcantrill/work/rphys-worktrees/stage-5-p2-adapters-validation`.
- Current `develop` base: includes Phase 1 merge metadata commit `4126a757b82498a97c064c72b4599ae3b9386bb4`.
- Earlier phase dependency status: Phase 1 merged and recorded.
- Push/PR infrastructure status: GitHub auth and Phase 1 PR workflow verified.
- Stop condition if isolation cannot be maintained: stop before PR submission and record the blocker.

## In-Scope Work

- Add datasource scan spec/result records and structural adapter protocol.
- Add validation IO policy, validation issue/report records, and descriptor-only scan-result validation.
- Add exercised Stage 5 datasource errors.
- Add private synthetic adapter fixtures under `tests/support`.
- Add unit, contract, and package coverage for scan/validation behavior and import boundaries.

## Out-of-Scope Work

- Views, filters, candidates, groups, split assignment, index finalization, manifest codecs, composite indexes, real datasource SDK integrations, registries, alias discovery, and payload loading.

## Assumptions

- Exact field names are implementation details as long as the records preserve descriptor identity, primitive evidence, warnings, rejections, and explicit IO policy.
- Validation issue codes remain provisional strings, not stable enum taxonomy.

## Scope Contract

Public names are exposed only from `rphys.datasources.adapters` and `rphys.datasources.validation`. `rphys.datasources` and root `rphys` parent exports remain unchanged. Scan results carry descriptors and primitive evidence only; validation reports are inspectable summaries and do not mutate descriptors.

## Scientific Contract Notes

- Sampling and temporal alignment: unchanged; no payload or field-native windows are introduced.
- Field roles, locators, schemas, and provenance: datasource and record refs are preserved without mutation.
- Masking, filtering, normalization, and aggregation order: unchanged.
- Subject identity, splits, leakage, and grouping: metadata can be inspected, but no split/group semantics are introduced.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: missing descriptor fields/metadata are reported; runtime numerical validation is out of scope.

## Design Impact

- Maintainability: adapter, scan, and validation concerns are separated from view/filter/index modules.
- Extensibility: real adapters can implement the structural protocol without global registration.
- Lightweight import policy: modules import only stdlib and existing descriptor modules.
- Source-tree boundaries: synthetic datasource behavior remains private test support.

## Future Compatibility

Later phases can consume `DataSourceScanResult` and `DataSourceValidationReport` without changing descriptor semantics. Real datasource adapters can be added without pulling SDK dependencies into core imports.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Adapter registry or aliases | The approved design prefers importable Python objects and `_target_` paths. |
| Validation issue enum | Codes are provisional diagnostics, not stable taxonomy. |
| Scan result carrying views | Would violate scan/view separation and Phase 3 ownership. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Validation reports have no durable schema version | Persistence belongs to later manifest phases. | Phase 6 durable schema work needs validation evidence in manifests. |

## Reviewability

- Expected PR size and shape: public API/data-shape PR with focused tests.
- Files and areas to inspect: `adapters.py`, `validation.py`, errors, package tests, synthetic support, unit/contract tests.
- Scope-control checks: no parent exports, no filters/views import from scan result, no hidden IO, no registry.

## Implementation Steps

1. Implement scan spec/result records and structural adapter protocol.
2. Implement validation IO policy, issues, reports, and `validate_scan_result`.
3. Add private synthetic adapter fixtures for unit/contract tests.
4. Update package/error tests for public submodule names and exercised errors.
5. Run unit, contract, package, and whitespace validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: submodule-first exports, no parent/root promotion, lightweight imports.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/datasources/test_adapters.py`, `tests/unit/rphys/datasources/test_validation.py`, `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: spec/result/report shapes, IO policy failures, primitive evidence, invalid input failures.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_datasource_scan_validation_contract.py`
- Required assertions or deferral reason: structural adapter contract, scan/view separation, provisional issue-code strings.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: vertical slice belongs to later phases.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end datasource flow yet.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real datasets or optional dependencies.

## Risks

- API shape may need additive refinement in later phases; current fields preserve the locked basics and tests cover no mutation or hidden IO.
- Strict IO policy could feel verbose, but prevents accidental full payload validation.

## Validation Commands

Targeted development commands:

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: adapters records/protocol, validation records/policy, private synthetic adapter, focused tests.
- Tests to run with each slice: unit tests first, then contract and package suites.
- Decisions the executor must not revisit: no registry, no scan/view coupling, no hidden IO, no real SDK dependency, no parent/root exports.
- Conditions that require stopping for the manager: need to add views, filters, payload loading, stable issue enums, or real adapter discovery.

## Refinement And Review Budget Status

- Phase execution plan refinement: manager-local expanded-path review completed
- Phase implementation refinement: not needed after targeted validation passed
- PR review: manager-local pre-submit review completed
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed with expanded-path review due public API/report shape.
- Implementation summary: implemented datasource specs/adapters, scan results, validation policy/issues/reports, validation entrypoint, private synthetic fixtures, and tests.
- Implementation validation: `make test-unit` passed with 332 tests; `make test-contract` passed with 41 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Refinement summary: not needed; no validation or scope blocker remains.
- Pre-submit blocker gate: passed; no view/filter coupling, hidden IO, registry, real SDK dependency, or parent/root export promotion.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/adapters-validation-pr-body.md`; PR #30 opened and verified against `develop`.
- Automated review: manager expanded-path review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
