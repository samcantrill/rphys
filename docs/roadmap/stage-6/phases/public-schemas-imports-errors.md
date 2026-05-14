# Phase 1 Execution Plan: Public Schemas, Imports, And Errors

## Metadata

- Status: refined phase execution plan; ready for implementation
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
- Merge eligibility: eligible after implementation review, focused local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; do not create a new worktree
- Plan quality gate: Stage 6 implementation plan approved; expanded-path refinement completed for public API schema, mutation, error, import-boundary, and stop-condition decisions
- Draft pass: completed 2026-05-14
- Refine pass: completed 2026-05-14
- Setup limitations: no product code, tests, PR body, or PR opened during this planning pass; no network refresh performed
- Blockers: none known after refinement

## Objective

Establish the smallest code-backed provisional `rphys.ops` schema and kernel vocabulary needed by later Stage 6 execution phases while keeping public imports exact, lightweight, and free of deferred Stage 7/8/9 concepts.

## Full-Plan Context

Phase 1 creates the schema/context/kernel declarations that Phase 2 will use for the concrete `Operation` wrapper and Phase 3 will use for ordered pipeline composition. It must leave execution, pipeline, runtime-container examples, docs expansion, and final validation to later phases. The public names and fields chosen here are hard to remove, so the phase must prefer a narrow implemented surface over placeholder exports.

## Source Phase Summary

- Goal: establish the code-backed provisional `rphys.ops` public surface and minimal declaration records before execution behavior depends on them.
- Required scope: `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, broad `FunctionalKernel` vocabulary, immutable or shallow-immutable normalization, exact package exports, private validators only if useful, and exactly three exercised concrete operation errors for invalid contract/context/result construction.
- Required checkpoints: package/export checks, import-boundary checks, unit tests for contract/context/result construction, contract tests for public schema semantics and deferred-field absence, and `git diff --check`.
- Acceptance criteria: no deferred fields, no root re-exports, no placeholder future names, no heavy/data/IO/datasource/codec imports, no public Protocol/base, no private helper leakage, and no operation or pipeline execution behavior.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/ops/__init__.py` currently has a docstring and empty `__all__`; `src/rphys/errors.py` already exposes broad `RemotePhysOperationError` and `RemotePhysPipelineError` bases plus exercised earlier-stage concrete errors.
- Existing tests or harness behavior: `tests/package/test_import.py` treats `rphys.ops` as a deferred package with empty public surface today; `tests/package/test_import_boundaries.py` verifies lightweight imports and forbidden workflow/artifact packages; unit tests mirror `src/rphys` under `tests/unit/rphys`; contract tests live under `tests/contracts`.
- Import-boundary or dependency constraints: importing `rphys.ops` and any new `rphys.ops` implementation modules must not load optional heavy stacks (`av`, `cv2`, `matplotlib`, `numpy`, `pandas`, `scipy`, `torch`), `rphys.data`, `rphys.io`, `rphys.datasources`, codec modules, `tests.support`, or workflow/artifact packages.

## Phase Isolation State

- Control checkout dirty-state review: `git status --short --branch` showed a clean worktree on `agent/stage-6-p1-public-schemas-imports-errors` before plan edits.
- Dedicated branch/worktree status: existing branch and worktree verified at `/home/samcantrill/work/rphys-worktrees/stage-6-p1-public-schemas-imports-errors`.
- Current `develop` base: local `HEAD`, `origin/develop`, and `develop` all resolved to `525c1fa` during this draft pass.
- Earlier phase dependency status: none; this is Phase 1.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before implementation if the worktree is not on the assigned branch, if unrelated dirty files appear in touched paths, or if the branch is no longer based on the intended `develop` revision.

## In-Scope Work

