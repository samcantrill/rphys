# Phase 0 Execution Plan: LIST Collation Round-Trip Repair

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v10`
- Feature focus: LIST collation inverse for default `Batch` containers
- Stage descriptor: Models, Methods, And NN Base Contracts
- Phase descriptor: LIST Collation Round-Trip Repair
- PR title: `Stage 10 Models, Methods, And NN Base Contracts - Phase 0: LIST Collation Round-Trip Repair`
- Branch: `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- Phase execution plan path: `docs/roadmap/stage-10/phases/list-uncollation-roundtrip.md`
- Full plan: `docs/roadmap/stage-10/implementation-plan.md`
- Planning document: `docs/roadmap/stage-10/planning.md`
- Source phase: `Phase 0: LIST Collation Round-Trip Repair`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed after maintainer implementation approval on 2026-05-16
- Draft pass: manager-local, because no subagent delegation was requested in this session
- Refine pass: not needed unless validation exposes a scope blocker
- Setup limitations: unrelated control-checkout changes in `docs/roadmap.md` and `docs/roadmap/stage-11/planning.md` are preserved and excluded
- Blockers: none

## Objective

Add a public `uncollate_batch` inverse for default LIST-collated batches so Stage 10 methods can rely on exact sample-field reconstruction without moving reconstruction logic into methods, trainers, or export helpers.

## Full-Plan Context

Phase 0 repairs the data-layer round trip before method/model contracts are introduced. Later phases may consume `Batch` objects and emit patch-like method outputs, but they must not own sample reconstruction, non-LIST collation policies, model tuple formatting, loaders, devices, exports, or trainer behavior.

## Source Phase Summary

- Goal: make default LIST-collated `Batch` containers unlist back to `tuple[Sample, ...]`.
- Required scope: `rphys.data` collation inverse, private collation evidence, scoped exports, and focused unit/contract/integration tests.
- Required checkpoints: fail loudly for ambiguous counts, non-LIST fields, payload length mismatches, metadata alignment mismatches, and unsupported batch-level scalar metadata.
- Acceptance criteria: explicit `None` metadata and absent metadata remain distinguishable, generic metadata round-trips where reversible, and Stage 9 torch collater flow remains FieldLocator-keyed and reversible.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/data/collation.py` is LIST-only and `BatchCollater` delegates to `collate_samples`; `Batch` and `Sample` share `FieldLocator`-keyed container behavior.
- Existing tests or harness behavior: collation unit tests cover LIST policy and sparse metadata; contract and integration tests cover FieldLocator-keyed `BatchCollater` output.
- Import-boundary or dependency constraints: `rphys.data` must remain dependency-light and must not import torch or framework stacks.

## Phase Isolation State

- Control checkout dirty-state review: unrelated roadmap/stage-11 docs are present and excluded from the phase branch.
- Dedicated branch/worktree status: created from current `origin/develop`.
- Current `develop` base: `4b36a84`
- Earlier phase dependency status: no earlier Stage 10 phases.
- Push/PR infrastructure status: GitHub auth and Git remote access verified before branch creation.
- Stop condition if isolation cannot be maintained: mark Phase 0 blocked and stop rather than implement in the control checkout.

## In-Scope Work

- Add public `uncollate_batch(batch) -> tuple[Sample, ...]`.
- Attach private per-batch collation evidence during `collate_samples`.
- Preserve current LIST collation payload and user-visible metadata behavior.
- Validate reversible payloads, schemas, policies, and sparse metadata alignment.
- Export `uncollate_batch` from `rphys.data` and extend focused tests.

## Out-of-Scope Work

- Stack, pad, drop, custom, device, or framework-specific collation policies.
- Model tuple/dict formatting, trainer batching, durable serialization, caches, or loaders.
- First-class sample IDs or domain identifier fields.
- Edits to Stage 9 planning artifacts or `docs/roadmap.md`.

## Assumptions

- Original `Sample` object identity is not preserved; field semantics are.
- Only batches produced by the default LIST collater are reversible.
- Private evidence is implementation detail and must not appear as ordinary field metadata.

## Scope Contract

`uncollate_batch` returns an immutable tuple of `Sample` containers. It supports only `Batch` objects produced by `collate_samples` or `BatchCollater` with default LIST fields. It reconstructs `FieldValue` payload entries, schema, collate policy, and per-sample metadata presence. It rejects manually assembled or edited batches when evidence, field sets, payload lengths, or metadata alignment no longer prove an exact LIST inverse.

## Scientific Contract Notes

- Sampling and temporal alignment: no resampling, slicing, alignment, or temporal interpretation is added.
- Field roles, locators, schemas, and provenance: locators and schemas are preserved; generic metadata is reconstructed only where collation evidence proves per-sample presence.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: no first-class identity fields are added; caller-owned metadata round-trips when reversible.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not interpreted by collation; missing fields and unsupported non-LIST fields fail through collate/uncollate validation.

## Design Impact

- Maintainability: inverse logic stays in `rphys.data` beside the collater.
- Extensibility: future non-LIST policies must add separate evidence and inverse semantics.
- Lightweight import policy: no new runtime dependencies.
- Source-tree boundaries: methods, models, loaders, trainers, and export helpers remain untouched.

## Future Compatibility

Stage 11-13 code can recover sample-aligned LIST fields through the data layer without depending on methods to reconstruct samples. Later collation policies can be added without changing this LIST-only contract.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Infer missing metadata from `None` in collated metadata lists | Cannot distinguish explicit `None` from an absent key. |
| Store evidence as ordinary metadata | Would leak private reconstruction details into user metadata. |
| Support manually assembled LIST-shaped batches | Cannot prove metadata presence or sample count without private collation evidence. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Private evidence supports only the default collater path | Exact LIST round trip is the current public need | A new collation policy or batch-construction API needs inverse semantics |

## Reviewability

- Expected PR size and shape: small public data API plus focused tests and one phase artifact.
- Files and areas to inspect: `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`, collation/contract/integration tests.
- Scope-control checks: no torch imports, no Stage 9 plan edits, no method/model/trainer/export changes.

## Implementation Steps

1. Add private collation evidence records and attach them during `collate_samples`.
2. Implement `uncollate_batch` validation and reconstruction.
3. Export `uncollate_batch` from `rphys.data`.
4. Add unit, contract, and Stage 9 collater integration tests for round trip and failure behavior.
5. Run required validation and update completion notes.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `make test-package`
- Required assertions or deferral reason: public export and import boundaries remain lightweight.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/data/test_collation.py`
- Required assertions or deferral reason: exact round trip, explicit `None` versus missing metadata, and fail-loud validation.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_batch_collater_contract.py`
- Required assertions or deferral reason: `BatchCollater` remains FieldLocator-keyed and non-model-formatted while exposing reversible LIST batches.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_stage9_torch_collater_flow.py`
- Required assertions or deferral reason: landed Stage 9 torch dataset/collater flow remains reversible.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: Phase 0 has no real dataset or workflow runtime behavior.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no user-facing acceptance workflow is introduced.

