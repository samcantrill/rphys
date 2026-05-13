# Phase 1 Execution Plan: Public Surface And Diagnostics

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v3`
- Feature focus: Stage 3 public package homes and diagnostics guardrails
- PR title: `Stage 3 P1: public surface and diagnostics guardrails`
- Branch: `agent/stage-3-p1-public-surface-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p1-public-surface-errors`
- Phase execution plan path: `docs/roadmap/stage-3/phases/public-surface-errors.md`
- Full plan: `docs/roadmap/stage-3/implementation-plan.md`
- Planning document: `docs/roadmap/stage-3/planning.md`
- Source phase: Phase 1, `public-surface-errors`
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: fast path
- Phase isolation: dedicated branch, worktree, and PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; maintainer approval recorded in the implementation plan
- Draft pass: manager-local draft, no subagent used in this session
- Refine pass: not needed for fast path if targeted validation passes
- Setup limitations: control checkout has an unrelated local `docs/roadmap.md` edit that is outside Phase 1 ownership and remains untouched
- Blockers: none

## Objective

Establish the Stage 3 import and diagnostics guardrails before descriptor behavior lands. This phase keeps `rphys.io` and `rphys.datasources` importable and empty at the public surface, preserves the existing broad error base behavior, and prevents root or deferred-package exports from freezing placeholder descriptor APIs.

## Full-Plan Context

Phase 1 prepares the public boundary for later descriptor phases. Phase 2 will add IO descriptors and concrete errors only with behavior that raises them. Phase 3 will add datasource refs and schema descriptors. Phase 4 will add `IndexItem`. Phase 5 will harden public examples, docs, and full validation.

## Source Phase Summary

- Goal: establish typed diagnostics and import-boundary guardrails.
- Required scope: `src/rphys/errors.py`, `src/rphys/io/__init__.py`, `src/rphys/datasources/__init__.py`, package tests, and focused error unit tests.
- Required checkpoints: no root exports, no placeholder descriptor modules or exports, no heavy optional imports, and no unexercised Stage 3 concrete errors.
- Acceptance criteria: package imports remain lightweight, error context behavior is preserved, and package docstrings describe homes without promising deferred codec, builder, registry, or runtime behavior.

## Current Source And Harness Findings

- `rphys.errors` already exposes broad IO, datasource, slice, and codec bases plus Stage 1/2 concrete errors.
- `rphys.io` and `rphys.datasources` import with empty `__all__`.
- Package tests already cover planned package imports, root non-exports, heavy optional import exclusions, and no generic workflow/artifact packages.

## Phase Isolation State

- Control checkout dirty-state review: only `docs/roadmap.md` is modified outside this phase's owned files.
- Dedicated branch/worktree status: created from `develop` at the approved Stage 3 implementation-plan commit.
- Current `develop` base: `9d75aba` at phase start.
- Earlier phase dependency status: no prior Stage 3 phases.
- Push/PR infrastructure status: GitHub auth and `develop` fetch were verified before phase setup.
- Stop condition if isolation cannot be maintained: do not copy the unrelated control-checkout roadmap edit or implement descriptor behavior in this phase.

## In-Scope Work

- Tighten package tests around Stage 3 package homes, exact public surfaces, no root re-exports, and deferred descriptor names.
- Preserve and test broad error-base message/context behavior and exact currently implemented error exports.
- Clarify package docstrings so Phase 1 does not promise codecs, builders, registries, datasource scanning, or runtime hooks.

## Out-of-Scope Work

- Descriptor modules, constructors, serialization, datasource provenance, `IndexItem`, codecs, builders, manifests, runtime sample construction, and concrete descriptor errors.

## Assumptions

- Later phases may replace Phase 1 deferred-name assertions as they add code-backed exports.
- No concrete Stage 3 error is directly exercised by Phase 1 behavior.

## Scope Contract

No Stage 3 descriptor API is introduced in this phase. `rphys.__all__` remains empty. `rphys.io.__all__` and `rphys.datasources.__all__` remain empty. Error behavior remains the existing broad-base behavior with readable messages and copied context.

## Scientific Contract Notes

- Sampling and temporal alignment: not implemented; no slice semantics are introduced.
- Field roles, locators, schemas, and provenance: existing Stage 1/2 exports are only guarded against accidental duplication from deferred packages.
- Masking, filtering, normalization, and aggregation order: not touched.
- Subject identity, splits, leakage, and grouping: not touched.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not touched.

## Design Impact

- Maintainability: keeps public errors and imports code-backed and testable.
- Extensibility: leaves descriptor behavior to P2 through P4 without placeholder names.
- Lightweight import policy: package tests continue to run imports in a fresh interpreter and check heavy optional modules.
- Source-tree boundaries: only package homes, errors, and tests are in scope.

## Future Compatibility

Later phases can add implemented descriptor exports without inheriting placeholder behavior from P1. Concrete descriptor errors must be added with behavior that raises them and tests that exercise them.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add descriptor modules with empty classes now | Would freeze placeholder public API before behavior exists. |
| Add all planned concrete descriptor errors in P1 | Would create unexercised public names and compatibility burden. |
| Re-export Stage 3 names from `rphys` root | Violates approved no-root-reexport policy. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Deferred descriptor package exports remain manually enumerated in tests | This is temporary until code-backed P2-P4 exports land. | Update tests in the descriptor phase that implements each name. |

## Reviewability

- Expected PR size and shape: small docs/test/docstring diff.
- Files and areas to inspect: package imports, error tests, `rphys.io` and `rphys.datasources` docstrings.
- Scope-control checks: no new descriptor modules, no concrete descriptor errors, no root exports, no heavy imports.

## Implementation Steps

1. Add this phase execution plan in the Phase 1 worktree.
2. Update `rphys.io` and `rphys.datasources` package docstrings to describe package homes without deferred runtime promises.
3. Harden package tests for Stage 3 empty public homes and root non-exports.
4. Harden error unit tests for exact current `__all__` and no unexercised Stage 3 concrete errors.
5. Run `make test-package`, focused error unit tests through `make test-unit`, and `git diff --check`.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions: exact Stage 3 package surfaces, no root re-exports, no duplicate vocabulary, no heavy optional imports, no workflow/artifact packages.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/test_errors.py`
- Required assertions: exact error exports, inheritance, readable messages, context preservation, and deferred descriptor-specific errors.