- Add focused `rphys.ops` implementation-home modules for schema/context/kernel vocabulary: `contracts.py`, `context.py`, `kernels.py`, and optional private `_validation.py`.
- Update `src/rphys/ops/__init__.py` to re-export only implemented Phase 1 provisional names: `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, and `FunctionalKernel`.
- Implement `OperationContract` with exactly these public fields: `role`, `input_type`, `output_type`, `mutation_policy`, `side_effects`, `required_context`, and `failure_modes`.
- Implement runtime-only `OperationContext` with exactly `metadata` and `provenance` mappings, and `OperationResult` with exactly `output`, `operation_name`, `role`, `metadata`, `provenance`, and `side_effect_evidence`.
- Add broad `FunctionalKernel` callable vocabulary without a registry, fixed scientific signature, hidden context requirement, public Protocol/base, or container dependency.
- Add only the Phase 1 concrete operation errors `InvalidOperationContractError`, `InvalidOperationContextError`, and `InvalidOperationResultError`, each subclassing `RemotePhysOperationError`; add no pipeline errors.
- Add package, unit, and contract tests that prove exact exports, lightweight imports, schema/context/result validation, deferred-field absence, and any exercised concrete error inheritance.

## Out-of-Scope Work

- `Operation` wrapper execution, `.run()`, `__call__`, callable invocation, output validation after execution, and raw-output API decisions.
- `OperationPipeline`, adjacent compatibility validation, step-aware pipeline errors, context propagation through steps, DAGs, routing, retries, or resume behavior.
- SampleOp, BatchOp, transforms, augmentations, checks, locator read/write/delete permissions, BatchOp equivalence, RNG replay, and ordered mapping/named-entry pipeline construction.
- Export/save operations, datasource scans, indexes, manifests, cache/materialization keys, workflow/artifact runtimes, trainer/data-loader behavior, and durable serialization.
- Concrete rPPG kernels, CHROM/POS/model preprocessing, optional array/video/deep-learning dependencies, real datasets, and acceptance-suite fixtures.
- Root `rphys` re-exports, placeholder Stage 7/8 packages or names, public registries, public helper modules, and tests or docs importing private helpers directly.

## Assumptions

- Public Phase 1 schema field spelling is fixed by this plan; implementation may choose constructor defaults and validation factoring only where observable fields and semantics remain unchanged.
- `OperationRole` starts with the single generic value `GENERIC = "generic"`; broader role taxonomy is deferred until a later implemented behavior needs it.
- `OperationMutationPolicy` is the public mutation representation. Its required values are `PURE = "pure"`, `MAY_MUTATE = "may_mutate"`, and `SIDE_EFFECTING = "side_effecting"`.
- `FunctionalKernel` can be a broad typing/documentation alias or similarly lightweight vocabulary, but it must not become a registry, mandatory inheritance surface, fixed-signature Protocol, or container-aware Protocol.
- Phase 1 invalid contract/context/result construction is public failure behavior and must use the three concrete errors named in this plan; broad `RemotePhysOperationError` remains the base catch-all.

## Scope Contract

Phase 1 changes public behavior only by making implemented Phase 1 `rphys.ops` names importable from the package and by defining their construction/validation contracts. The exact package-level public surface for this phase is `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, and `FunctionalKernel`. `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, `Transform`, export/save names, registries, public helper APIs, and public Protocol/base classes remain absent.

`OperationContract` must be a small frozen/slotted inspectable declaration record with exactly these public fields:

- `role`: an `OperationRole` value. Phase 1 exposes only `OperationRole.GENERIC = "generic"` and must not add transform/check/export/analysis role values.
- `input_type`: `None`, a `type`, or a `tuple[type, ...]` describing optional runtime input expectations.
- `output_type`: `None`, a `type`, or a `tuple[type, ...]` describing optional runtime output expectations.
- `mutation_policy`: an `OperationMutationPolicy` value. `PURE` means the operation declares no input mutation or external side effect and requires empty `side_effects`; `MAY_MUTATE` means it may mutate the input object, Stage 6 does not inspect field-level writes, and `side_effects` stays empty; `SIDE_EFFECTING` means it may perform externally visible side effects described by a non-empty `side_effects` tuple.
- `side_effects`: an ordered tuple of non-empty string labels. It is declaration metadata only, not export/save policy.
- `required_context`: an ordered tuple of non-empty string keys expected to be present in `OperationContext.metadata`.
- `failure_modes`: an ordered tuple of non-empty string labels documenting public failure categories.

`OperationContract` must reject invalid role, type expectation, mutation policy, label, duplicate label, or mapping/sequence shapes loudly through `InvalidOperationContractError`. It must not include deterministic/randomness fields, field locators, export targets, cache keys, datasource identity, workflow IDs, run IDs, tags, durable serialization controls, algorithm-specific schemas, or Stage 7/8 context fields.

`OperationContext` and `OperationResult` must be runtime-inspectable records, not durable artifact schemas. `OperationContext` exposes only `metadata` and `provenance`; `required_context` keys are checked against `OperationContext.metadata` in later execution phases, not against provenance. `OperationResult` exposes only `output`, `operation_name`, `role`, `metadata`, `provenance`, and `side_effect_evidence`; `operation_name` is a non-empty operation label, not a run ID, cache key, workflow ID, or artifact identity. Mapping fields must be shallow-copied from caller mappings and exposed through an immutable mapping view so later caller mutation cannot change the record and record-level assignment fails. Nested values are not deep-copied and no primitive-only serialization promise is made. Sequence fields on `OperationContract` must normalize to tuples and detach from caller-owned lists. Public tests should assert observable construction, normalization, shallow immutability/copy behavior, and absence of deferred fields through public APIs only.

Concrete errors are public API. Phase 1 must add exactly `InvalidOperationContractError`, `InvalidOperationContextError`, and `InvalidOperationResultError` for construction/validation failures it exercises. Each must subclass `RemotePhysOperationError`, preserve `RemotePhysError.context`, and use structured context fields such as `field`, `expected`, `actual`, `operation_name`, and `role` where useful. Do not add pipeline errors in this phase; if pipeline failure behavior appears necessary, stop for review instead of expanding scope.

## Scientific Contract Notes

- Sampling and temporal alignment: no signal sampling, alignment, resampling, filtering, or temporal-slice behavior is implemented in this phase; examples must stay synthetic and stdlib-only.
- Field roles, locators, schemas, and provenance: operation records may carry generic metadata/provenance mappings, but must not introduce field-locator permissions, schema conversion, datasource identity, manifest semantics, cache keys, or required primitive provenance fields.
- Masking, filtering, normalization, and aggregation order: no numerical processing order is implemented; `FunctionalKernel` only documents the plain-callable boundary that later kernels must respect.
- Subject identity, splits, leakage, and grouping: no subject, split, grouping, or leakage policy is introduced; do not add identity-like context/result fields.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: no signal validation is introduced; Phase 1 failure behavior is limited to invalid declarations and invalid context/result construction. Unsupported deferred fields should remain absent from constructors/attributes and be covered by absence tests, not custom Stage 7/8 validators.

## Design Impact

- Maintainability: focused implementation-home modules keep schema/context/kernel concerns separated before execution and pipeline behavior land.
- Extensibility: a narrow schema leaves additive room for Stage 7 SampleOp/BatchOp locator permissions, Stage 8 export result adapters, and Stage 9 cache/materialization identity.
- Lightweight import policy: `rphys.ops`, `rphys.ops.contracts`, `rphys.ops.context`, and `rphys.ops.kernels` must depend only on stdlib typing/dataclasses/enums/collections-style modules and `rphys.errors`; importing data, IO, datasource, codec, test-support, workflow/artifact, or heavy optional stacks is a blocker.
- Source-tree boundaries: Stage 6 Phase 1 may touch `src/rphys/ops`, `src/rphys/errors.py`, package tests, unit ops/error tests, and operation contract tests only.

## Future Compatibility

- Keep `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, export/save operation names, and specialized context/result names absent until their phases implement them.
- Keep public Protocol/base-class and `OperationLike` surfaces deferred until repeated custom-operation-object needs are proven.
- Keep deterministic/randomness declarations deferred until Stage 7/8 operation families require RNG replay or stochastic provenance.
- Keep runtime-only metadata/provenance mappings and `side_effect_evidence` from becoming cache keys, manifests, export summaries, datasource identities, or workflow IDs.
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
| `OperationMutationPolicy` starts with only three generic values | This keeps mutation visible without field-locator, export, or RNG policy. | Stage 7/8 needs additional mutation/export/RNG declarations that cannot be added without changing the generic contract semantics. |
| Kernel purity cannot be proven statically by a broad callable vocabulary | A broad callable boundary preserves scientific reuse and avoids false rigidity; import-boundary tests and docs carry the guardrail. | A later concrete kernel family needs a narrower verified protocol or repeated misuse appears in examples/tests. |

