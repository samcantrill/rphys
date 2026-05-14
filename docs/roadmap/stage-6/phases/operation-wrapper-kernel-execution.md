# Phase 2 Execution Plan: Operation Wrapper And Kernel Execution

## Metadata

- Status: draft phase execution plan; expanded-path refinement required before implementation
- Roadmap stage: `v6`
- Feature focus: Concrete operation wrapper execution and functional-kernel boundary
- Stage descriptor: Operation Foundations And Functional Kernels
- Phase descriptor: Operation Wrapper And Kernel Execution
- PR title: `Stage 6 Operation Foundations And Functional Kernels - Phase 2: Operation Wrapper And Kernel Execution`
- Branch: `agent/stage-6-p2-operation-wrapper-kernel-execution`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p2-operation-wrapper-kernel-execution`
- Phase execution plan path: `docs/roadmap/stage-6/phases/operation-wrapper-kernel-execution.md`
- Full plan: `docs/roadmap/stage-6/implementation-plan.md`
- Planning document: `docs/roadmap/stage-6/planning.md`
- Source phase: Phase 2, `operation-wrapper-kernel-execution`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; do not create a new worktree
- Plan quality gate: Stage 6 implementation plan approved; expanded-path refinement is required before implementation because Phase 2 locks public execution return semantics, wrapper API behavior, cause-preserving errors, and import-boundary guardrails.
- Draft pass: completed 2026-05-14
- Refine pass: pending/required
- Setup limitations: no product code, tests, PR body, or PR opened during this planning pass; no broad checks run; no new worktree created
- Blockers: none known for drafting; implementation must wait for the required refine pass

## Objective

Implement the concrete `Operation` wrapper that executes dependency-light callables under an `OperationContract`, validates input and required context before invocation, returns `OperationResult` from both `.run()` and `__call__`, accepts or wraps callable results without exposing a raw-output API, and preserves metadata, provenance, side-effect evidence, and original exception causes in exercised typed operation errors.

## Full-Plan Context

Phase 1 has merged the public schema/context/kernel vocabulary and the initial construction errors. Phase 2 is the first executable operation behavior over that surface: it adds the wrapper/core execution path and proves kernels remain directly callable without runtime containers or registries. Phase 3 owns ordered pipeline composition and `result.output` forwarding, Phase 4 owns runtime-container/lazy-field compatibility examples and public docs expansion, and Phase 5 owns final stage-wide validation. Phase 2 must not pull any of that future behavior forward.

## Source Phase Summary

- Goal: implement single-operation execution semantics over wrapped callables and prove the plain functional-kernel boundary.
- Required scope: `Operation` wrapper, callable and callable-object wrapping, input type and required-context validation before invocation, callable invocation, accepted or wrapped `OperationResult` handling, output/result validation, `.run()` and `__call__` parity, explicit `.output` access by callers, cause-preserving typed operation errors, and kernel examples/tests that remain stdlib and container-free.
- Required checkpoints: unit coverage for wrapper execution, kernel boundary, result validation, and operation errors; contract coverage for public execution semantics; package/import regression coverage for exports and lightweight imports; `git diff --check`.
- Acceptance criteria: `.run()` and `__call__` both return `OperationResult`; invalid inputs, missing context, invalid results, and callable exceptions fail loudly with typed errors and preserved causes; no pipeline behavior, raw-output API, public Protocol/base, registry, SampleOp/BatchOp dependency, runtime-container dependency, hidden RNG/device/schema conversion, or concrete rPPG kernels are introduced.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: Phase 1 added `src/rphys/ops/contracts.py`, `src/rphys/ops/context.py`, `src/rphys/ops/kernels.py`, and private `src/rphys/ops/_validation.py`; `src/rphys/ops/__init__.py` currently re-exports only `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, and `FunctionalKernel`.
- Existing files or modules that constrain this phase: `OperationContract` exposes `role`, `input_type`, `output_type`, `mutation_policy`, `side_effects`, `required_context`, and `failure_modes`; `OperationContext.required_context` is intentionally absent, and required keys are checked against `OperationContext.metadata`.
- Existing files or modules that constrain this phase: `OperationResult` exposes `output`, `operation_name`, `role`, `metadata`, `provenance`, and `side_effect_evidence`; all mapping fields are shallow-copied immutable mapping views with no durable serialization promise.
- Existing files or modules that constrain this phase: `src/rphys/errors.py` currently has broad `RemotePhysOperationError` and concrete `InvalidOperationContractError`, `InvalidOperationContextError`, and `InvalidOperationResultError`. Any new concrete execution error must be exercised by Phase 2 public behavior and remain under `RemotePhysOperationError`.
- Existing tests or harness behavior: `tests/package/test_import.py` asserts exact `rphys.ops.__all__`, submodule `__all__`, root non-reexports, and operation error exports; Phase 2 must update these only for implemented `Operation` and any exercised execution errors.
- Existing tests or harness behavior: `tests/package/test_import_boundaries.py` imports `rphys.ops`, `rphys.ops.contracts`, `rphys.ops.context`, and `rphys.ops.kernels` in a subprocess and forbids heavy optional modules, `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, and `tests.support`; Phase 2 must extend this to `rphys.ops.core`.
- Existing tests or harness behavior: unit ops tests currently cover schema/context/result construction only, and `tests/contracts/test_operation_contract.py` covers public declaration semantics. Phase 2 should add source-mirrored `tests/unit/rphys/ops/test_core.py`, likely extend `tests/unit/rphys/ops/test_kernels.py` or add it if needed, and add `tests/contracts/test_operation_execution_contract.py`.
- Import-boundary or dependency constraints: `rphys.ops.core` and any Phase 2 validators may use stdlib typing/dataclasses/collections/inspect utilities and existing `rphys.ops` records/errors only. They must not import `rphys.data`, `rphys.io`, `rphys.datasources`, codecs, optional numerical/video/deep-learning stacks, `tests.support`, workflow/artifact packages, or runtime-container modules.

## Phase Isolation State

- Control checkout dirty-state review: `git status --short --branch` showed a clean existing worktree on `agent/stage-6-p2-operation-wrapper-kernel-execution` before plan edits.
- Dedicated branch/worktree status: assigned branch and worktree verified at `/home/samcantrill/work/rphys-worktrees/stage-6-p2-operation-wrapper-kernel-execution`; no new worktree was created.
- Current `develop` base: local `HEAD`, local `develop`, and merge-base with `develop` all resolved to `64029451db2c76b1c55a70fa5d7cb6aac05e216a` during the draft pass.
- Earlier phase dependency status: Phase 1 is merged via PR #38 at `159734a0f4c79722afa14abb0484b76cff3ef4d3`, and its schema/context/kernel code is present in the current base.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before implementation if the worktree is not on the assigned branch, if unrelated dirty files appear in touched paths, if `develop` advances in a way that invalidates Phase 1 assumptions, or if implementation pressure requires a new worktree/branch.

## In-Scope Work

- Add `Operation` as the concrete wrapper-first public execution surface, likely in `src/rphys/ops/core.py`, and export it from `rphys.ops` only after it is implemented and tested.
- Support wrapping plain functions and callable objects through composition; no subclassing or public structural Protocol/base is required for user callables.
- Store an operation name, wrapped callable, and `OperationContract`; use the Phase 1 generic contract fields without adding deterministic/randomness, locator, identity, serialization, workflow, export, or cache fields.
- Validate the runtime input against `OperationContract.input_type` before callable invocation when a type expectation is declared.
- Validate `OperationContract.required_context` against explicit `OperationContext.metadata` before callable invocation, and create an empty `OperationContext` when callers omit context.
- Invoke the wrapped callable through one narrow, documented call shape chosen by implementation refinement, using explicit input and context behavior without hidden globals, registries, implicit runtime containers, device movement, RNG, or schema conversion.
- Return `OperationResult` from both `.run()` and `__call__` with identical public semantics.
- Accept a callable-returned `OperationResult` when valid and compatible, or wrap a bare callable output into a new `OperationResult` when the callable returns a raw value.
- Validate accepted or wrapped results against operation name, role, declared output type, result metadata/provenance mapping shape, and side-effect evidence shape through public behavior.
- Preserve caller and callable metadata/provenance in inspectable runtime records without making them durable serialization, identity, cache, export, or workflow schemas.
- Add only exercised concrete operation execution errors for invalid runtime input/context and callable execution failure if broad `RemotePhysOperationError` plus existing invalid result errors are not sufficiently precise for tested behavior.
- Add unit, contract, and package/import regression tests for wrapper execution, functional-kernel direct use, public return semantics, cause preservation, and guardrail absences.

## Out-of-Scope Work

- `OperationPipeline`, ordered sequence composition, adjacent compatibility validation, step-aware pipeline errors, `result.output` forwarding between steps, DAGs, routing, retries, resume, or workflow runtime behavior.
- A raw-output operation API, raw-output convenience method/property, alternate `__call__` return shape, or public API that hides `OperationResult.output` unwrapping.
- Public `OperationLike`, public Protocol/base class, subclass-required operation extension model, registries, symbolic lookup, plugin discovery, or `_target_` resolver behavior.
- SampleOp, BatchOp, Transform, augmentation/check classes, locator read/write/delete permissions, BatchOp equivalence, RNG replay, runtime-container field policy, or imports of `Sample`, `Batch`, `SampleField`, `IndexItem`, or builders.
- Export/save behavior, external file writes, datasource scans/indexes/manifests, cache/materialization keys, workflow/artifact state, training loaders, or downstream project orchestration.
- Hidden randomness, hidden device movement, implicit schema conversion, array/video/deep-learning dependencies, concrete CHROM/POS/rPPG kernels, real datasets, or test-only synthetic helper dependencies in core imports.
- New broad error taxonomy, placeholder public errors, pipeline errors, public helper APIs, private-helper tests/imports, root `rphys` exports, or placeholder Stage 7/8 subpackages.

## Assumptions

- `Operation` is a concrete lightweight wrapper around a callable plus `OperationContract`, not an abstract base, mixin, registry entry, or public Protocol.
- The default contract for an operation may be `OperationContract()` unless refinement identifies an existing Phase 1 validation reason to require an explicit contract; the resulting behavior must stay public and tested.
- The implementation may choose exact constructor keyword spelling during refinement only if the public wrapper semantics remain obvious, package-level exports stay exact, and no extra extension model is introduced.
- Context defaults to `OperationContext()` when omitted; required context keys are satisfied only by `OperationContext.metadata`, not provenance.
- Result wrapping uses the operation's own name and contract role. Bare outputs receive empty metadata/provenance/side-effect evidence unless implementation refinement records a narrow, explicit merge rule.
- Callable-returned `OperationResult` must be validated as a result object, not blindly trusted; invalid result construction/shape continues to use `InvalidOperationResultError` where that existing concrete error fits.
- Concrete execution error names may be selected during refinement/implementation only for failures exercised in Phase 2 tests; any unexercised public error name is out of scope.
- Direct functional kernels remain ordinary Python callables and may be called outside `Operation`; Phase 2 tests should demonstrate this boundary with synthetic stdlib payloads only.

## Scope Contract

Phase 2 changes public behavior by adding `Operation` execution only. Public imports from `rphys.ops` should include the existing Phase 1 names plus `Operation`; no other new public operation-family or pipeline names should appear unless the required refinement pass explicitly approves an exercised execution error export in `rphys.errors`.

`Operation.run(input, context=None)` and `Operation.__call__(input, context=None)` must both return `OperationResult`. They must not return bare callable outputs, and no `run_raw`, `apply`, `execute_raw`, or equivalent raw-output public API is allowed in this phase. Users access the underlying value through `result.output`.

Before invoking the callable, `Operation` must validate any declared `input_type` with normal runtime type semantics and must validate that all `contract.required_context` keys are present in `OperationContext.metadata`. These failures must be typed `RemotePhysOperationError` subclasses with structured context that includes useful fields such as `operation_name`, `field`, `expected`, `actual`, `missing`, or `role`.

Callable invocation must be explicit and narrow. Refinement must lock whether callables receive `(input)`, `(input, context)`, keyword context, or another small documented shape. The implementation must not infer or inject `Sample`, `Batch`, device, RNG, schema, datasource, IO, or workflow state. Callable objects are supported because they are callable, not because they implement a public `OperationLike` interface.

After invocation, if the callable returns `OperationResult`, the wrapper validates it and returns it when compatible. If the callable returns any other object, the wrapper creates an `OperationResult` around that object. In both cases, declared `output_type` must be checked against `result.output` when present, result `role` must remain compatible with the contract role, and metadata/provenance/side-effect evidence must remain inspectable runtime mappings. Result records must not become durable serialization contracts or identity/cache/export/workflow records.

Callable exceptions must be wrapped or re-raised as exercised operation execution errors under `RemotePhysOperationError` while preserving the original exception as `__cause__`. Error context must include the operation name and enough execution phase detail to diagnose whether validation, invocation, or result validation failed. Do not collapse original causes into strings only.

Mutation and side effects remain declared behavior only in Phase 2. `OperationMutationPolicy.MAY_MUTATE` can document that the callable may mutate its input, and `SIDE_EFFECTING` can document side-effect labels/evidence, but Phase 2 must not police field-level writes, locator permissions, export targets, or external side-effect completion. Any side-effect evidence returned or wrapped must stay generic and mapping-shaped.

## Scientific Contract Notes

- Sampling and temporal alignment: Phase 2 examples may use synthetic signal-like lists or tuples with explicit sampling-rate metadata, but no resampling, filtering, temporal alignment, windowing, or invalid-rate scientific algorithm behavior is introduced.
- Field roles, locators, schemas, and provenance: generic metadata/provenance are inspectable runtime mappings only; no field locator permissions, datasource identity, manifest fingerprints, cache keys, schema conversion, or runtime-container-specific provenance fields are added.
- Masking, filtering, normalization, and aggregation order: any kernel example must keep numerical behavior trivial and stdlib-only, and must not imply a CHROM/POS/rPPG preprocessing contract or a required processing order beyond explicit callable execution.
- Subject identity, splits, leakage, and grouping: no subject, split, leakage, group, or cross-record policy is introduced; any context keys used in tests are synthetic metadata keys and not durable identity fields.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: Phase 2 validates operation input type, required context, callable failure, and result/output compatibility. It does not add signal-quality validation, field-missing behavior, temporal slicing, or numerical edge-case policy unless a synthetic callable raises an ordinary cause that the wrapper preserves.

## Design Impact

- Maintainability: `Operation` belongs in a focused core module so execution behavior does not leak into schema/context/kernels modules or future pipeline code.
- Extensibility: wrapper-first composition leaves Stage 7 SampleOp/BatchOp and Stage 8 export operations free to wrap or specialize later without requiring inheritance in Stage 6.
- Lightweight import policy: `rphys.ops.core` must stay stdlib plus `rphys.errors` and Phase 1 `rphys.ops` modules; package/import tests must prove it does not load data, IO, datasource, codec, test-support, workflow/artifact, or heavy optional stacks.
- Source-tree boundaries: Phase 2 may touch `src/rphys/ops/core.py`, `src/rphys/ops/kernels.py` only for docs/examples if needed, private `src/rphys/ops` validators if needed, `src/rphys/ops/__init__.py`, `src/rphys/errors.py` only for exercised execution errors, package tests, unit ops/error tests, and operation execution contract tests.

## Future Compatibility

- Keep `OperationPipeline` absent so Phase 3 can define ordered sequence semantics without inheriting accidental single-operation shortcuts.
- Keep public Protocol/base and `OperationLike` absent until repeated custom operation-object needs appear in later stages.
- Keep raw-output convenience APIs absent so Stage 6 preserves uniform `OperationResult` return semantics and Phase 3 can forward `result.output` consistently.
- Keep context/result records generic and runtime-only so Stage 5/8/9 identity, serialization, cache/materialization, and export result adapters remain additive.
- Keep operation execution independent of `Sample`, `Batch`, `SampleField`, datasource indexes, codec IO, hidden RNG, hidden device movement, and schema conversion so Stage 7 specialized operation families can add those policies explicitly.
- Keep concrete errors minimal and exercised so later operation families can add catchable failures without carrying unused Phase 2 taxonomy.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Make `Operation.__call__` return the bare callable output | Maintainer approval locked `.run()` and `__call__` to return `OperationResult`, preserving provenance and explicit `.output` unwrapping. |
| Add a raw-output helper alongside result-return execution | Raw-output convenience is explicitly deferred; adding it now would split public execution semantics before downstream pressure exists. |
| Introduce public `OperationLike`/Protocol/base for callable objects | Wrapper-first composition is locked for Stage 6, and public structural extension is deferred until repeated custom-object needs appear. |
| Add a registry or symbolic kernel lookup | Stage 6 operations wrap explicit importable callables; registries would add global state and hidden resolution behavior. |
| Import runtime containers to make examples realistic | Phase 2 proves the plain kernel boundary; runtime-container-as-payload compatibility belongs to Phase 4. |
| Add broad execution and pipeline error taxonomy now | Repository policy requires only concrete public errors exercised by implemented behavior and tests. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| `Operation` callable signature adaptation is intentionally narrow | A narrow explicit call shape keeps execution inspectable and avoids a hidden dispatch framework. | Repeated real kernels need a second documented signature that cannot be expressed without awkward adapters. |
| Mutation and side-effect behavior remains declared rather than proven | Arbitrary Python callables cannot be inspected safely, and locator/export enforcement belongs to later stages. | Stage 7/8 needs field-level mutation, RNG replay, or export side-effect policy that cannot compose with generic declarations. |
| Direct callers must unwrap `OperationResult.output` | Uniform result-return execution preserves metadata/provenance and pipeline compatibility. | Downstream use repeatedly demonstrates excessive `.output` noise and a later accepted API adds a clearly named raw-output helper. |

## Reviewability

- Expected PR size and shape: small execution-focused PR adding one core wrapper module, exact `rphys.ops` export updates, minimal exercised errors if required, and focused package/unit/contract tests.
- Files and areas to inspect: `src/rphys/ops/core.py`, `src/rphys/ops/__init__.py`, `src/rphys/ops/kernels.py` only if docs/example text changes, private `src/rphys/ops/_validation.py` only if execution validation reuses it, `src/rphys/errors.py`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/unit/rphys/ops/test_core.py`, `tests/unit/rphys/ops/test_kernels.py`, `tests/unit/rphys/test_errors.py`, and `tests/contracts/test_operation_execution_contract.py`.
- Scope-control checks: `Operation` is the only new `rphys.ops` execution public name; no raw-output API; no pipeline names or behavior; no Protocol/base/registry; no SampleOp/BatchOp/runtime-container imports; no hidden RNG/device/schema conversion; no IO/datasource/heavy imports; no private helper docs/tests; no unexercised public errors.

