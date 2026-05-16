# Phase 4 Execution Plan: Synthetic Contract Integration, Docs, And Full Validation

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v10`
- Feature focus: Stage 10 composition, docs, and final validation
- Stage descriptor: Models, Methods, And NN Base Contracts
- Phase descriptor: Synthetic Contract Integration, Docs, And Full Validation
- PR title: `Stage 10 Models, Methods, And NN Base Contracts - Phase 4: Synthetic Contract Integration, Docs, And Full Validation`
- Branch: `agent/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p4-synthetic-integration-docs-validation`
- Phase execution plan path: `docs/roadmap/stage-10/phases/synthetic-integration-docs-validation.md`
- Full plan: `docs/roadmap/stage-10/implementation-plan.md`
- Planning document: `docs/roadmap/stage-10/planning.md`
- Source phase: `Phase 4: Synthetic Contract Integration, Docs, And Full Validation`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 0-3 merged and recorded
- Draft pass: manager-local, because no subagent delegation was requested in this session
- Refine pass: not needed unless broad validation exposes a blocker
- Setup limitations: unrelated control-checkout roadmap/stage-11 docs are preserved outside this worktree
- Blockers: none

## Objective

Prove Stage 10 contracts compose with tiny synthetic objects, update public vocabulary docs, and run the full validation matrix before closing the stage.

## Full-Plan Context

Phase 4 is the closeout phase. It must not introduce concrete algorithms, real datasets, loaders, losses, metrics, learners, trainers, exporters, devices, checkpoints, or backend helpers.

## Source Phase Summary

- Goal: validate synthetic batch -> adapter -> model/method -> `MethodOutput` -> explicit apply flow, model isolation, context propagation, and backend-neutral trainable state/parameter records that are not tied to any one framework.
- Required scope: integration tests, test-only fakes, public docs/glossary if vocabulary changed, and full validation evidence.
- Required checkpoints: all accepted Stage 10 examples execute without concrete algorithms or heavy optional dependencies.
- Acceptance criteria: final validation commands pass or failures are recorded with risk.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: Phase 2 synthetic integration covers adapters/apply; Phase 3 contract tests cover trainable fakes; glossary currently defines Method/Model but not new Stage 10 record names.
- Existing tests or harness behavior: full `make validate-pr`, `make test-summary`, package/unit/contract/integration targets are available.
- Import-boundary or dependency constraints: no torch or other heavy optional import in core method/model/nn surfaces.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` and `docs/roadmap/stage-11/planning.md` changes remain outside the phase worktree.
- Dedicated branch/worktree status: created from current `origin/develop`.
- Current `develop` base: `d2f31f1`
- Earlier phase dependency status: Phases 0-3 merged and metadata pushed.
- Push/PR infrastructure status: GitHub auth, fetch, push, PR creation, and merge verified in earlier phases.
- Stop condition if isolation cannot be maintained: mark Phase 4 blocked and stop rather than implement in the control checkout.

## In-Scope Work

- Extend synthetic integration coverage so adapter/model/method/output/apply/state/parameter/context contracts compose.
- Add glossary entries for new public Stage 10 terms.
- Run focused and full validation commands.
- Record validation evidence and residual risks.

## Out-of-Scope Work

- Real datasets, concrete rPPG algorithms, neural baselines, model zoo, losses, metrics, objectives, learners, trainers, dataloaders, prediction export runners, device/GPU checks, workflow runtime, torch helpers, and edits to `docs/roadmap.md`.

## Assumptions

- Synthetic fakes are test-only and not public algorithms.
- Existing package/import tests are the authoritative heavy-import gate; compatibility with arbitrary backends is represented through opaque backend-native test objects, not a Stage 10 backend adapter.
- No acceptance tests are needed because no user workflow/runtime is introduced.

## Scope Contract

Phase 4 may add tests and docs only, plus minimal test-only fake logic inside test files. It must not change public behavior unless a validation blocker proves a small docs/error refinement is required.

## Scientific Contract Notes

- Sampling and temporal alignment: sample order is preserved in synthetic LIST collation; no resampling or alignment inference is added.
- Field roles, locators, schemas, and provenance: synthetic tests preserve declared locators, schemas, context provenance, and output patch fields.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: no policy is encoded.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: covered by earlier focused failure tests where relevant; not expanded here.