## Reviewability

- Expected PR size and shape: small public API/schema PR with new `src/rphys/ops` schema modules, exact package exports, exactly three concrete operation errors, and package/unit/contract tests.
- Files and areas to inspect: `src/rphys/ops/__init__.py`, `src/rphys/ops/contracts.py`, `src/rphys/ops/context.py`, `src/rphys/ops/kernels.py`, optional `src/rphys/ops/_validation.py`, `src/rphys/errors.py`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/unit/rphys/ops/test_contracts.py`, `tests/unit/rphys/ops/test_context.py`, `tests/unit/rphys/test_errors.py`, and `tests/contracts/test_operation_contract.py`.
- Scope-control checks: exact `__all__`, no root re-exports, no private helper imports in tests/docs, no deferred fields, no execution/pipeline behavior, no IO/datasource/codec/heavy imports, no unexercised public errors, and no public names beyond this phase's list.

## Implementation Steps

1. Define `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, `FunctionalKernel`, and any private validators in focused `rphys.ops` modules without importing data, IO, datasource, codec, or heavy optional packages.
2. Re-export only those six Phase 1 names from `rphys.ops.__init__` and update package tests to assert exact public names, exact submodule `__all__` values, no root re-exports, and absence of placeholder future names.
3. Implement declaration/context/result validation and normalization through public constructors, including tuple normalization, shallow copied immutable mapping views, and `OperationMutationPolicy` semantics exactly as recorded above.
4. Add `InvalidOperationContractError`, `InvalidOperationContextError`, and `InvalidOperationResultError` under `RemotePhysOperationError`, with package/unit coverage for export order, inheritance, message/context behavior, and no pipeline error additions.
5. Add unit and contract coverage for valid/invalid schema construction, mutation/side-effect declarations, required context keys, result metadata/provenance/side-effect evidence, deferred-field absence, and private-helper non-leakage through public behavior.
6. Run the focused Phase 1 validation commands and stop for review if any required behavior needs execution, pipeline, identity, deterministic/randomness, locator, serialization, broad role taxonomy, or private-helper public exposure.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact `rphys.ops.__all__` equals `["OperationRole", "OperationMutationPolicy", "OperationContract", "OperationContext", "OperationResult", "FunctionalKernel"]`; `rphys.ops.contracts.__all__` equals `["OperationRole", "OperationMutationPolicy", "OperationContract"]`; `rphys.ops.context.__all__` equals `["OperationContext", "OperationResult"]`; `rphys.ops.kernels.__all__` equals `["FunctionalKernel"]`; no root `rphys` re-exports; no placeholder `Operation`, `OperationPipeline`, `SampleOp`, `BatchOp`, `Transform`, export/save, Stage 7/8, registry, public helper, or Protocol/base names; `rphys.errors.__all__` inserts `["InvalidOperationContractError", "InvalidOperationContextError", "InvalidOperationResultError"]` after the existing concrete stage-error groups and before broad error bases; `rphys.ops` and implemented submodules do not load heavy optional modules, `rphys.data`, `rphys.io`, `rphys.datasources`, codec modules, workflow/artifact packages, or `tests.support`.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_contracts.py`; `tests/unit/rphys/ops/test_context.py`; `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: valid and invalid construction for `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, and `OperationResult`; exact `OperationRole` and `OperationMutationPolicy` values; exact `OperationContract` field list; rejection of invalid type expectations, mutation values, blank/duplicate labels, non-string context/failure labels, inconsistent mutation/side-effect declarations, and invalid mapping inputs; tuple normalization and shallow copied immutable mapping behavior; result `operation_name`, `role`, metadata, provenance, and `side_effect_evidence`; absence of deterministic/randomness, locator, identity, serialization, export, cache, datasource, workflow, and private-helper fields; concrete error inheritance/export for all three Phase 1 operation errors.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_contract.py`
- Required assertions or deferral reason: public operation declaration semantics are stable enough for downstream users; invalid declarations fail loudly with Phase 1 operation errors; public records expose inspectable metadata/provenance/side-effect evidence without hidden globals; shallow immutability/copying is observable; unsupported/deferred fields are absent; examples use synthetic stdlib values only.

