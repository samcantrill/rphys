# Phase 1 Execution Plan: Public Schemas, Imports, And Errors

## Metadata

- Status: draft pass complete; refinement required before implementation
- Roadmap stage: `v6`
- Feature focus: Operation foundations public schema, import, and error boundary
- Stage descriptor: Operation Foundations And Functional Kernels
- Phase descriptor: Public Schemas, Imports, And Errors
- PR title: `Stage 6 Operation Foundations And Functional Kernels - Phase 1: Public Schemas, Imports, And Errors`
- Branch: `agent/stage-6-p1-public-schemas-imports-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p1-public-schemas-imports-errors`
- Phase execution plan path: `docs/roadmap/stage-6/phases/public-schemas-imports-errors.md`
- Full plan: `docs/roadmap/stage-6/implementation-plan.md`
- Planning document: `docs/roadmap/stage-6/planning.md`
- Source phase: Phase 1, `public-schemas-imports-errors`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after required refinement, implementation review, focused local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; do not create a new worktree
- Plan quality gate: Stage 6 implementation plan approved; this phase plan needs one refinement pass because public API, schema, error, and import-boundary decisions are high risk
- Draft pass: completed 2026-05-14
- Refine pass: pending / required
- Setup limitations: no product code, tests, PR body, or PR opened during this planning pass; no network refresh performed
- Blockers: none known before required refinement

## Objective

Establish the smallest code-backed provisional `rphys.ops` schema and kernel vocabulary needed by later Stage 6 execution phases while keeping public imports exact, lightweight, and free of deferred Stage 7/8/9 concepts.

## Full-Plan Context

Phase 1 creates the schema/context/kernel declarations that Phase 2 will use for the concrete `Operation` wrapper and Phase 3 will use for ordered pipeline composition. It must leave execution, pipeline, runtime-container examples, docs expansion, and final validation to later phases. The public names and fields chosen here are hard to remove, so the phase must prefer a narrow implemented surface over placeholder exports.

## Source Phase Summary

