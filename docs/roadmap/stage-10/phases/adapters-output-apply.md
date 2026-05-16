# Phase 2 Execution Plan: Adapter Specs And Explicit Output Application

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v10`
- Feature focus: method input/output adapters and explicit patch application
- Stage descriptor: Models, Methods, And NN Base Contracts
- Phase descriptor: Adapter Specs And Explicit Output Application
- PR title: `Stage 10 Models, Methods, And NN Base Contracts - Phase 2: Adapter Specs And Explicit Output Application`
- Branch: `agent/stage-10-method-model-contracts-p2-adapters-output-apply`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p2-adapters-output-apply`
- Phase execution plan path: `docs/roadmap/stage-10/phases/adapters-output-apply.md`
- Full plan: `docs/roadmap/stage-10/implementation-plan.md`
- Planning document: `docs/roadmap/stage-10/planning.md`
- Source phase: `Phase 2: Adapter Specs And Explicit Output Application`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 0 and 1 merged and recorded
- Draft pass: manager-local, because no subagent delegation was requested in this session
- Refine pass: not needed unless validation exposes merge/apply ambiguity
- Setup limitations: unrelated control-checkout roadmap/stage-11 docs are preserved outside this worktree
- Blockers: none

## Objective

Implement explicit adapters between `Batch`/`FieldLocator` fields and named method/model inputs/outputs, plus a standalone `MethodOutput` patch application helper with documented copy and conflict behavior.

## Full-Plan Context

Phase 2 builds on Phase 1 core contracts. Phase 3 state/trainable records and Phase 4 synthetic integration must not be implemented here except where a minimal synthetic flow is needed to validate adapter/apply composition.

## Source Phase Summary

- Goal: add `MethodInputSpec`, `MethodOutputSpec`, `MethodInputAdapter`, `MethodOutputAdapter`, and explicit `apply_method_output`.
- Required scope: `src/rphys/methods/adapters.py`, output helper colocated with `MethodOutput`, methods exports, adapter/output unit tests, method contract adapter probe, and focused synthetic integration.
- Required checkpoints: construction-time locator parsing, duplicate name/locator checks, optional type/schema checks, output role validation, model result arity/name checks, fail-loud missing/extra outputs, and no hidden mutation/export/training behavior.
- Acceptance criteria: synthetic echo flow extracts batch fields, maps outputs to field patches, and applies patches only through the explicit helper.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `Batch` exposes `require`, `field`, `has`, `set_field`, `shallow_copy`, and field-item APIs; `MethodOutput` already normalizes patch fields.
- Existing tests or harness behavior: Phase 1 output tests assert patch-like non-`Batch` behavior; package tests verify scoped methods exports and heavy-import boundaries.
- Import-boundary or dependency constraints: adapters may import runtime data containers; models remain below `Batch`; no torch or framework imports.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` and `docs/roadmap/stage-11/planning.md` changes remain outside the phase worktree.
- Dedicated branch/worktree status: created from current `origin/develop`.
- Current `develop` base: `9c3e589`
- Earlier phase dependency status: Phases 0 and 1 merged and metadata pushed.
- Push/PR infrastructure status: GitHub auth, fetch, push, PR creation, and merge verified in earlier phases.
- Stop condition if isolation cannot be maintained: mark Phase 2 blocked and stop rather than implement in the control checkout.

## In-Scope Work

- Add frozen input/output spec records with construction-time locator normalization.
- Add input adapter extraction from `Batch` to named payload mappings.
- Add output adapter conversion from named model results to `MethodOutput`.
- Add explicit `apply_method_output` with shallow-copy default and `error`/`replace` conflict policy.
- Add unit/contract/integration/package tests for adapters, apply behavior, and import boundaries.

## Out-of-Scope Work

- Public schema language, datasource/dataloader access, model input/output records, file export, metric/loss computation, trainer-owned result schemas, device movement, and shared public validation registries.

## Assumptions

- Input adapters return payloads rather than `FieldValue` objects because models stay below runtime containers.
- Output adapters accept mappings by declared names, sequences by spec order, and single raw values only for one-output specs.
- `apply_method_output` uses shallow copies by default to avoid copying tensor-like payloads.

## Scope Contract

Adapter specs are frozen, normalize string locators to `FieldLocator`, and validate names, duplicate locators, roles, optional expected Python payload types, and optional schemas. `MethodOutput` remains patch-only. Patch application is a separate helper and never runs from `Method.predict` implicitly.

## Scientific Contract Notes

- Sampling and temporal alignment: no resampling, alignment, filtering, masking, or normalization behavior is introduced.
- Field roles, locators, schemas, and provenance: declared locators and schemas are preserved or fail loudly; output roles are limited to prediction/output fields.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: no identity or split policy is added.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: adapters validate declared field presence/type/schema only; payload semantics remain caller-owned.

## Design Impact

- Maintainability: adapter validation stays local to `rphys.methods`.
- Extensibility: Stage 11 can revisit selector/spec reuse if identical semantics repeat.
- Lightweight import policy: no optional backend imports.
- Source-tree boundaries: methods bridge runtime fields; models remain container-agnostic.

## Future Compatibility

Stage 13 can use explicit patch application/conversion without Stage 10 implementing export or result writers. Stage 12 can compose adapters around models without changing the base `Model` protocol.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Hidden `predict` mutation | Violates patch-only DQ-2 semantics and makes provenance harder to inspect. |
| Public selector registry/schema language | Premature until losses/metrics/prediction runners repeat the same selector semantics. |
| Model access to `Batch` | Violates model-below-runtime-container boundary. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Private adapter validation helpers remain local | Only methods need these semantics now | Stage 11/13 duplicate selector/spec behavior |

## Reviewability

- Expected PR size and shape: one adapter module, one output helper update, exports, focused tests, and phase artifacts.
- Files and areas to inspect: `src/rphys/methods/adapters.py`, `src/rphys/methods/output.py`, methods exports, adapter/output/contract/integration/package tests.
- Scope-control checks: no datasource, trainer, export, loss, metric, backend, or public registry behavior.

## Implementation Steps

1. Add adapter spec records and construction validation.
2. Add input/output adapter extraction and result mapping.
3. Add explicit patch application helper and conflict policy tests.
4. Update package exports/import tests.
5. Add contract and synthetic integration coverage, then run required validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `make test-package`
- Required assertions or deferral reason: methods exports remain scoped and imports lightweight.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/methods/test_adapters.py`, `tests/unit/rphys/methods/test_output.py`
- Required assertions or deferral reason: specs, extraction, output mapping, failures, and explicit apply behavior.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_method_contract.py`
- Required assertions or deferral reason: adapter-backed method behavior and non-mutation default.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_synthetic_method_prediction_flow.py`
- Required assertions or deferral reason: synthetic batch -> adapter -> model/method -> patch -> explicit apply flow.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no workflow runtime behavior.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no user-facing acceptance workflow is introduced.