### Integration Suite

- Status: deferred for Phase 1
- Expected paths: none in this phase
- Required assertions or deferral reason: runtime-container and lazy-field boundary coverage belongs to Phase 4 after operation execution and pipeline behavior exist. Phase 1 must not add integration tests that imply SampleOp/BatchOp locator permissions, runtime-container coupling, operation execution, or pipeline behavior.

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
- `OperationMutationPolicy` may still be too narrow or too broad once Stage 7/8 add field locators, export behavior, or RNG replay.
- Three concrete Phase 1 errors improve catchability but become public API; any additional error name would be unsupported scope creep.
- Private validators can accidentally become public contracts if docs/tests import them directly.
- Import-boundary regressions may hide in convenient reuse of existing data, IO, datasource, or test helper modules.

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

- Safe implementation slices: schema/context/kernel modules first, package exports/import tests second, construction validation tests third, exact Phase 1 errors last.
- Tests to run with each slice: package tests after export/import edits; unit ops tests after schema/context edits; unit error tests after any `errors.py` change; contract tests after public semantics settle.
- Decisions the executor must not revisit: exact Phase 1 public names and field spelling, exact `OperationMutationPolicy` values, no public Protocol/base, no deterministic/randomness fields, no locator permissions, no identity/serialization fields, no raw-output API, no pipeline behavior, no placeholder names, no IO/datasource/codec/heavy imports, and no private helper leakage.
- Conditions that require stopping for the manager: a required public field conflicts with locked deferrals; schema/context/result behavior needs execution or pipeline semantics; additional or different concrete error names appear necessary; lightweight import tests show forbidden modules load; implementation requires public helper APIs, direct private-helper tests, broad role taxonomy, or Stage 7/8/9 fields.

