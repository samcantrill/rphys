# Phase 5 Execution Plan: Contract Examples, Docs, And Final Validation Hardening

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v3`
- Feature focus: Stage 3 lazy-reference contract hardening
- PR title: `Stage 3 P5: lazy reference hardening`
- Branch: `agent/stage-3-p5-lazy-reference-hardening`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p5-lazy-reference-hardening`
- Phase execution plan path: `docs/roadmap/stage-3/phases/lazy-reference-hardening.md`
- Full plan: `docs/roadmap/stage-3/implementation-plan.md`
- Planning document: `docs/roadmap/stage-3/planning.md`
- Source phase: Phase 5, `lazy-reference-hardening`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: dedicated branch, worktree, and PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 1 through 4 are merged and recorded
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path refinement for complete graph coverage, docs wording, import boundaries, and final validation
- Setup limitations: control checkout has an unrelated local `docs/roadmap.md` edit outside Phase 5 ownership
- Blockers: none

## Objective

Prove the complete Stage 3 descriptor graph through public imports, align
glossary wording with implemented names, and run focused plus broad validation.
This phase should not add new Stage 3 behavior beyond defect fixes required by
the contract examples.

## Full-Plan Context

Phases 1 through 4 landed public surfaces, IO descriptors, datasource refs and
schemas, and `IndexItem`. Phase 5 hardens the combined public contract and
records final validation evidence.

## Source Phase Summary

- Goal: prove `DataSourceRef -> RecordRef -> FieldRef -> FieldView -> IndexItem` and the approved exclusions.
- Required scope: contract tests, package/import boundary checks, public docstrings/glossary wording if needed, and broad validation evidence.
- Required checkpoints: public-import examples, primitive graph round trips, no root exports, no heavy imports, no private helper exports, no runtime/codec/datasource/workflow coupling, and no deferred fields.
- Acceptance criteria: EX-1 through EX-5 are covered without real datasets, optional dependencies, codecs, builders, manifests, or runtime sample construction.

## Current Source And Harness Findings

- Existing Phase 2 through 4 contracts cover IO, datasource, and index item slices separately.
- A single full graph contract improves reviewability for the final public behavior.
- `docs/GLOSSARY.md` had lazy IO entries but did not yet name `DataSourceRef`, `DataSourceSchema`, or `TemporalIndexSlice`.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` edit remains outside Phase 5 files.
- Dedicated branch/worktree status: created from `develop` after Phase 4 metadata commit `cb1ec81`.
- Current `develop` base: `cb1ec81` at phase start.
- Earlier phase dependency status: Phases 1 through 4 merged and recorded.
- Push/PR infrastructure status: GitHub auth, fetch, PR listing, and prior merge path verified.
- Stop condition if isolation cannot be maintained: do not add new behavior beyond documentation/test hardening or scoped defect fixes.

## In-Scope Work

- Add a complete public-import contract for the full lazy reference graph.
- Update glossary wording for implemented Stage 3 terms.
- Run focused and broad validation commands.
- Record unavailable checks, if any, with residual risk.

## Out-of-Scope Work

- New descriptor behavior, real datasets, hardware/network access, heavy optional dependencies, integration with runtime samples, codecs, builders, datasource scanning, manifests, fingerprints, stable item identity, seconds/spatial slices, and multi-member items.

## Assumptions

- Existing split contract files remain useful; the new full graph contract complements them rather than replacing them.
- Glossary updates are documentation alignment, not new API scope.

## Scope Contract

No new public classes, constructor fields, serialization keys, or behavior are
introduced in Phase 5. The complete descriptor graph must serialize through
primitive dictionaries without schema-version fields, fingerprints, item IDs,
payloads, manifests, validation status, or member fields.

## Scientific Contract Notes

- Sampling and temporal alignment: field-native indexes remain independent; no cross-field alignment claim is introduced.
- Field roles, locators, schemas, and provenance: role lives in `FieldLocator`; field identity lives in `DataKey`; provenance lives in `RecordRef` and metadata.
- Masking, filtering, normalization, and aggregation order: not implemented.
- Subject identity, splits, leakage, and grouping: metadata context survives the full graph.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: no new behavior beyond existing descriptor validation.

## Design Impact

- Maintainability: full graph contract catches accidental drift across modules.
- Extensibility: glossary and tests keep Stage 4/5 deferrals explicit.
- Lightweight import policy: package tests include implemented Stage 3 submodules.
- Source-tree boundaries: no workflow/artifact packages or root re-exports.

## Future Compatibility

Later stages can add codecs, sample builders, datasource indexes, manifests,
fingerprints, and stable item identity as wrappers or consumers without
changing Stage 3 descriptor meaning.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Replace split contract files with one large test | Split files still give focused failure signals for IO, datasource, and item slices. |
| Add README examples | Glossary plus executable contracts are enough for this stage without expanding public docs. |
| Run integration/e2e/acceptance suites as required | Stage 3 remains descriptor-only and has no integration with real datasets or runtime materialization. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Contract setup is verbose | Verbosity keeps provenance explicit without adding builders. | Later sample-builder or datasource stages add code-backed factories. |

## Reviewability

- Expected PR size and shape: small docs plus contract hardening and validation evidence.
- Files and areas to inspect: `tests/contracts/test_lazy_reference_contract.py`, `docs/GLOSSARY.md`, phase docs/PR body.
- Scope-control checks: no new implementation modules, public names, serialization fields, runtime hooks, registries, root exports, or heavy imports.

## Implementation Steps

1. Add full public-import contract covering EX-1 through EX-5.
2. Align glossary wording for implemented Stage 3 terms.
3. Run focused package/unit/contract validation.
4. Run broad `make test`, `make test-summary`, `make validate-pr`, `uv lock --check`, and `git diff --check`.
5. Record validation results in phase docs and PR body.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: public imports, exact `__all__`, no root exports, no heavy optional imports.

### Unit Suite

- Status: required
- Expected paths: all Stage 3 unit tests
- Required assertions or deferral reason: all descriptor behavior still passes after final hardening.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_lazy_reference_contract.py` plus existing lazy contracts
- Required assertions or deferral reason: full graph examples, primitive round trips, and negative coupling checks.