## Risks

- Adapter specs could overgrow into a schema language; keep type/schema checks narrow.
- Apply helper could hide mutation; default must copy and conflict behavior must be explicit.
- Failure diagnostics should name selectors/outputs without broad public error taxonomy.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/methods/test_adapters.py
uv run pytest tests/unit/rphys/methods/test_output.py
uv run pytest tests/contracts/test_method_contract.py
uv run pytest tests/integration/test_synthetic_method_prediction_flow.py
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

- Safe implementation slices: specs, adapters, apply helper, exports/tests.
- Tests to run with each slice: adapter unit tests first, output tests, method contract, integration, package.
- Decisions the executor must not revisit: patch-only output, explicit apply, no hidden mutation, no model `Batch`, no public registry.
- Conditions that require stopping for the manager: datasource/dataloader access, direct export, default mutation, or a need for public schema language.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed by manager in phase worktree.
- Final phase execution plan: this document.
- Implementation summary: added input/output adapter specs, input/output adapters, explicit `apply_method_output`, scoped methods exports, adapter-backed method contract coverage, and synthetic prediction integration.
- Implementation validation: `uv run pytest tests/unit/rphys/methods/test_adapters.py`, `uv run pytest tests/unit/rphys/methods/test_output.py`, `uv run pytest tests/contracts/test_method_contract.py`, `uv run pytest tests/integration/test_synthetic_method_prediction_flow.py`, `make test-package`, `make test-unit`, `make validate-pr`, `make test-summary`, and `git diff --check` passed. `make test-summary` reported package 47 passed, unit 649 passed, contract 124 passed, integration 19 passed, and no e2e/acceptance suites present.
- Refinement summary: added `tests/unit/rphys/methods/__init__.py` to avoid a pytest module-name collision with existing datasource adapter unit tests.
- Pre-submit blocker gate: passed; no hidden mutation, model `Batch` import, datasource/loader access, export/loss/metric/trainer behavior, or public selector registry blocker found.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
