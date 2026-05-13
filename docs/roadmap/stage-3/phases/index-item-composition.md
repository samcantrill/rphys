# Phase 4 Execution Plan: Role-Qualified IndexItem Composition

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v3`
- Feature focus: role-qualified lazy index items
- PR title: `Stage 3 P4: IndexItem composition`
- Branch: `agent/stage-3-p4-index-item-composition`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p4-index-item-composition`
- Phase execution plan path: `docs/roadmap/stage-3/phases/index-item-composition.md`
- Full plan: `docs/roadmap/stage-3/implementation-plan.md`
- Planning document: `docs/roadmap/stage-3/planning.md`
- Source phase: Phase 4, `index-item-composition`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: dedicated branch, worktree, and PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 1 through 3 are merged and recorded
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path refinement for role mapping, record membership, item identity, and no-alignment posture
- Setup limitations: control checkout has an unrelated local `docs/roadmap.md` edit outside Phase 4 ownership
- Blockers: none

## Objective

Implement `IndexItem(fields, record, metadata=None)` as the pure lazy IO unit
for later sample builders. It maps role-qualified `FieldLocator` keys to
`FieldView` values, preserves mandatory `RecordRef` provenance, validates
locator/view key consistency and record field membership, and remains free of
runtime sample construction, item IDs, fingerprints, transforms, export,
training, manifests, and implicit alignment.

## Full-Plan Context

Phase 2 supplies field views and Phase 3 supplies record provenance. Phase 4
composes those descriptors into the lazy item unit. Phase 5 will harden public
contracts, docs, and broad validation across the complete graph.

## Source Phase Summary

- Goal: implement role-qualified lazy item composition.
- Required scope: `src/rphys/datasources/index_items.py`, datasource exports,
  concrete index-item error, index-item unit tests, package tests, and contract examples.
- Required checkpoints: non-empty `FieldLocator -> FieldView`, mandatory
  `RecordRef`, locator/view key consistency, record field membership,
  primitive metadata, primitive round trips, and no item identity or runtime sample behavior.
- Acceptance criteria: future supervised item examples map input and target
  roles to different field-native views without constructing a `Sample`.

## Current Source And Harness Findings