## Implementation Steps

1. Add `src/rphys/ops/core.py` with a concrete `Operation` wrapper that stores a name, callable, and `OperationContract`, validates constructor inputs, and keeps imports limited to stdlib, Phase 1 operation records, and `rphys.errors`.
2. Implement `.run()` and `__call__` parity with explicit context defaulting, declared input-type validation, required context validation against `OperationContext.metadata`, narrow callable invocation, and `OperationResult` return in every successful path.
3. Implement result acceptance/wrapping and output/result validation: validate callable-returned `OperationResult`, wrap bare outputs with operation name/role and generic runtime mappings, check declared output type, preserve side-effect evidence, and keep metadata/provenance generic.
4. Add only exercised concrete execution errors if needed for invalid input/context or callable failure, preserving original callable exceptions as `__cause__` and structured `RemotePhysError.context`; otherwise reuse existing concrete result/context errors where semantically correct.
5. Update package exports/import-boundary tests for `Operation` and `rphys.ops.core`, add unit tests for wrapper execution and functional-kernel direct-call examples, and add contract tests for public execution semantics and guardrail absences.
6. Run focused Phase 2 validation and stop for manager review if implementation requires pipeline behavior, raw-output execution, public Protocol/base, registry lookup, runtime-container imports, hidden RNG/device/schema conversion, or unexercised public errors.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` includes `Operation` plus existing Phase 1 public names and no `OperationPipeline`, `SampleOp`, `BatchOp`, `Transform`, registry, raw-output helper, Protocol/base, or Stage 7/8 placeholder names; `rphys.ops.core.__all__` exposes exactly `["Operation"]`; root `rphys` still does not re-export operation names; any new exercised execution error appears in `rphys.errors.__all__` only if implemented and tested; importing `rphys.ops.core` does not load heavy optional modules, `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, `tests.support`, or workflow/artifact packages.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_core.py`; `tests/unit/rphys/ops/test_kernels.py`; `tests/unit/rphys/test_errors.py` if new execution errors are added
- Required assertions or deferral reason: `Operation` wraps functions and callable objects; `.run()` and `__call__` return equivalent `OperationResult` shapes; omitted context becomes empty `OperationContext`; declared `input_type` is checked before invocation; missing required context keys fail before invocation; bare outputs are wrapped; callable-returned `OperationResult` is accepted only when valid and compatible; output type mismatches fail loudly; result metadata/provenance/side-effect evidence remain mapping-shaped and immutable through `OperationResult`; callable exceptions preserve `__cause__`; direct kernels remain callable without `Operation`; no raw-output method, registry, Protocol/base, SampleOp/BatchOp, runtime-container, RNG, device, or schema conversion behavior is present.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_execution_contract.py`
- Required assertions or deferral reason: public execution contract proves `Operation` is wrapper-first, context is explicit, `required_context` keys come from `OperationContext.metadata`, successful calls always return `OperationResult`, users unwrap `.output`, input/context/result/callable failures are typed and cause-preserving, and Stage 6 execution has no raw-output API, registry, public Protocol/base, pipeline behavior, or later-stage domain semantics.

