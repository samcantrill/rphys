# Phase 5 Execution Plan: Final Validation And Readiness

## Metadata

- Status: draft phase execution plan; expanded-path rigor included; ready for implementation
- Roadmap stage: `v6`
- Feature focus: Stage-wide validation evidence and readiness accounting for generic operations
- Stage descriptor: Operation Foundations And Functional Kernels
- Phase descriptor: Final Validation And Readiness
- PR title: `Stage 6 Operation Foundations And Functional Kernels - Phase 5: Final Validation And Readiness`
- Branch: `agent/stage-6-p5-final-validation-readiness`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p5-final-validation-readiness`
- Phase execution plan path: `docs/roadmap/stage-6/phases/final-validation-readiness.md`
- Full plan: `docs/roadmap/stage-6/implementation-plan.md`
- Planning document: `docs/roadmap/stage-6/planning.md`
- Source phase: Phase 5, `final-validation-readiness`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after local validation evidence, scope review, automated review, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; preserve this branch/worktree/base/target
- Plan quality gate: Stage 6 implementation plan approved. Expanded-path rigor is used because this phase is the final public API, import-boundary, documentation, and validation evidence gate for Stage 6. Separate refine pass is not needed unless a stop condition below is hit.
- Draft pass: completed 2026-05-14
- Refine pass: not needed before implementation
- Setup limitations: no product code, tests, broad validation, PR body, PR, or GitHub operation was run during this planning pass. The assigned worktree already existed on `agent/stage-6-p5-final-validation-readiness`; local `HEAD`, `develop`, `origin/develop`, and merge-base all resolved to `92079cd35968e052603205b8c472ad73868863f6`.
- Blockers: none before implementation

## Objective

Consolidate Stage 6 validation evidence and readiness notes without adding feature behavior: run the required stage-wide suites and hygiene checks, review public/private operation boundaries against the approved design, record exact results and residual risks, and prepare the Stage 6 implementation for review or merge.

## Full-Plan Context

Phases 1 through 4 implemented and merged the Stage 6 generic operation foundation: provisional public `rphys.ops` exports, operation contracts, runtime context/result records, plain functional-kernel vocabulary, wrapper-first `Operation` execution, ordered sequence-only `OperationPipeline`, typed operation/pipeline failures, runtime-container-as-payload evidence, and public boundary docs. Phase 5 must not add new feature modules or behavior. Its job is to prove that the merged Stage 6 surface is coherent, dependency-light, documented, and ready for review.

Future work that must remain out of scope includes Stage 7 `SampleOp`/`BatchOp` operation families, locator permission policy, named pipeline entries, and augmentation replay; Stage 8 export/save behavior and operation side-effect workflows; Stage 9 cache/materialization identity; concrete rPPG kernels; heavy optional dependencies; root `rphys` convenience exports; and placeholder future packages.

## Source Phase Summary

- Goal: consolidate Stage 6 evidence, broaden validation, and prepare the stage for review/merge.
- Required scope: validation command execution, evidence review, guardrail review, status/evidence updates, and final handoff notes only.
- Required checkpoints: `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, `git diff --check`, and `make validate-pr` as the final local gate if practical.
- Acceptance criteria: required validation results are recorded exactly, public operation exports and error exports match the approved surface, import-boundary and private-helper leakage guardrails hold, docs/docstrings/examples use package-level imports and explicit `.output`, sequence-only pipeline and declaration-only mutation/side-effect semantics remain intact, and Stage 7/8/9 deferrals remain absent and documented.

## Current Source And Harness Findings