## Refinement And Review Budget Status

- Phase execution plan refinement: completed 2026-05-14
- Phase implementation refinement: completed 2026-05-14 for pre-submit blocker hardening
- PR review: unused
- Blocker resolution: 1/3 used

## Completion Notes

- Draft plan: completed 2026-05-14 in the assigned worktree
- Final phase execution plan: completed 2026-05-14 after expanded-path refinement
- Implementation summary:
  - Added new dependency-light `rphys.ops` public schemas in `src/rphys/ops/contracts.py`, `src/rphys/ops/context.py`, and `src/rphys/ops/kernels.py` with exact public names.
  - Added private validation helpers in `src/rphys/ops/_validation.py` and exact error types in `src/rphys/errors.py`.
  - Added focused package/import-boundary tests and unit + contract coverage for contract/context/result normalization, validation, and deferred-field absence.
- Implementation validation: complete (`make test-package`, `make test-unit`, `make test-contract`, `git diff --check` executed by phase executor)
- Refinement summary: locked public schema field spelling/semantics, `OperationMutationPolicy`, shallow immutability/copying expectations, Phase 1 concrete errors, package/import-boundary obligations, and stop conditions without changing phase scope
- Implementation refinement pass: completed 2026-05-14; updated stale `src/rphys/ops` Stage 1 docstrings to Stage 6 language, replaced identity-like `run_id` provenance examples in `tests/unit/rphys/ops/test_context.py`, and aligned the contracts unit test path to `tests/unit/rphys/ops/test_contracts.py` with an ops test namespace marker to avoid duplicate basename collection conflicts, without changing behavior or adding public API.
- PR body refinement: completed 2026-05-14 for expanded-path final gate evidence; PR not opened.
- Pre-submit blocker gate: cleared after `make validate-pr`, `uv lock --check`, `make test-summary`, `uv build`, and `git diff --check` passed.
- PR preparation: PR body draft complete 2026-05-14 at `docs/roadmap/stage-6/phases/public-schemas-imports-errors-pr-body.md`; expanded-path PR body refine complete; PR not opened.
- Automated review: not run in this PR-body/evidence-only refinement pass
- Merge result: pending
- Cleanup: in-progress
- Remaining blockers: none known after refinement
