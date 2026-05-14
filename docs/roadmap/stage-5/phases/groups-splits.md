# Phase 4 Execution Plan: Candidate-Level Groups And Split Assignment

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v5`
- Feature focus: candidate groups and explicit group-disjoint split assignment
- Stage descriptor: DataSource Discovery, Views, Filters, Splits, And Indexes
- Phase descriptor: Candidate-Level Groups And Split Assignment
- PR title: `Stage 5 DataSource Discovery, Views, Filters, Splits, And Indexes - Phase 4: Candidate-Level Groups And Split Assignment`
- Branch: `agent/stage-5-p4-groups-splits`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p4-groups-splits`
- Phase execution plan path: `docs/roadmap/stage-5/phases/groups-splits.md`
- Full plan: `docs/roadmap/stage-5/implementation-plan.md`
- Planning document: `docs/roadmap/stage-5/planning.md`
- Source phase: Phase 4 in `docs/roadmap/stage-5/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path due scientific leakage/split contract
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed 2026-05-14 in the implementation plan
- Blockers: none

## Objective

Implement candidate-level group extraction and explicit group-disjoint split assignment over selected index candidates without adding trainer/evaluator modes, implicit ratios, post-split filtering, or final index persistence.

## Scope Contract

Groups are named metadata-derived values extracted from candidate, record, or datasource metadata. Required groups fail loudly by default. Splits are assigned only through explicit split-group value mappings; missing split-group assignments and leakage raise errors. Non-split analysis groups are preserved in split assignments.

## Scientific Contract Notes

- Subject identity, splits, leakage, and grouping: split assignment is candidate-level and group-disjoint by explicit split-group key.
- Masking, filtering, normalization, and aggregation order: no post-split filtering is implemented.
- Sampling and temporal alignment: unchanged.
- Field roles, locators, schemas, and provenance: candidate provenance is preserved; no index entries are finalized.

## In-Scope Work

- `GroupPlan`, `GroupBuilder`, `GroupResult`, and `CandidateGroupAssignment`.
- `SplitPlan`, `SplitBuilder`, `SplitResult`, and `SplitAssignment`.
- Unit and contract tests for multiple groups, missing required groups, explicit split mappings, leakage detection, counts, and analysis group preservation.

## Out-of-Scope Work

- Implicit ratios, seeded random assignment, trainer/evaluator modes, project-specific recipes, split-conditioned filtering, final indexes, manifests, and persistence.

## Validation Commands

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
- Final phase execution plan: completed with expanded-path review due leakage/split contract.
- Implementation summary: implemented candidate group extraction, explicit split assignment, leakage checks, counts, and tests.
- Implementation validation: `make test-unit` passed with 350 tests; `make test-contract` passed with 46 tests; `make test-package` passed with 25 tests; `git diff --check` passed.
- Pre-submit blocker gate: passed; no implicit ratios, trainer/evaluator semantics, post-split filtering, or final index persistence.
- PR preparation: PR body drafted at `docs/roadmap/stage-5/phases/groups-splits-pr-body.md`; PR #32 opened and verified against `develop`.
- Automated review: manager expanded-path review passed before PR submission; GitHub checks pending/not configured at open.
- Merge result: PR #32 squash-merged to `develop` at `c8ec1454c08e65ea73c3e61c1f651217a30f220c` on 2026-05-14.
- Cleanup: pending worktree and branch removal after metadata commit.
- Remaining blockers: none.