- Current operation modules: `src/rphys/ops/__init__.py`, `contracts.py`, `context.py`, `core.py`, `kernels.py`, `pipelines.py`, and private `_validation.py`.
- Public `rphys.ops.__all__` is currently exact and code-backed: `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `Operation`, `OperationContext`, `OperationResult`, `OperationPipeline`, and `FunctionalKernel`.
- Scoped submodule exports are currently exact: `contracts.__all__` exposes `OperationRole`, `OperationMutationPolicy`, and `OperationContract`; `context.__all__` exposes `OperationContext` and `OperationResult`; `core.__all__` exposes `Operation`; `kernels.__all__` exposes `FunctionalKernel`; `pipelines.__all__` exposes `OperationPipeline`; `_validation.__all__` is empty.
- Exercised Stage 6 error exports in `rphys.errors` are `InvalidOperationContractError`, `InvalidOperationContextError`, `InvalidOperationResultError`, `InvalidOperationInputError`, `OperationExecutionError`, `InvalidOperationPipelineError`, and `OperationPipelineExecutionError`, plus the broad `RemotePhysOperationError` and `RemotePhysPipelineError` categories.
- `tests/package/test_import.py` asserts exact `rphys.ops` exports, scoped operation submodule exports, scoped Stage 6 error exports, and no root `rphys` operation re-exports. Phase 5 must additionally review no root leakage for every Stage 6 error name.
- `tests/package/test_import_boundaries.py` imports `rphys.ops` and its public submodules in a subprocess and fails if those imports load `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, `tests.support`, or heavy optional stacks.
- `OperationContract` currently exposes role, input/output type expectations, mutation policy, side effects, required context, and failure modes. Mutation and side effects are declaration/evidence vocabulary only; Stage 6 does not enforce field-level mutation permissions.
- `OperationContext` and `OperationResult` are runtime records with inspectable metadata/provenance mappings. `OperationResult.output` is the only payload field; context/result records do not carry cache keys, run IDs, input IDs, datasource identity, or export manifests.
- `Operation.run()` and `Operation.__call__()` validate context/input, call the wrapped callable with explicit `context`, preserve callable exceptions as causes, and always return `OperationResult`.
- `OperationPipeline` construction is sequence-only, stores an immutable operations tuple, validates adjacent declared types, passes one context through every step, forwards each step's `result.output`, and returns the final `OperationResult`.
- Contract coverage exists for operation construction/runtime records, execution, pipeline behavior, runtime-container payload handling, lazy `SampleField` demand behavior, no raw-output operation API, and no stable step/pipeline name APIs.
- Current test layout has package, unit, contract, and integration suites. No `tests/e2e` or `tests/acceptance` directories exist; `make test-summary` is expected to account for absent suites through the harness rather than requiring new Stage 6 e2e or acceptance tests.

## Phase Isolation State

- Control checkout dirty-state review: main checkout on `develop` had unrelated untracked `docs/roadmap/stage-7/`; this phase must not touch or depend on it.
- Dedicated branch/worktree status: assigned branch and worktree already exist at `/home/samcantrill/work/rphys-worktrees/stage-6-p5-final-validation-readiness`.
- Current `develop` base: local `HEAD`, `develop`, `origin/develop`, and merge-base all resolved to `92079cd35968e052603205b8c472ad73868863f6` before this plan edit.
- Earlier phase dependency status: Phases 1 through 4 are merged into the current base, including PR #38, #40, #42, and #44 completion records in the implementation plan.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before validation if the worktree leaves `agent/stage-6-p5-final-validation-readiness`, if unrelated dirty files appear in touched paths, if `develop` advances and invalidates the recorded Phase 1-4 operation surface, or if evidence recording requires rewriting approved planning decisions.

## In-Scope Work