- `FieldLocator` already preserves runtime role separately from intrinsic `DataKey`.
- `FieldView` is role-free and carries optional field-native indexes.
- `RecordRef.fields` provides intrinsic field membership for validation.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` edit remains outside Phase 4 files.
- Dedicated branch/worktree status: created from `develop` after Phase 3 metadata commit `7aaf4f3`.
- Current `develop` base: `7aaf4f3` at phase start.
- Earlier phase dependency status: Phases 1 through 3 merged and recorded.
- Push/PR infrastructure status: GitHub auth, fetch, PR listing, and prior merge path verified.
- Stop condition if isolation cannot be maintained: do not implement runtime samples, sample builders, datasource indexes, manifests, fingerprints, or stable item identity.

## In-Scope Work

- Add `IndexItem` descriptor and exercised `InvalidIndexItemError`.
- Update datasource package exports and import-boundary tests.
- Add unit and contract coverage for construction, invalid input, mapping
  isolation, serialization, membership validation, and coupling exclusions.

## Out-of-Scope Work

- Runtime `Sample`, `FieldValue`, lazy `SampleField`, `SampleBuilder`,
  transforms, augmentations, export, training, stochastic/nested/multi-member
  items, `item_id`, fingerprints, datasource-index identity, and manifests.

## Assumptions

- Mandatory `RecordRef` provenance is accepted even for synthetic examples.
- Stable item identity can be added externally by later datasource index stages.

## Scope Contract

`IndexItem` requires a non-empty `FieldLocator -> FieldView` mapping and a
mandatory `RecordRef`. Each locator's intrinsic `DataKey` must match its
`FieldView.field_ref.key`, and every view field key must be present in
`record.fields`. Metadata is copied as immutable primitive data. Serialization
uses exactly `fields`, `record`, and `metadata`.

## Scientific Contract Notes

- Sampling and temporal alignment: per-field indexes remain field-native; matching numeric indexes across roles do not imply alignment.
- Field roles, locators, schemas, and provenance: runtime role is in the locator; intrinsic field identity is in `FieldRef`; provenance is in `RecordRef`.
- Masking, filtering, normalization, and aggregation order: not implemented.
- Subject identity, splits, leakage, and grouping: preserved through `RecordRef` metadata only.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not introduced beyond item mapping validation.

## Design Impact

- Maintainability: composition stays in `rphys.datasources` without coupling to runtime containers.
- Extensibility: later sample builders can consume items without redefining roles or provenance.
- Lightweight import policy: uses stdlib, Stage 1 locators, Phase 2 field views, and Phase 3 records only.
- Source-tree boundaries: no IO descriptor semantics or runtime data containers are modified.

## Future Compatibility

Stage 4 sample builders can turn `IndexItem` into runtime samples. Stage 5 can
wrap items in datasource indexes/manifests with stable identity and fingerprints
without mutating Stage 3 item fields.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add `item_id` now | Stable item identity is datasource-index/manifest policy deferred to Stage 5. |
| Make record optional | Mandatory record provenance is approved and keeps leakage context inspectable. |
| Construct runtime `Sample` directly | Sample materialization belongs to later sample-builder behavior. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Synthetic examples require verbose `RecordRef` setup | Preserves mandatory provenance without adding builders. | Later sample-builder/datasource stages add ergonomic factories. |

## Reviewability

- Expected PR size and shape: narrow descriptor module plus focused tests.
- Files and areas to inspect: `index_items.py`, datasource exports, error taxonomy, package/unit/contract tests.
- Scope-control checks: no runtime sample dependency, sample builder, transforms, augmentations, training/export hooks, fingerprints, `item_id`, nested/multi-member items, or manifest behavior.

## Implementation Steps

1. Add `InvalidIndexItemError`.
2. Implement `IndexItem` with immutable copied fields and metadata.
3. Validate locator/view key consistency and record field membership.
4. Update datasource exports and package tests.
5. Add unit and contract coverage for role-qualified examples, serialization, and exclusions.
6. Run required validation and pre-submit scope review.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact datasource package/submodule exports, no root exports, no heavy optional imports.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/datasources/test_index_items.py`, `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: constructor validation, mapping isolation, serialization, failure cases, error inheritance, no runtime hooks.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_lazy_index_item_contract.py`
- Required assertions or deferral reason: EX-3, EX-4, and EX-5 role-qualified lazy item examples and exclusions.

### Integration Suite

- Status: deferred
- Required assertions or deferral reason: no runtime sample building exists.

### E2E Suite

- Status: deferred
- Required assertions or deferral reason: no user-facing workflow or dataset behavior.

### Acceptance Suite

- Status: deferred
- Required assertions or deferral reason: no opt-in acceptance behavior is affected.

## Risks

- Stable item identity pressure may reappear before Stage 5.
- Contract examples are verbose because mandatory record provenance is explicit.
- Role-qualified locators could be misread as alignment or sample construction if docs/tests are vague.

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

- Safe implementation slices: error, `IndexItem`, package tests, unit/contract tests.
- Tests to run with each slice: focused unit tests, then package and contract suites.
- Decisions the executor must not revisit: mandatory record, no `item_id`, no fingerprints, no runtime sample, no builders, no transforms/export/training hooks, no implicit alignment.
- Conditions that require stopping for the manager: item validation cannot work without stable identity, optional record provenance, runtime sample construction, or multi-member/nested item behavior.

## Refinement And Review Budget Status

- Phase execution plan refinement: used manager-local expanded-path refinement
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed with expanded-path guardrails.
- Implementation summary: added `IndexItem`; added exercised `InvalidIndexItemError`; updated datasource exports and package/unit/contract coverage for role-qualified lazy item composition.
- Implementation validation: `make test-unit` passed with 252 tests; `make test-contract` passed with 22 tests; `make test-package` passed with 18 tests; `git diff --check` passed.
- Refinement summary: first contract run found stale Phase 3 expectation that `IndexItem` was still deferred; fixed the contract to include the code-backed export.
- Pre-submit blocker gate: passed manager-local expanded-path scope review; no runtime sample dependency, sample builder, transforms, augmentations, training/export hooks, fingerprints, `item_id`, nested/multi-member items, or manifest behavior were introduced.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