- Goal: establish the code-backed provisional `rphys.ops` public surface and minimal declaration records before execution behavior depends on them.
- Required scope: `OperationRole`, `OperationContract`, `OperationContext`, `OperationResult`, broad `FunctionalKernel` vocabulary, immutable or shallow-immutable normalization, exact package exports, private validators only if useful, and exercised concrete operation errors only if this phase tests them.
- Required checkpoints: package/export checks, import-boundary checks, unit tests for contract/context/result construction, contract tests for public schema semantics and deferred-field absence, and `git diff --check`.
- Acceptance criteria: no deferred fields, no root re-exports, no placeholder future names, no heavy/IO/datasource imports, no public Protocol/base, no private helper leakage, and no operation or pipeline execution behavior.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/ops/__init__.py` currently has a docstring and empty `__all__`; `src/rphys/errors.py` already exposes broad `RemotePhysOperationError` and `RemotePhysPipelineError` bases plus exercised earlier-stage concrete errors.
- Existing tests or harness behavior: `tests/package/test_import.py` treats `rphys.ops` as a deferred package with empty public surface today; `tests/package/test_import_boundaries.py` verifies lightweight imports and forbidden workflow/artifact packages; unit tests mirror `src/rphys` under `tests/unit/rphys`; contract tests live under `tests/contracts`.
- Import-boundary or dependency constraints: importing `rphys.ops` and any new `rphys.ops` implementation modules must not load optional heavy stacks (`av`, `cv2`, `matplotlib`, `numpy`, `pandas`, `scipy`, `torch`), `rphys.io`, `rphys.datasources`, `tests.support`, or workflow/artifact packages.

## Phase Isolation State

- Control checkout dirty-state review: `git status --short --branch` showed a clean worktree on `agent/stage-6-p1-public-schemas-imports-errors` before plan edits.
- Dedicated branch/worktree status: existing branch and worktree verified at `/home/samcantrill/work/rphys-worktrees/stage-6-p1-public-schemas-imports-errors`.
- Current `develop` base: local `HEAD`, `origin/develop`, and `develop` all resolved to `525c1fa` during this draft pass.
- Earlier phase dependency status: none; this is Phase 1.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before implementation if the worktree is not on the assigned branch, if unrelated dirty files appear in touched paths, or if the branch is no longer based on the intended `develop` revision.

## In-Scope Work

- Add focused `rphys.ops` implementation-home modules for schema/context/kernel vocabulary, likely `contracts.py`, `context.py`, `kernels.py`, and optional private `_validation.py`.
- Update `src/rphys/ops/__init__.py` to re-export only implemented Phase 1 provisional names.
- Implement a minimal `OperationContract` declaration shape covering role, optional input/output type expectations, mutation policy, side-effect labels, required context keys, and failure-mode labels.
- Implement runtime-only `OperationContext` and `OperationResult` records with inspectable metadata/provenance mappings, output, operation identity/role, and side-effect evidence as needed.
- Add broad `FunctionalKernel` callable vocabulary without a registry, fixed scientific signature, hidden context requirement, public Protocol/base, or container dependency.
- Add concrete errors in `src/rphys/errors.py` only when a Phase 1 public failure exercises and tests the name; otherwise keep existing broad bases unchanged.
- Add package, unit, and contract tests that prove exact exports, lightweight imports, schema/context/result validation, deferred-field absence, and any exercised concrete error inheritance.

## Out-of-Scope Work

- `Operation` wrapper execution, `.run()`, `__call__`, callable invocation, output validation after execution, and raw-output API decisions.
- `OperationPipeline`, adjacent compatibility validation, step-aware pipeline errors, context propagation through steps, DAGs, routing, retries, or resume behavior.
- SampleOp, BatchOp, transforms, augmentations, checks, locator read/write/delete permissions, BatchOp equivalence, RNG replay, and ordered mapping/named-entry pipeline construction.
- Export/save operations, datasource scans, indexes, manifests, cache/materialization keys, workflow/artifact runtimes, trainer/data-loader behavior, and durable serialization.
- Concrete rPPG kernels, CHROM/POS/model preprocessing, optional array/video/deep-learning dependencies, real datasets, and acceptance-suite fixtures.
- Root `rphys` re-exports, placeholder Stage 7/8 packages or names, public registries, public helper modules, and tests or docs importing private helpers directly.

## Assumptions

- Exact field names may be selected during implementation, but the semantic field set must not exceed the approved minimal categories.
- Mutation policy spelling may be chosen during implementation if it can express pure/new-output, may-mutate, and side-effecting behavior without field locators.
- `FunctionalKernel` can be a broad typing/documentation alias or similarly lightweight vocabulary, but it must not become a registry, mandatory inheritance surface, or container-aware Protocol.
- If invalid contract/context/result construction can be expressed cleanly with existing broad `RemotePhysOperationError`, no new concrete error name is required in this phase.

## Scope Contract

Phase 1 changes public behavior only by making implemented Phase 1 `rphys.ops` names importable from the package and by defining their construction/validation contracts. `OperationContract` must be a small inspectable declaration record with a role, optional runtime type expectations, mutation policy, side-effect labels, required context keys, and failure-mode labels. It must reject invalid declarations loudly and must not include deterministic/randomness fields, field locators, export targets, cache keys, datasource identity, workflow IDs, run IDs, tags, durable serialization controls, algorithm-specific schemas, or Stage 7/8 context fields.

`OperationContext` and `OperationResult` must be runtime-inspectable records, not durable artifact schemas. They may preserve shallow-copied metadata/provenance mappings and result side-effect evidence, but they must not promise primitive serialization, define identity/cache semantics, or settle Stage 5 manifest/fingerprint policy. Public tests should assert observable construction, normalization, immutability/copy behavior, and absence of deferred fields through public APIs only.

Concrete errors are public API. Add only names that are directly exercised by Phase 1 construction or validation behavior and export them from `rphys.errors` only with matching package/unit coverage. Do not add pipeline errors in this phase unless pipeline behavior somehow becomes part of approved Phase 1 scope, which should instead stop for review.

## Scientific Contract Notes

- Sampling and temporal alignment: no signal sampling, alignment, resampling, filtering, or temporal-slice behavior is implemented in this phase; examples must stay synthetic and stdlib-only.
- Field roles, locators, schemas, and provenance: operation records may carry generic metadata/provenance mappings, but must not introduce field-locator permissions, schema conversion, datasource identity, or manifest semantics.
- Masking, filtering, normalization, and aggregation order: no numerical processing order is implemented; `FunctionalKernel` only documents the plain-callable boundary that later kernels must respect.
- Subject identity, splits, leakage, and grouping: no subject, split, grouping, or leakage policy is introduced; do not add identity-like context/result fields.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: no signal validation is introduced; Phase 1 failure behavior is limited to invalid declarations, invalid context/result construction, and unsupported schema fields.

## Design Impact

- Maintainability: focused implementation-home modules keep schema/context/kernel concerns separated before execution and pipeline behavior land.
- Extensibility: a narrow schema leaves additive room for Stage 7 SampleOp/BatchOp locator permissions, Stage 8 export result adapters, and Stage 9 cache/materialization identity.
- Lightweight import policy: `rphys.ops` must depend only on stdlib typing/dataclasses/enums/collections-style modules and `rphys.errors`; importing data, IO, datasource, test-support, or heavy optional stacks is a blocker.
- Source-tree boundaries: Stage 6 Phase 1 may touch `src/rphys/ops`, `src/rphys/errors.py`, package tests, unit ops/error tests, and operation contract tests only.

## Future Compatibility

- Keep `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, export/save operation names, and specialized context/result names absent until their phases implement them.
- Keep public Protocol/base-class and `OperationLike` surfaces deferred until repeated custom-operation-object needs are proven.
- Keep deterministic/randomness declarations deferred until Stage 7/8 operation families require RNG replay or stochastic provenance.
- Keep runtime-only metadata/provenance mappings from becoming cache keys, manifests, export summaries, or workflow IDs.
- Keep private validators local and replaceable so later operation families can reuse public contracts without depending on helper internals.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Export placeholder `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, or export names now | Public names must be code-backed and tested; later phases own execution, pipelines, and specialized operations. |
| Add deterministic/randomness or locator fields to `OperationContract` | These fields are explicitly deferred to later concrete operation families and would pre-lock Stage 7/8 policy. |
| Make `OperationContext`/`OperationResult` durable serialization or identity schemas | Generic operation records must not settle Stage 5/8/9 cache, manifest, export, or workflow identity contracts. |
| Add a broad public error taxonomy up front | Placeholder errors create public API churn; concrete errors must be exercised by this phase's public failures. |
| Test or document private validation helpers directly | Helper leakage would freeze internals and undermine DD-10's private-helper approval. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Exact mutation policy spelling remains an implementation choice within approved semantics | The roadmap locks behavior but leaves spelling to the implementation pass; the refine pass should pressure-test the chosen public shape before code lands. | Implementation cannot express pure/new-output, may-mutate, and side-effecting behavior generically without extra public fields. |
| Kernel purity cannot be proven statically by a broad callable vocabulary | A broad callable boundary preserves scientific reuse and avoids false rigidity; import-boundary tests and docs carry the guardrail. | A later concrete kernel family needs a narrower verified protocol or repeated misuse appears in examples/tests. |

## Reviewability

- Expected PR size and shape: small public API/schema PR with new `src/rphys/ops` schema modules, exact package exports, focused error edits only if exercised, and package/unit/contract tests.
- Files and areas to inspect: `src/rphys/ops/__init__.py`, `src/rphys/ops/contracts.py`, `src/rphys/ops/context.py`, `src/rphys/ops/kernels.py`, optional `src/rphys/ops/_validation.py`, `src/rphys/errors.py`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/unit/rphys/ops/`, `tests/unit/rphys/test_errors.py`, and `tests/contracts/test_operation_contract.py`.
- Scope-control checks: exact `__all__`, no root re-exports, no private helper imports in tests/docs, no deferred fields, no execution/pipeline behavior, no IO/datasource/heavy imports, and no unexercised public errors.