### Contract Suite

- Status: deferred
- Required assertions or deferral reason: no descriptor behavior exists yet; public lazy-reference contracts begin in Phase 2 and are finalized in Phase 5.

### Integration Suite

- Status: deferred
- Required assertions or deferral reason: Phase 1 does not connect runtime systems.

### E2E Suite

- Status: deferred
- Required assertions or deferral reason: no user-facing workflow or dataset behavior.

### Acceptance Suite

- Status: deferred
- Required assertions or deferral reason: no acceptance markers are affected.

## Risks

- Over-tightening tests could make later descriptor phases update package tests, but that is expected and keeps public exports intentional.
- Package docstrings must avoid promising deferred behavior while still naming the package homes clearly.

## Validation Commands

Targeted development commands:

```sh
make test-package
make test-unit
git diff --check
```

Final PR-preparation commands:

```sh
make test-package
make test-unit
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: package docstrings, package tests, error unit tests.
- Tests to run with each slice: `make test-package`, `make test-unit`, `git diff --check`.
- Decisions the executor must not revisit: no root exports, no placeholder descriptor modules, no unexercised concrete errors.
- Conditions that require stopping for the manager: any need to change approved public homes or add descriptor behavior.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed before code changes.
- Implementation summary: tightened Stage 3 package-home docstrings and package/error tests without adding descriptor modules, descriptor exports, root exports, or concrete Stage 3 errors.
- Implementation validation: `make test-package` passed with 15 tests; `make test-unit` passed with 188 tests; `git diff --check` passed.
- Refinement summary: not needed; targeted validation passed and no blocker was found.
- Pre-submit blocker gate: passed manager-local scope review; diff is limited to Phase 1 docstrings, tests, and this phase artifact.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
