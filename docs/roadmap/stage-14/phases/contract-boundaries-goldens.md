# Phase 2 Execution Plan: Contract Boundaries And Durable Goldens

## Metadata

- Status: implemented; ready for PR submission
- Roadmap stage: `v14`
- Feature focus: private contract assertions, package guardrails, and narrow durable manifest goldens
- Stage descriptor: Synthetic Fixtures, Contract Tests, And Smoke Hardening
- Phase descriptor: Contract Boundaries And Durable Goldens
- PR title: `Stage 14 Synthetic Fixtures, Contract Tests, And Smoke Hardening - Phase 2: Contract Boundaries And Durable Goldens`
- Branch: `agent/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
- Phase execution plan path: `docs/roadmap/stage-14/phases/contract-boundaries-goldens.md`
- Full plan: `docs/roadmap/stage-14/implementation-plan.md`
- Planning document: `docs/roadmap/stage-14/planning.md`
- Source phase: `docs/roadmap/stage-14/implementation-plan.md#phase-2-contract-boundaries-and-durable-goldens`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phase 1 is merged and recorded
- Draft pass: completed by manager
- Refine pass: completed by manager review because this phase touches
  import-boundary and durable manifest contracts
- Setup limitations: control checkout is dirty and behind `origin/develop`;
  all work is isolated in this Phase 2 worktree
- Blockers: none for Phase 2

## Objective

Convert the Phase 1 private fixture catalog into reusable private contract
assertions, narrow durable manifest/fingerprint evidence, and package/import
guardrails while keeping public construction paths visible in consuming tests.

## Full-Plan Context

Phase 2 builds on the merged Phase 1 catalog. Phase 3 will use the resulting
support base for upstream smoke composition and validation tier semantics.
Phase 4 remains out of scope for this phase and must still consume real Stage
13 APIs only.

## In-Scope Work

- Add small private assertion helpers under `tests/support` for repeated
  public-object invariants: descriptor round trips, scan evidence,
  manifest/fingerprint shape, and sample materialization.
- Add contract/integration consumers that construct public `rphys` objects
  directly and use helpers only for repeated invariant checks.
- Add one narrow manifest/fingerprint golden for a public datasource index
  manifest contract without loaded arrays or private helper internals.
- Harden package checks for absence of public `rphys.testing`,
  `rphys.fixtures`, root fixture exports, and production imports from
  `tests.support`.

## Out-of-Scope Work

- Public testing-helper packages, support-level scenario runners or registries,
  broad private snapshots, Stage 3 smoke tiers, Phase 4 scan-to-report tail
  behavior, production placeholder exports, real data, and optional-heavy
  checks.

## Scope Contract

No public library behavior changes are planned. New helpers remain private
under `tests/support` and must not hide public object construction in tests.
Goldens may freeze only durable public manifest/fingerprint facts, not loaded
payloads, open handles, broad object dictionaries, or helper implementation
details.

## Scientific Contract Notes

- Sampling and temporal alignment: manifest and sample assertions preserve the
  Phase 1 sample-rate, timestamp, waveform, and alignment evidence.
- Field roles, locators, schemas, and provenance: helpers check public
  descriptors, role locators, schema names, record provenance, and manifest
  sidecar entries.
- Subject identity, splits, leakage, and grouping: index assertions preserve
  group and split evidence from public `DataSourceIndexEntry` sidecars.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: Phase 2 uses Phase 1 edge evidence where relevant but
  does not add new validators or coerce invalid fixtures.

## Implementation Steps

1. Add private contract assertion helpers with narrow responsibilities.
2. Add a focused contract test that builds a catalog index and validates
   descriptor, scan, manifest, and sample invariants through helpers.
3. Add a narrow golden JSON file and test it against public manifest output.
4. Add package/import-boundary tests for no public helper leakage and no source
   imports from `tests.support`.
5. Run targeted and suite-level validation; update this phase artifact and PR
   body with evidence.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`
- Required assertions: no public testing/fixture package, no root fixture
  exports, no production source imports from `tests.support`.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_synthetic_contract_assertions.py`
- Required assertions: descriptor round trip, scan evidence, manifest
  fingerprint/golden, no loaded payloads, sample materialization, provenance.

### Integration Suite

- Status: required where touched
- Expected paths: existing `tests/integration/test_synthetic_catalog_flow.py`
  remains the integration consumer for this phase's helpers and catalog shape.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/contracts/test_synthetic_contract_assertions.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-contract
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Refinement And Review Budget Status

- Phase execution plan refinement: completed by manager
- Phase implementation refinement: not needed; validation passed
- PR review: manager review completed
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed on 2026-05-18.
- Final phase execution plan: completed on 2026-05-18.
- Implementation summary: private contract assertions, narrow manifest golden,
  consuming contract tests, and package guardrails added.
- Implementation validation: focused contract/package checks passed;
  `make test-package`, `make test-contract`, `make test-integration`,
  `make validate-pr`, rerun `make test-summary`, and `git diff --check`
  passed on 2026-05-18. A concurrent `make test-summary` attempt collided
  with `make validate-pr` while writing summary artifacts and was rerun alone;
  the clean summary reported 1026 passed tests across package, unit, contract,
  and integration suites, with e2e and acceptance not present.
- Refinement summary: no implementation refiner needed unless validation fails.
- Pre-submit blocker gate: passed by manager review; helpers remain private,
  the golden freezes only manifest/fingerprint facts, and no public package,
  runner, placeholder export, broad snapshot, or Stage 13 tail work was added.
- PR preparation: PR body drafted at
  `docs/roadmap/stage-14/phases/contract-boundaries-goldens-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
