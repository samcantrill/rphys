# Phase 4 Execution Plan: Stage 13 Scan-To-Report Tail

## Metadata

- Status: merged
- Roadmap stage: `v14`
- Feature focus: Stage 13 scan-to-report smoke tail and final validation
- Stage descriptor: Synthetic Fixtures, Contract Tests, And Smoke Hardening
- Phase descriptor: Stage 13 Scan-To-Report Tail
- PR title: `Stage 14 Synthetic Fixtures, Contract Tests, And Smoke Hardening - Phase 4: Stage 13 Scan-To-Report Tail`
- Branch: `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
- Phase execution plan path: `docs/roadmap/stage-14/phases/stage13-scan-to-report-tail.md`
- Full plan: `docs/roadmap/stage-14/implementation-plan.md`
- Planning document: `docs/roadmap/stage-14/planning.md`
- Source phase: `docs/roadmap/stage-14/implementation-plan.md#phase-4-stage-13-gated-scan-to-report-tail-and-final-validation`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 1-3 are merged and recorded
- Stage 13 prerequisite gate: satisfied in active `develop` by PRs #85-#90
- Draft pass: completed by manager
- Refine pass: completed by manager because this phase composes Stage 14
  synthetic fixtures with Stage 13 artifact, metric, visualization, report,
  and collection APIs
- Setup limitations: control checkout remains dirty and behind
  `origin/develop`; all work is isolated in this Phase 4 worktree
- Blockers: none for Phase 4

## Objective

Complete the Stage 14 root smoke by extending the synthetic scan/index/sample
path through real Stage 13 public APIs: returned `Batch` prediction fields,
explicit uncollation, sample artifact export/reload, metric-as-operation
fields, visualization/report records, and grouped/stitched sample-collection
outputs.

## In-Scope Work

- Add one integration smoke tail using Phase 1-3 synthetic fixtures and real
  Stage 13 public APIs.
- Verify legacy Stage 13 public runner/output/observation names remain absent
  while the smoke uses code-backed replacements.
- Record final validation evidence for package, contract, integration, e2e
  availability, summary, lock, PR validation, and whitespace checks.

## Out-of-Scope Work

- New production APIs, fake Stage 13 stand-ins, private report runners, public
  test helper packages, real datasets, network/GPU/heavy optional dependency
  requirements, performance profiling, broad golden snapshots, and Stage 15
  data-path optimization.

## Scope Contract

The smoke path must be a real composition of public `rphys` objects. It may use
private synthetic test fixtures from Phases 1-3, but it must not use a hidden
Stage 13 runner, skipped tail, placeholder production module, or old public
`MethodOutput*`, `StepOutput`, `MetricObservation*`, `MetricResult`, or
evaluation-runner surface.

## Scientific Contract Notes

- Sampling and temporal alignment: the test uses a deterministic two-sample
  BVP/timestamp slice from public datasource indexes.
- Field roles, locators, schemas, and provenance: prediction, target, metric,
  visualization, and stitched output locators remain explicit and
  role-qualified.
- Subject identity, splits, leakage, and grouping: subject/split sidecars are
  carried from source records into report rows and collection grouping.
- Artifact provenance: predictions are uncollated per sample, exported through
  `sample_artifact_export_request`, reassembled as a derived datasource, and
  reloaded through `SampleBuilder`.
- Failure behavior: this phase composes positive final smoke behavior; Phase 1
  edge variants and Phase 2 contract assertions remain the detailed failure
  vocabulary.

## Implementation Steps

1. Add a final integration smoke test that starts with synthetic scan
   validation and index construction.
2. Run a Batch-returning method through `SupervisedLearner`, then explicitly
   uncollate returned prediction/target/input fields.
3. Export and reload per-sample artifacts through public export and derived
   datasource APIs.
4. Apply metric, visualization, report, grouping, sorting, and concatenation
   operations to produce report rows and record-level output fields.
5. Check legacy Stage 13 public surfaces remain absent.
6. Run required focused, package, contract, integration, summary, lock, PR, and
   whitespace validation.

## Validation Commands

```sh
uv run pytest tests/integration/test_stage14_scan_to_report_tail.py
uv run pytest tests/package/test_import.py -k stage_13
make test-package
make test-contract
make test-integration
make test-e2e
make test-summary
make validate-pr
uv lock --check
git diff --check
```

## Completion Notes

- Draft plan: completed on 2026-05-18.
- Final phase execution plan: completed on 2026-05-18.
- Implementation summary: Stage 14 scan-to-report tail integration added.
- Implementation validation: focused scan-to-report tail test passed; focused
  Stage 13 package guardrails passed; `make test-package`,
  `make test-contract`, `make test-integration`, `make test-e2e`,
  `make test-summary`, `make validate-pr`, `uv lock --check`, and
  `git diff --check` passed on 2026-05-18. `make test-e2e` reported the e2e
  suite is not present. The clean summary reported 1028 passed tests across
  package, unit, contract, and integration suites, with e2e and acceptance not
  present.
- Refinement summary: no implementation refiner needed unless validation fails.
- Pre-submit blocker gate: passed by manager review; the smoke tail uses
  code-backed Stage 13 public APIs, keeps legacy Stage 13 runner/output/
  observation surfaces absent, and adds no production placeholder, alternate
  loader, public helper package, real data, network, GPU, heavy optional
  dependency, or workflow runtime.
- PR preparation: PR body drafted at
  `docs/roadmap/stage-14/phases/stage13-scan-to-report-tail-pr-body.md`.
- Automated review: GitHub reported no status checks; local validation passed.
- Merge result: squash-merged to `develop` on 2026-05-18 as
  `e5f30f81e98a6250c1b0f732324163dc39ef2961`.
- Cleanup: pending.
- Remaining blockers: none.