- Run final validation commands from the implementation plan and capture exact pass/fail/not-present/skipped results with enough detail for review.
- Review exact `rphys.ops` public exports, scoped operation submodule exports, Stage 6 error exports, no root `rphys` operation/error exports, and no placeholder Stage 7/8/9 names.
- Review import-boundary evidence for lightweight `rphys.ops` imports: no data/datasource/IO/codec/test-support/heavy optional imports from operation modules.
- Review private-helper leakage: `_validation` must stay private, `__all__` must remain empty, docs/tests must not present private helpers as public API, and any direct private-helper testing must remain out of scope.
- Review docs/docstrings/examples for package-level `from rphys.ops import ...` imports, explicit `OperationResult.output` unwrapping, sequence-only pipeline construction, mutation/side-effect declaration limits, runtime payload boundary, and Stage 7/8/9 deferrals.
- Record validation evidence and residual risk in `docs/roadmap/stage-6/implementation-plan.md` only if the implementation workflow requires status/evidence updates for Phase 5.
- Optionally create `docs/roadmap/stage-6/phases/final-validation-readiness-pr-body.md` as a PR-ready handoff artifact with behavior, scientific contract implications, validation evidence, assumptions, accepted deferrals, and residual risks.
- Leave `docs/roadmap/stage-6/planning.md` untouched unless the workflow explicitly requires a small handoff/status update.

## Out-of-Scope Work

- New feature modules, public APIs, public re-exports, errors, registries, protocols, operation base classes, raw-output helpers, placeholder future packages, or root `rphys` exports.
- Source or test changes by default. If validation uncovers a concrete blocker, stop and get explicit manager assignment before any source/test/doc behavior fix.
- Behavior changes to `Operation`, `OperationContract`, `OperationContext`, `OperationResult`, `OperationPipeline`, runtime containers, data/datasource/IO modules, codec behavior, or Stage 5 identity/manifest behavior.
- Queue reopening, design-policy rewrites, or implementation-plan reshaping without a concrete contradiction.
- Stage 7 `SampleOp`/`BatchOp`, locator permissions, named pipeline entries, export/save behavior, cache/materialization identity, workflow provenance, concrete kernels, real datasets, hardware/GPU/network acceptance checks, and broad tutorials.
- Unrelated dirty-file cleanup, updates to `docs/roadmap/stage-5`, or edits to the untracked Stage 7 work in the main checkout.

## Assumptions

- Phases 1 through 4 are present in `develop` and are the source of truth for Stage 6 behavior.
- Phase 5 validation runs from this clean dedicated worktree, not from the main checkout with unrelated untracked work.
- E2E and acceptance suites are currently absent; this is an expected Stage 6 state unless the test harness reports otherwise.
- `make validate-pr` is practical if the environment can build distributions locally. If it fails for environment-only reasons, record the exact failure and run the individual required checks that are still available.
- Evidence recording may update implementation-plan Phase 5 status/results and an optional PR body artifact, but this planning pass commits only this phase execution plan.

## Scope Contract

Phase 5 has no default public behavior contract changes. The executor must validate the implemented Stage 6 contract rather than redesign it: users import provisional operation names from `rphys.ops`, not root `rphys`; wrapped execution returns `OperationResult`; users unwrap payloads through `.output`; pipelines are ordered sequences only; `OperationContext`/`OperationResult` provenance is runtime inspectable metadata, not durable identity; mutation and side effects are declarations/evidence, not field-level enforcement.

Module boundaries must remain unchanged. `src/rphys/ops` may depend on stdlib, `rphys.errors`, and local operation modules, but it must not import data, datasource, IO, codec, test-support, array, plotting, deep-learning, or dataset-SDK stacks. Private helpers remain implementation details. Documentation may mention public operation imports and behavior, but must not bless private modules or implementation submodules as stable public API.

If validation finds behavior that contradicts the approved design, the executor must stop for manager review before applying a fix. A fix inside this phase requires an explicit manager assignment, must be limited to the blocker, and must rerun the affected package/unit/contract/integration suites plus final checks.

## Scientific Contract Notes

- Sampling and temporal alignment: Phase 5 does not add or modify sampling, alignment, padding, resampling, temporal slicing, invalid-rate, or windowing behavior. Runtime-boundary evidence may mention existing `SampleField` demand behavior only as Stage 6 validation evidence.
- Field roles, locators, schemas, and provenance: operations must not add locator permissions, schema conversion, datasource identity, manifest fingerprints, or cache keys. `OperationContext.provenance` and `OperationResult.provenance` remain inspectable runtime mappings.
- Masking, filtering, normalization, and aggregation order: no signal processing kernels, filtering, normalization, aggregation, CHROM/POS, or model behavior is introduced or validated beyond absence from Stage 6 scope.
- Subject identity, splits, leakage, and grouping: no subject, split, record, grouping, leakage, or datasource-view policy changes are in scope. Required context keys remain generic metadata keys only.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: Phase 5 does not add numerical edge-case policy. It must confirm that operation failures remain typed and fail loud for the implemented generic contracts without inventing signal-specific semantics.