### Integration Suite

- Status: deferred for Phase 2
- Expected paths: none in this phase
- Required assertions or deferral reason: runtime-container and lazy-field boundary tests belong to Phase 4 after single-operation and pipeline behavior exist. Phase 2 must not import or depend on `Sample`, `Batch`, `SampleField`, datasource/index, or codec modules.

### E2E Suite

- Status: deferred for Phase 2
- Expected paths: none in this phase
- Required assertions or deferral reason: end-to-end operation workflows require pipeline/runtime-boundary behavior from later phases. Phase 2 validates only single-operation execution through package, unit, and contract suites.

### Acceptance Suite

- Status: deferred for Phase 2
- Markers affected: none
- Required assertions or deferral reason: no real datasets, hardware, GPU, network, optional dependency, or long-running acceptance behavior is involved in generic wrapper execution.

## Risks

- Public `Operation` constructor and call signature will be difficult to change after Phase 3 pipelines depend on it.
- Returning `OperationResult` from `__call__` may be ergonomically noisy, but it is a locked public semantics decision.
- Cause-preserving errors need enough specificity for diagnostics without adding placeholder taxonomy.
- Callable-result acceptance can blur responsibility between callable and wrapper metadata unless validation and merge rules stay narrow.
- Import-boundary regressions can slip in if execution helpers reuse runtime, IO, datasource, codec, or test helper modules.
- Signature adaptation can accidentally become a hidden dispatch framework if it supports too many callable shapes.

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

