# Phase 3 Execution Plan: Stateful And Trainable Capability Records

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v10`
- Feature focus: backend-neutral state and trainable capability records
- Stage descriptor: Models, Methods, And NN Base Contracts
- Phase descriptor: Stateful And Trainable Capability Records
- PR title: `Stage 10 Models, Methods, And NN Base Contracts - Phase 3: Stateful And Trainable Capability Records`
- Branch: `agent/stage-10-method-model-contracts-p3-state-trainable-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p3-state-trainable-records`
- Phase execution plan path: `docs/roadmap/stage-10/phases/state-trainable-records.md`
- Full plan: `docs/roadmap/stage-10/implementation-plan.md`
- Planning document: `docs/roadmap/stage-10/planning.md`
- Source phase: `Phase 3: Stateful And Trainable Capability Records`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 0-2 merged and recorded
- Draft pass: manager-local, because no subagent delegation was requested in this session
- Refine pass: not needed unless validation exposes public record drift
- Setup limitations: unrelated control-checkout roadmap/stage-11 docs are preserved outside this worktree
- Blockers: none

## Objective

Add richer backend-neutral state and parameter capability records plus structural `StatefulMethod`/`TrainableMethod` protocols without introducing torch, optimizer, checkpoint, device, distributed, trainer, or framework lifecycle behavior.

## Full-Plan Context

Phase 3 builds on Phase 1 method contracts and is independent of Phase 2 adapters except for shared package export conventions. Phase 4 will compose these records with synthetic fakes.

## Source Phase Summary

- Goal: add descriptive state/load/parameter records and structural stateful/trainable method protocols.
- Required scope: `src/rphys/methods/state.py`, `src/rphys/methods/core.py`, methods exports, package/unit/contract tests, and docstrings.
- Required checkpoints: immutable/copy-protected primitive metadata/provenance, named state entries, strict-load diagnostics, named parameter handles, trainability/update flags, no torch/helper/backend imports, and no optimizer/checkpoint/device/distributed fields.
- Acceptance criteria: non-torch fake capability implementation passes contract tests.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: Phase 1 `Method` protocol and private primitive mapping helper; Phase 2 package export/import tests.
- Existing tests or harness behavior: package tests verify scoped methods exports and import-boundary tests catch heavy optional imports.
- Import-boundary or dependency constraints: methods imports may see data containers for `Method`; state records must remain dependency-light and backend-neutral.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` and `docs/roadmap/stage-11/planning.md` changes remain outside the phase worktree.
- Dedicated branch/worktree status: created from current `origin/develop`.
- Current `develop` base: `a360675`
- Earlier phase dependency status: Phases 0-2 merged and metadata pushed.
- Push/PR infrastructure status: GitHub auth, fetch, push, PR creation, and merge verified in earlier phases.
- Stop condition if isolation cannot be maintained: mark Phase 3 blocked and stop rather than implement in the control checkout.

## In-Scope Work

- Add `StateEntry`, `StateView`, `StateLoadResult`, and `ParameterView` records.
- Add structural `StatefulMethod` and `TrainableMethod` protocols.
- Add methods package exports and package/import-boundary assertions.
- Add non-torch unit and contract tests for state, load diagnostics, and parameters.

## Out-of-Scope Work

- Optimizer factories, parameter groups, schedulers, checkpoint schemas/files, device placement/movement, distributed state, torch helpers, Lightning/Fabric integration, lifecycle hooks, and hard optional dependency imports.

## Assumptions

- State values and parameter handles may be arbitrary backend objects; metadata/provenance/diagnostics remain primitive.
- `StateLoadResult.success` is derived from missing/unexpected/incompatible names.
- Parameter handles are descriptive and do not imply optimizer grouping or device placement.

## Scope Contract

State records expose names, values/handles, primitive metadata/provenance, and load diagnostics only. Protocols expose `state()`, `load_state(state, *, strict=True)`, and `parameters()` equivalents. No record or protocol defines `.to()`, `training_step`, `validation_step`, `configure_optimizers`, precision, compile, logging, callbacks, checkpoint writers, distributed state, or device behavior.