## Implementation Steps

1. Define the Phase 1 public schema/context/kernel records and any private validators in focused `rphys.ops` modules without importing data, IO, datasource, or heavy optional packages.
2. Re-export only implemented Phase 1 names from `rphys.ops.__init__` and update package tests to assert exact public names and absence of placeholder future names.
3. Implement declaration/context/result validation and normalization through public constructors, keeping metadata/provenance shallow-copied or immutable enough to prevent caller mutation surprises.
4. Add concrete operation errors only for Phase 1 failures that need public catchability, with inheritance/export tests; otherwise leave `src/rphys/errors.py` broad bases unchanged.
5. Add unit and contract coverage for valid/invalid schema construction, mutation/side-effect declarations, required context keys, result metadata/provenance, deferred-field absence, and private-helper non-leakage through public behavior.
6. Run the focused Phase 1 validation commands and stop for review if any required behavior needs execution, pipeline, identity, deterministic/randomness, locator, serialization, or private-helper public exposure.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact `rphys.ops.__all__` for implemented Phase 1 names; no root `rphys` re-exports; no placeholder `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, export/save, or Stage 7/8 names unless code-backed in this phase; `rphys.ops` and implemented submodules do not load heavy optional modules, IO, datasources, workflow/artifact packages, or `tests.support`.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_contracts.py`; `tests/unit/rphys/ops/test_context.py`; `tests/unit/rphys/test_errors.py` if concrete errors are added
- Required assertions or deferral reason: valid and invalid construction for `OperationRole`, `OperationContract`, `OperationContext`, and `OperationResult`; normalization/immutability or shallow-copy behavior; mutation policy, side-effect labels, required context keys, and failure-mode labels; absence of deterministic/randomness, locator, identity, serialization, export, cache, datasource, workflow, and private-helper fields; concrete error inheritance/export only if exercised.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_contract.py`
- Required assertions or deferral reason: public operation declaration semantics are stable enough for downstream users; invalid declarations fail loudly; public records expose inspectable metadata/provenance without hidden globals; unsupported/deferred fields are absent; examples use synthetic stdlib values only.

### Integration Suite

- Status: deferred for Phase 1
- Expected paths: none in this phase
- Required assertions or deferral reason: runtime-container and lazy-field boundary coverage belongs to Phase 4 after operation execution and pipeline behavior exist. Phase 1 must not add integration tests that imply SampleOp/BatchOp locator permissions or runtime-container coupling.

### E2E Suite

- Status: deferred for Phase 1
- Expected paths: none in this phase
- Required assertions or deferral reason: no end-to-end operation workflow exists before wrapper execution and pipeline composition. Do not add e2e tests for schema-only behavior.

### Acceptance Suite

- Status: deferred for Phase 1
- Markers affected: none
- Required assertions or deferral reason: no real datasets, hardware, network, GPU, optional dependencies, or long-running checks are allowed or needed for public schema/import validation.

## Risks

- Public field names and exported symbols chosen in this phase may become hard to remove after Phase 2/3 build on them.
- Over-eager concrete errors could freeze an unsupported taxonomy; under-specified errors could weaken catchability for invalid public declarations.
- Private validators can accidentally become public contracts if docs/tests import them directly.
- Import-boundary regressions may hide in convenient reuse of existing data, IO, datasource, or test helper modules.
- A mutation policy representation that is too narrow may force Stage 7/8 refactoring; one that is too rich may pre-lock future locator/export policy.

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
make test-package
make test-unit
make test-contract
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: schema/context/kernel modules first, package exports/import tests second, construction validation tests third, exercised errors last.
- Tests to run with each slice: package tests after export/import edits; unit ops tests after schema/context edits; unit error tests after any `errors.py` change; contract tests after public semantics settle.
- Decisions the executor must not revisit: no public Protocol/base, no deterministic/randomness fields, no locator permissions, no identity/serialization fields, no raw-output API, no pipeline behavior, no placeholder names, no IO/datasource/heavy imports, and no private helper leakage.
- Conditions that require stopping for the manager: a required public field conflicts with locked deferrals; invalid schema behavior needs execution or pipeline semantics; concrete error names would be unexercised; lightweight import tests show forbidden modules load; implementation requires public helper APIs or direct private-helper tests.

## Refinement And Review Budget Status

- Phase execution plan refinement: pending / required
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed 2026-05-14 in the assigned worktree
- Final phase execution plan: pending required refinement pass
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending
- Pre-submit blocker gate: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known before required refinement