- Safe implementation slices: add `Operation` core wrapper and constructor validation first; add package export/import-boundary updates second; add run/call input/context validation third; add result acceptance/wrapping/output validation fourth; add exercised execution errors and cause preservation last.
- Tests to run with each slice: package tests after export/import-boundary edits; focused unit core tests after wrapper behavior; unit error tests after any `errors.py` change; contract tests after public execution semantics settle.
- Decisions the executor must not revisit: `.run()` and `__call__` return `OperationResult`; no raw-output API; wrapper-first concrete `Operation`; no public Protocol/base; no registry; no pipeline behavior; no SampleOp/BatchOp/runtime-container dependency; no hidden RNG/device/schema conversion; no durable identity/serialization/context fields; no unexercised public errors.
- Conditions that require stopping for the manager: implementation needs multiple callable signature conventions beyond the refined call shape; callable-object support appears impossible without a public Protocol/base; preserving exception causes requires broad new error taxonomy; execution needs runtime-container, IO, datasource, codec, workflow, RNG, device, or schema conversion imports; tests require pipeline semantics or a raw-output API.

## Refinement And Review Budget Status

- Phase execution plan refinement: pending/required
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed 2026-05-14 in the assigned worktree
- Final phase execution plan: pending required expanded-path refinement
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending; must focus on public execution return semantics, exact wrapper API/callable invocation shape, cause-preserving errors, result merge/validation rules, and import-boundary risk before implementation
- Pre-submit blocker gate: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: required refinement pass before implementation