## Design Impact

- Maintainability: this phase creates a reviewable evidence checkpoint for Stage 6 without expanding the implementation surface.
- Extensibility: preserving generic `Operation` and sequence-only `OperationPipeline` leaves specialized Stage 7/8/9 capabilities additive and explicit.
- Lightweight import policy: final package/import validation must prove `rphys.ops` remains dependency-light and does not couple to runtime containers, codecs, datasources, or heavy optional stacks.
- Source-tree boundaries: default write scope is limited to the Stage 6 implementation plan evidence/status and an optional PR body artifact; source/tests are blocked unless explicitly assigned after a concrete validation failure.

## Future Compatibility

- Stage 7 can add `SampleOp`, `BatchOp`, locator permissions, named pipeline entries, and richer runtime operation families without treating Stage 6 generic operations as specialized container policies.
- Stage 8 can define export/save operations, artifacts, and side-effect workflows without treating `side_effect_evidence` as an export result schema.
- Stage 9 can define cache/materialization identity without treating Stage 6 context/result provenance as cache keys, manifests, or durable identity.
- Later workflow/runtime stages can add routing, retries, resume, DAGs, and artifact handling without changing the Stage 6 sequence-only pipeline contract.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add new validation tests or source guardrails proactively | Phase 5 is validation and evidence only; test/source changes require a concrete validation blocker and manager assignment. |
| Treat final validation as a broad cleanup phase | Cleanup invites unrelated churn and hidden behavior changes; the approved phase owns evidence, guardrails, and residual risk accounting. |
| Run only `make validate-pr` | The implementation plan specifically requires individual package, unit, contract, integration, summary, lock, and diff evidence, with `validate-pr` as a final gate if practical. |
| Convert Stage 6 docs into a tutorial | Phase 4 documented public boundaries; Phase 5 should review and record evidence, not expand user education or future-stage promises. |
| Record Stage 6 provenance as cache/export identity | Cache/materialization/export identity belongs to later stages and would violate locked deferrals. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Final evidence may live in the implementation plan and optional PR body rather than a generated validation database | Existing roadmap workflow uses durable Markdown artifacts for phase evidence. | Test harness grows a first-class validation ledger or release readiness artifact. |
| E2E and acceptance suites remain absent for Stage 6 | Stage 6 provides generic operation primitives without real datasets, hardware, or downstream workflows. | A later stage adds end-to-end operation workflows, export flows, or real-data acceptance criteria. |
| Manual boundary review supplements automated package tests | Some risks are wording and future-scope implications that are hard to encode safely without overfitting tests. | Repeated helper/public leakage or docs drift justifies focused automated checks. |

## Reviewability

- Expected PR size and shape: small validation/evidence PR. Default file changes are `docs/roadmap/stage-6/implementation-plan.md` for Phase 5 status/evidence and optionally `docs/roadmap/stage-6/phases/final-validation-readiness-pr-body.md`; source/tests/docs behavior files should be unchanged unless a blocker fix is separately approved.
- Files and areas to inspect: `src/rphys/ops/__init__.py`, `contracts.py`, `context.py`, `core.py`, `kernels.py`, `pipelines.py`, `_validation.py`; `src/rphys/errors.py`; `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`; `tests/unit/rphys/ops/`; `tests/contracts/test_operation_contract.py`; `tests/contracts/test_operation_execution_contract.py`; `tests/contracts/test_operation_pipeline_contract.py`; `tests/contracts/test_operation_runtime_boundary_contract.py`; `tests/integration/`; operation module docstrings and Stage 6 roadmap artifacts.
- Scope-control checks: no source/test/doc behavior edits by default; no new public names; no private helper exposure; no root exports; no heavy imports; no Stage 7/8/9 behavior; no edits outside Stage 6 evidence artifacts unless explicitly approved.