## Scientific Contract Notes

- Sampling and temporal alignment: not affected.
- Field roles, locators, schemas, and provenance: not affected except generic provenance maps on records.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: not encoded.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not interpreted by state records.

## Design Impact

- Maintainability: records are descriptive dataclasses with local validation.
- Extensibility: Stage 12 can inspect records and add optimizer/checkpoint/device policy later.
- Lightweight import policy: no torch or backend imports.
- Source-tree boundaries: `rphys.nn` remains empty because no shared protocol helper is needed.

## Future Compatibility

Future learners/trainers can inspect state and parameters without changing method prediction semantics. Optional backend adapters can convert framework-native state later without changing Stage 10 core records.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Torch-style-only `state_dict`/`parameters()` | Excludes non-torch methods and bakes in backend policy. |
| Optimizer/checkpoint/device fields now | Stage 12 owns those semantics. |
| `rphys.nn.torch` helper | Stage 10 explicitly defers optional torch helpers. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Parameter grouping is absent | Optimizer policy is out of scope | Stage 12 defines optimizer groups |

## Reviewability

- Expected PR size and shape: one state module, core protocol additions, exports, focused tests, and phase artifacts.
- Files and areas to inspect: `src/rphys/methods/state.py`, `src/rphys/methods/core.py`, methods exports, state/contract/package tests.
- Scope-control checks: no torch/Lightning hooks, optimizer, checkpoint, device, distributed, or trainer behavior.

## Implementation Steps

1. Add immutable state/parameter/load records and validation.
2. Add structural stateful/trainable protocols.
3. Update methods package exports and import tests.
4. Add unit and non-torch contract tests.
5. Run required validation and record evidence.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `make test-package`
- Required assertions or deferral reason: methods exports remain scoped and imports lightweight.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/methods/test_state.py`
- Required assertions or deferral reason: state/parameter records and strict-load diagnostics.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_trainable_method_contract.py`, `tests/contracts/test_method_contract.py`
- Required assertions or deferral reason: non-torch fake structural behavior and unchanged base prediction semantics.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: cross-contract synthetic integration belongs to Phase 4.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no workflow runtime behavior.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no user-facing acceptance workflow is introduced.

## Risks

- Records may need additive fields once Stage 12 defines optimizer/checkpoint details.
- Public naming should stay descriptive and not imply backend lifecycle hooks.
- `rphys.nn` should not gain placeholder exports.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/methods/test_state.py
uv run pytest tests/contracts/test_trainable_method_contract.py
make test-package
uv run pytest tests/contracts/test_method_contract.py
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: state records, protocols, exports, tests.
- Tests to run with each slice: state unit tests first, trainable contract tests, package tests.
- Decisions the executor must not revisit: no torch helper, no optimizer/checkpoint/device/distributed semantics, no lifecycle hooks.
- Conditions that require stopping for the manager: need for optimizer groups, checkpoint schema, device movement, distributed state, or torch helpers.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed by manager in phase worktree.
- Final phase execution plan: this document.
- Implementation summary: added `StateEntry`, `StateView`, `StateLoadResult`, `ParameterView`, structural `StatefulMethod`/`TrainableMethod`, scoped methods exports, and non-torch unit/contract coverage.
- Implementation validation: `uv run pytest tests/unit/rphys/methods/test_state.py`, `uv run pytest tests/contracts/test_trainable_method_contract.py`, `uv run pytest tests/contracts/test_method_contract.py`, `make test-package`, `make validate-pr`, `make test-summary`, and `git diff --check` passed. `make test-summary` reported package 47 passed, unit 654 passed, contract 128 passed, integration 19 passed, and no e2e/acceptance suites present.
- Refinement summary: no implementation refinement needed after targeted validation.
- Pre-submit blocker gate: passed; no torch/helper import, optimizer/checkpoint/device/distributed policy, framework lifecycle hook, or trainer behavior blocker found.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
