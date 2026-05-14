# Phase 3 Execution Plan: Non-Mutating Views, Filter Chains, And Index-Candidate Selection

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: datasource views, filter chains, and provisional index candidates
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Non-Mutating Views, Filter Chains, And Index-Candidate Selection
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 3: Non-Mutating Views, Filter Chains, And Index-Candidate Selection`
- Branch: `agent/stage-5-p3-views-filters-candidates`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p3-views-filters-candidates`
- Phase execution plan path: `docs/roadmap/stage-5/phases/views-filters-candidates.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 3 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path due public API and candidate data-shape changes
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path review; no implementation refinement required after validation passed
- Setup limitations: no subagent delegation was used in this session
- Blockers: none

## Objective

Implement non-mutating descriptor views, structural filter chains, and provisional index candidates while preserving scan/view separation and keeping group/split assignment, durable index identity, manifests, and runtime samples out of scope.

## Full-Plan Context

Phase 3 consumes Phase 2 scan results and prepares selected candidates for later group/split and final index construction phases. It does not implement Phase 4 split policy, Phase 5 `DataSourceIndex`, or Phase 6/7 manifests and composites.

## Source Phase Summary

- Goal: implement staged non-mutating selection before group/split and final index entry emission.
- Required scope: `DataSourceViewPlan`, `DataSourceView`, view results, structural filters, `FilterChain`, `FilterResult`, `IndexCandidate`, candidate plans/views/results, and candidate filtering.
- Required checkpoints: no split assignment, no final entry identity, no payloads, no runtime samples, no hidden IO, and no `IndexItem.metadata` mutation.
- Acceptance criteria: filter/candidate order is scan/validation -> view/filter -> candidate construction -> candidate filtering.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: Phase 2 scan results are descriptor-only and parent exports remain conservative.
- Existing tests or harness behavior: unit/contract suites already exercise scan/validation and Stage 3 `IndexItem` purity.
- Import-boundary or dependency constraints: `indexes.py` may use `DataSourceView` and `FilterChain`, but must not pull in split/index manifest behavior.

## In-Scope Work

- Add immutable datasource view plan/view/result records.
- Add structural filter decisions, chains, and result records.
- Add index candidate plan/candidate/view/result records and candidate construction/filtering helpers.
- Add tests proving non-mutation, ordering, missing-field rejection, and `IndexItem` compatibility without identity metadata.

## Out-of-Scope Work

- Group and split assignment, final datasource indexes, entry sidecars, manifest codecs, composite indexes, payload loading, runtime `SampleOp` behavior, seconds/spatial/alignment windows, and split-conditioned filtering.

## Assumptions

- Candidate IDs can use record IDs provisionally; durable sidecar identity belongs to Phase 5.
- Filter objects can be callable or expose `evaluate(target)` as long as results are explicit and deterministic.

## Scope Contract

Views and filter results return new records/results while reusing descriptor objects without mutation. Candidates carry locator-to-`FieldView` mappings, record/source provenance, primitive metadata, and optional field-native indexes only. They do not carry split assignment, payloads, runtime samples, final entry identity, or fingerprints.

## Scientific Contract Notes

- Sampling and temporal alignment: only field-native `FieldIndex` values are attached to `FieldView`; no seconds conversion or alignment is inferred.
- Field roles, locators, schemas, and provenance: candidates validate locator keys against field keys and preserve record/source refs.
- Masking, filtering, normalization, and aggregation order: filters operate before candidate construction or candidate filtering; no runtime transforms occur.
- Subject identity, splits, leakage, and grouping: metadata is preserved but no group/split semantics are assigned.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: missing descriptor fields reject candidates; runtime numerical checks remain out of scope.

## Design Impact

- Maintainability: view/filter behavior is separate from candidate construction and later split/index phases.
- Extensibility: structural filters can apply to records or candidates without a registry.
- Lightweight import policy: modules import only stdlib and existing descriptor modules.
- Source-tree boundaries: no public test helper or fake datasource API is introduced.

## Future Compatibility

Phase 4 can consume candidate views for group/split assignment, and Phase 5 can finalize selected candidates into sidecar-backed indexes without changing candidate field mappings.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add split assignment to candidates | Phase 4 owns leakage policy and split provenance. |
| Add entry IDs or fingerprints to candidates | Phase 5 owns durable sidecar identity. |
| Return `IndexItem` directly from candidate construction | Would collapse candidate and final index responsibilities. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Candidate IDs are provisional record IDs | Durable identity is explicitly Phase 5 scope. | Phase 5 sidecar entry construction. |

## Reviewability

- Expected PR size and shape: public API/data-shape PR with focused tests.
- Files and areas to inspect: `filters.py`, `indexes.py`, errors, package tests, candidate/view unit and contract tests.
- Scope-control checks: no groups/splits, no final index class, no manifests, no payload loading, no metadata identity mutation.

## Implementation Steps

1. Implement datasource view plan/view/result and `build_view`.
2. Implement filter decisions/chains/results.
3. Implement index candidate plan/candidate/view/result and construction/filtering helpers.
4. Add unit and contract tests for order, non-mutation, and candidate purity.
5. Run unit, contract, package, and whitespace validation.

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

## Refinement And Review Budget Status

- Phase execution plan refinement: manager-local expanded-path review completed
- Phase implementation refinement: not needed after targeted validation passed
- PR review: manager-local pre-submit review completed
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local draft.
- Final phase execution plan: completed with expanded-path review due public API/candidate shape.
- Implementation summary: implemented non-mutating views, filter chains, provisional candidates, candidate filtering, and tests.
- Implementation validation: `make test-unit` passed with 343 tests; `make test-contract` passed with 44 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Refinement summary: not needed; no validation or scope blocker remains.
- Pre-submit blocker gate: passed; no split assignment, final identity, manifests, payloads, runtime samples, or `IndexItem.metadata` identity mutation.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/views-filters-candidates-pr-body.md`; PR #31 opened and verified against `develop`.
- Automated review: manager expanded-path review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