### Integration Suite

- Status: optional
- Required assertions or deferral reason: not required because descriptors do not connect to runtime materialization.

### E2E Suite

- Status: deferred
- Required assertions or deferral reason: no user-facing workflow or dataset behavior.

### Acceptance Suite

- Status: deferred
- Required assertions or deferral reason: no opt-in acceptance behavior is affected.

## Risks

- Broad validation may expose unrelated failures.
- Full graph examples can reveal earlier cross-phase defects.
- Glossary wording must avoid promising Stage 4/5 behavior.

## Validation Commands

Targeted development commands:

```sh
make test-package
make test-unit
make test-contract
git diff --check
```

Final PR-preparation commands:

```sh
make test
make test-summary
make validate-pr
uv lock --check
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: contract hardening, glossary wording, final validation docs.
- Tests to run with each slice: focused contract tests, then full required validation.
- Decisions the executor must not revisit: no new descriptor behavior, no root exports, no runtime samples/builders/codecs/manifests/fingerprints/item IDs.
- Conditions that require stopping for the manager: final examples require deferred capabilities or broad validation reveals unrelated failures that cannot be scoped.

## Refinement And Review Budget Status

- Phase execution plan refinement: used manager-local expanded-path refinement
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed with expanded-path guardrails.
- Implementation summary: added a full public-import lazy-reference graph contract and aligned `docs/GLOSSARY.md` with implemented Stage 3 descriptors, temporal slice semantics, provenance, and deferrals.
- Implementation validation: `make test-package` passed with 18 tests; `make test-unit` passed with 252 tests; `make test-contract` passed with 25 tests; `make test` passed with 296 tests; `make test-summary` passed and wrote `build/test-summary.md`; `make validate-pr` passed, including lock check, summary, build, and diff check; `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` passed; `git diff --check` passed.
- Refinement summary: first contract run used raw string lookup against `IndexItem.fields`; fixed the test to use parsed `FieldLocator` keys.
- Pre-submit blocker gate: passed manager-local expanded-path scope review; no new descriptor behavior, public names, serialization fields, runtime hooks, registries, root exports, or heavy imports were introduced.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