## Design Impact

- Maintainability: closes Stage 10 with a compact synthetic composition test and glossary updates.
- Extensibility: leaves Stage 11-13 and Stage 12 behavior deferred.
- Lightweight import policy: full package validation remains the dependency gate.
- Source-tree boundaries: docs/tests only unless validation requires a small fix.

## Future Compatibility

Stage 11-13 can consume method output fields and explicit application; Stage 12 can inspect state/parameter records later without optimizer/checkpoint/device policy being present now.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add a concrete baseline method | Stage 10 excludes concrete algorithms. |
| Add framework integration smoke tests | Stage 10 defers concrete backend helpers and keeps core import-light. |
| Expand into learner/trainer flow | Stage 12 owns learner/trainer semantics. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Synthetic fakes remain test-local | Avoids public fake algorithm catalog | A reusable testing-helper roadmap decision is approved |

## Reviewability

- Expected PR size and shape: docs/test closeout only.
- Files and areas to inspect: synthetic integration test, glossary, phase artifact and PR body.
- Scope-control checks: no public behavior drift, no heavy imports, no concrete algorithms.

## Implementation Steps

1. Extend synthetic integration to include state/trainable records and context with the adapter/apply flow.
2. Update glossary for public Stage 10 record/protocol vocabulary.
3. Run focused integration and full validation targets.
4. Record evidence and open the final phase PR.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `make test-package`
- Required assertions or deferral reason: exports/import boundaries after all phases.

### Unit Suite

- Status: required
- Expected paths: `make test-unit`
- Required assertions or deferral reason: all record/adapter/state coverage.

### Contract Suite

- Status: required
- Expected paths: `make test-contract`
- Required assertions or deferral reason: method/model/trainable contracts.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_synthetic_method_prediction_flow.py`, `make test-integration`
- Required assertions or deferral reason: synthetic end-to-end Stage 10 flow.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no workflow runtime behavior.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no user-facing acceptance workflow is introduced.

## Risks

- Full validation may surface unrelated failures; record exact residual risk if so.
- Glossary wording must not imply Stage 11-13 or Stage 12 behavior is implemented.
- Synthetic fakes must stay local to tests.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/integration/test_synthetic_method_prediction_flow.py
make test-package
make test-unit
make test-contract
make test-integration
make test
make test-summary
uv lock --check
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: test-local fake extension, glossary update, validation evidence.
- Tests to run with each slice: synthetic integration first, then suite targets.
- Decisions the executor must not revisit: no concrete algorithms, no torch helper, no learner/trainer/export/loss/metric behavior.
- Conditions that require stopping for the manager: required behavior cannot be expressed without changing public contracts outside Phase 4 scope.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: used once after maintainer clarification that compatibility is for arbitrary backends, not only non-torch cases.
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed by manager in phase worktree.
- Final phase execution plan: this document.
- Implementation summary: extended the synthetic method integration so adapter extraction, backend-native callable model execution, `MethodOutput`, explicit apply, `PredictionContext`, `StateView`, `StateLoadResult`, and `ParameterView` compose in one test-local flow; updated glossary and public docstrings for backend-neutral method/model/state/parameter vocabulary; repaired a model import-boundary contract test so temporary `sys.modules` removal is restored after the test.
- Implementation validation: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/methods/test_state.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_trainable_method_contract.py tests/contracts/test_model_contract.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_synthetic_method_prediction_flow.py`; `make test-package`; `make test-unit`; `make test-contract`; `make test-integration`; `make test`; `UV_CACHE_DIR=/tmp/uv-cache uv lock --check`; `make test-summary`; `git diff --check`; `make validate-pr`.
- Refinement summary: after maintainer feedback, state and parameter records now explicitly preserve opaque backend-native objects by identity and docs avoid implying that torch is the only backend pressure. Framework-specific helpers remain deferred as additive adapters.
- Pre-submit blocker gate: passed; `make test` reported 850 passed and `make test-summary` reported package 47 passed, unit 655 passed, contract 128 passed, integration 20 passed, with no e2e or acceptance suites present.
- PR preparation: ready after commit and branch push.
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none