## Risks

- Private evidence could be lost on arbitrary copies; validation must fail rather than infer.
- Tests must assert field semantics, not original object identity.
- Future non-LIST policy support remains explicitly unsupported.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/data/test_collation.py
uv run pytest tests/contracts/test_batch_collater_contract.py
uv run pytest tests/integration/test_stage9_torch_collater_flow.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: private evidence, public inverse, export, focused tests.
- Tests to run with each slice: unit collation tests first, then contract and integration tests.
- Decisions the executor must not revisit: LIST-only inverse, tuple return, private evidence, no domain identifiers, no method/trainer reconstruction.
- Conditions that require stopping for the manager: inability to preserve explicit `None` versus missing metadata without public metadata pollution, or any need for non-LIST policy support.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed by manager in phase worktree.
- Final phase execution plan: this document.
- Implementation summary: added public `uncollate_batch`, private LIST collation evidence, scoped `rphys.data` exports, and focused round-trip/failure tests.
- Implementation validation: `uv run pytest tests/unit/rphys/data/test_collation.py`, `uv run pytest tests/contracts/test_batch_collater_contract.py`, `uv run pytest tests/integration/test_stage9_torch_collater_flow.py`, `make test-package`, `make validate-pr`, `make test-summary`, and `git diff --check` passed. `make test-summary` reported package 41 passed, unit 628 passed, contract 118 passed, integration 18 passed, and no e2e/acceptance suites present.
- Refinement summary: fixed lazy `SampleField` metadata collection order so payload-demanding LIST collation continues to materialize before metadata evidence is captured.
- Pre-submit blocker gate: passed; no scope, import-boundary, metadata-leakage, model-formatting, or future-policy blocker found.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
