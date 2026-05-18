# Phase 3 Execution Plan: Upstream Synthetic Smoke And Validation Tiers

## Metadata

- Status: implemented; ready for PR submission
- Roadmap stage: `v14`
- Feature focus: upstream synthetic smoke composition and validation tier notes
- Stage descriptor: Synthetic Fixtures, Contract Tests, And Smoke Hardening
- Phase descriptor: Upstream Synthetic Smoke And Validation Tiers
- PR title: `Stage 14 Synthetic Fixtures, Contract Tests, And Smoke Hardening - Phase 3: Upstream Synthetic Smoke And Validation Tiers`
- Branch: `agent/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
- Phase execution plan path: `docs/roadmap/stage-14/phases/upstream-smoke-validation-tiers.md`
- Full plan: `docs/roadmap/stage-14/implementation-plan.md`
- Planning document: `docs/roadmap/stage-14/planning.md`
- Source phase: `docs/roadmap/stage-14/implementation-plan.md#phase-3-upstream-synthetic-smoke-and-validation-tiers`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 1-2 are merged and recorded
- Draft pass: completed by manager
- Refine pass: completed by manager because this phase composes multiple public
  surfaces and records validation-tier behavior
- Setup limitations: control checkout remains dirty and behind
  `origin/develop`; all work is isolated in this Phase 3 worktree
- Blockers: none for Phase 3

## Objective

Compose one deterministic upstream smoke flow through public Stage 5-12 APIs
using the Phase 1-2 private fixture support, and document that debug, smoke,
and signal tiers are validation breadth choices over the same loader path.

## In-Scope Work

- Add a reviewable integration smoke slice covering synthetic scan,
  validation, group/split/index, manifest round trip, lazy sample building,
  sample operation pipeline, LIST collation, Batch-returning method prediction,
  and Stage 8 export/derived datasource reload.
- Explicitly label the flow incomplete before the Stage 13 scan-to-report tail.
- Add concise test-suite guidance for validation tiers without adding a hidden
  runner or alternate fake loader.

## Out-of-Scope Work

- Stage 13 returned-batch uncollation policy, sample artifact handoff,
  collection/metric/report tail, e2e suite creation, workflow runtime, real
  data, GPU/network/heavy dependency requirements, and performance profiling.

## Scope Contract

The smoke path must use public APIs and the same synthetic descriptors,
codecs, manifests, sample builders, operations, collaters, methods, export,
and derived datasource reload behavior that ordinary tests use. It must not
introduce production APIs or private Stage 13 stand-ins.

## Scientific Contract Notes

- Sampling and temporal alignment: the smoke consumes Phase 1 sample-rate,
  timestamp, waveform, and alignment evidence through public field metadata.
- Field roles, locators, schemas, and provenance: index and sample assertions
  preserve role-qualified locators, schema identities, record provenance, and
  derived datasource reload evidence.
- Subject identity, splits, leakage, and grouping: public group/split sidecars
  preserve subject and cohort boundaries.
- Failure behavior: this phase composes positive smoke behavior only; Phase 1
  edge variants and Phase 2 contract assertions remain the failure vocabulary.

## Implementation Steps

1. Add an integration test for the upstream smoke slice using public APIs and
   private Phase 1-2 support helpers.
2. Keep method prediction and export/reload upstream-only and explicitly
   incomplete before Stage 13 report-tail semantics.
3. Add concise suite-tier guidance to `tests/README.md`.
4. Run required integration/default validation and final PR gates.

## Validation Commands

```sh
uv run pytest tests/integration/test_stage14_upstream_smoke_flow.py
make test-integration
make test
make validate-pr
make test-summary
git diff --check
```

## Completion Notes

- Draft plan: completed on 2026-05-18.
- Final phase execution plan: completed on 2026-05-18.
- Implementation summary: upstream smoke integration and validation-tier docs
  added.
- Implementation validation: focused upstream smoke test passed;
  `make test-integration`, `make test`, `make validate-pr`,
  `make test-summary`, and `git diff --check` passed on 2026-05-18. The clean
  summary reported 1027 passed tests across package, unit, contract, and
  integration suites, with e2e and acceptance not present.
- Refinement summary: no implementation refiner needed unless validation fails.
- Pre-submit blocker gate: passed by manager review; the smoke flow stops
  before the Stage 13 tail, uses the same public loader/materialization path as
  focused tests, and adds no workflow runtime, alternate loader, heavy
  dependency, public helper package, or fake Stage 13 surface.
- PR preparation: PR body drafted at
  `docs/roadmap/stage-14/phases/upstream-smoke-validation-tiers-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