## Implementation Steps

1. Reconfirm phase isolation and scope before validation: `git status --short --branch`, current branch, base/target, and changed paths. Stop if unrelated dirty files appear in Stage 6 evidence paths or if the worktree no longer targets `develop`.
2. Run the required validation commands individually and capture exact results: `make test-package`, `make test-unit`, `make test-contract`, `make test-integration`, `make test-summary`, `uv lock --check`, and `git diff --check`.
3. Run the manual evidence review checklist against the current tree: exact `rphys.ops` exports, exact Stage 6 error exports, no root operation/error exports, scoped submodule exports, empty private helper exports, import-boundary coverage, package-level docs/examples, explicit `.output`, sequence-only pipeline, mutation/side-effect declaration limits, runtime payload boundary, and Stage 7/8/9 deferrals.
4. Record validation evidence and residual risks in the active Stage 6 implementation artifact if required, and prepare an optional PR body artifact with behavior summary, scientific contract implications, validation table, assumptions, accepted deferrals, and open risks.
5. Run `make validate-pr` as the final gate if practical. If it is not practical or fails for environment-only reasons, record the exact limitation and the successful individual checks; do not mask a real validation failure.
6. Stop for manager review instead of fixing by default if any required validation fails, a public/private boundary contradiction appears, private helper leakage cannot be resolved within Phase 5 scope, or a planning/design decision needs reopening.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: confirm exact `rphys.ops` public exports, exact operation submodule `__all__` values, Stage 6 error exports, no root `rphys` operation exports, no root error exports including all Stage 6 operation/pipeline error names, no placeholder future names, no duplicate vocabulary leakage, and lightweight imports that avoid data/datasource/IO/codec/test-support/heavy optional stacks.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_contracts.py`; `tests/unit/rphys/ops/test_context.py`; `tests/unit/rphys/ops/test_core.py`; `tests/unit/rphys/ops/test_kernels.py`; `tests/unit/rphys/ops/test_pipelines.py`; `tests/unit/rphys/test_errors.py` as error-taxonomy evidence if needed
- Required assertions or deferral reason: confirm exact contract fields, immutable/copying behavior, typed construction failures, context/result runtime record semantics, callable wrapping, result validation, cause preservation, functional-kernel alias behavior, sequence-only pipeline storage/execution, context propagation, `result.output` forwarding, and side-effect evidence limits.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_contract.py`; `tests/contracts/test_operation_execution_contract.py`; `tests/contracts/test_operation_pipeline_contract.py`; `tests/contracts/test_operation_runtime_boundary_contract.py`; `tests/contracts/test_runtime_core_contract.py` as runtime evidence
- Required assertions or deferral reason: confirm public operation records do not expose deferred fields, `Operation.run()` and `__call__` return `OperationResult`, explicit `.output` is required, no raw-output operation API exists, context requirements use metadata only, pipeline public API is sequence-only, no stable step/name APIs are exposed, runtime `Sample`/`Batch` payloads remain ordinary inputs/outputs, and lazy `SampleField` materialization remains demand-driven by runtime APIs.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/`
- Required assertions or deferral reason: run the existing integration suite as stage-wide regression evidence. Phase 5 should not add integration tests unless a validation blocker is found and the manager assigns a fix.

### E2E Suite

- Status: deferred/not present
- Expected paths: none currently
- Required assertions or deferral reason: Stage 6 does not define an end-to-end operation workflow through real datasources, export/save paths, cache/materialization paths, or downstream projects. `make test-summary` should record absent e2e coverage; do not create e2e tests during this validation-only phase.

### Acceptance Suite

- Status: deferred/not present
- Markers affected: none
- Required assertions or deferral reason: no real data, hardware, GPU, network, optional dependency, or long-running acceptance scenario is part of Stage 6. Acceptance evidence is the local validation/readiness record, not new acceptance tests.

## Risks

- A required suite could fail for an unrelated pre-existing issue; record exact evidence and stop unless the manager assigns a fix.
- `make validate-pr` also builds distributions; a packaging/environment failure must be distinguished from package/unit/contract/integration behavior failures.
- Root error leakage may be under-asserted compared with operation-name leakage; manual review must cover every Stage 6 error name.
- Docs or docstrings could imply private helpers, stable implementation submodule imports, locator permissions, export/cache identity, or future operation families even while code remains correct.
- The main checkout has unrelated untracked Stage 7 work; validation and evidence must stay inside the Phase 5 worktree.

## Validation Commands

Targeted development and evidence commands:

```sh
git status --short --branch
make test-package
make test-unit
make test-contract
make test-integration
make test-summary
uv lock --check
git diff --check
```

Manual evidence review commands:

```sh
rg -n "_validation|coerce_|from rphys\\.ops\\._|import rphys\\.ops\\._" docs src/rphys tests
rg -n "SampleOp|BatchOp|run_raw|execute_raw|call_raw|cache|export|workflow|locator permission|Stage 7|Stage 8|Stage 9" src/rphys/ops tests/package tests/unit/rphys/ops tests/contracts docs/roadmap/stage-6
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: isolation check; required validation commands; manual evidence review; evidence/status artifact update; optional PR body artifact; final gate.
- Tests to run with each slice: package suite after public/import review; unit suite after operation-source evidence review; contract suite after public behavior and runtime-boundary review; integration suite after contract validation; `make test-summary`, `uv lock --check`, `git diff --check`, and practical `make validate-pr` before handoff.
- Decisions the executor must not revisit: no source/test behavior changes by default; package-level `rphys.ops` imports only; no root exports; explicit `.output`; sequence-only pipeline; mutation/side effects are declarations/evidence only; runtime containers are ordinary payloads; Stage 7/8/9 deferrals remain out of scope.
- Conditions that require stopping for the manager: failed required validation without a documented and approved risk; design contradiction; helper/public API leakage that cannot be fixed inside validation scope; need to add behavior, public names, tests, or docs beyond evidence updates; need to reopen implementation-plan decisions.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: this artifact unless a refinement trigger is hit
- Implementation summary: validation/evidence-only phase completed without source,
  test, or public API behavior changes. Reviewed Stage 6 public exports, scoped
  submodule exports, Stage 6 error exports, root-export absence, private-helper
  boundaries, lightweight import guardrails, docs/docstring wording, explicit
  `.output` behavior, sequence-only pipeline semantics, declaration-only
  mutation/side-effect wording, runtime payload boundary evidence, and Stage
  7/8/9 deferrals.
- Implementation validation: `make test-package` (29 passed), `make test-unit`
  (416 passed), `make test-contract` (73 passed), `make test-integration` (3
  passed), `make test-summary` (package 29 passed, unit 416 passed, contract 73
  passed, integration 3 passed, e2e/acceptance not present),
  `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` (passed after uncached
  `uv lock --check` hit read-only home cache), `git diff --check` (passed),
  and `make validate-pr` (package 29 passed, unit 416 passed, contract 73
  passed, integration 3 passed, e2e/acceptance not present; `uv lock --check`,
  `uv build`, and `git diff --check` passed).
- Refinement summary: none
- Pre-submit blocker gate: passed
- PR preparation: completed in
  `docs/roadmap/stage-6/phases/final-validation-readiness-pr-body.md`
- Automated review: completed; no blocking findings. Residual non-blocking
  observation: package tests manually cover exact `rphys.ops` root-export
  absence and most Stage 6 root error absence, while two concrete Stage 6
  operation errors are not included in that root-error loop; manual review
  verified all seven concrete Stage 6 operation/pipeline errors are absent from
  root `rphys`.
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known
