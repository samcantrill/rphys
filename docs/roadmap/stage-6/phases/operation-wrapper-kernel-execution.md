# Phase 2 Execution Plan: Operation Wrapper And Kernel Execution

## Metadata

- Status: final phase execution plan; expanded-path refinement completed; ready for implementation
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
- Plan quality gate: Stage 6 implementation plan approved; expanded-path refinement was required and is now completed because Phase 2 locks public execution return semantics, wrapper API behavior, cause-preserving errors, and import-boundary guardrails.
- Draft pass: completed 2026-05-14
- Refine pass: completed 2026-05-14
- Setup limitations: no product code, tests, PR body, or PR opened during this planning/refinement pass; no broad checks run; no new worktree created
- Blockers: none known; implementation may proceed within this refined phase contract

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
- Import-boundary or dependency constraints: `rphys.ops.core` and any Phase 2 validators may use stdlib typing/dataclasses/collections utilities and existing `rphys.ops` records/errors only. They must not import `rphys.data`, `rphys.io`, `rphys.datasources`, codecs, optional numerical/video/deep-learning stacks, `tests.support`, workflow/artifact packages, runtime-container modules, or signature-introspection helpers that create alternate call conventions.

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
- Invoke the wrapped callable through the single refined call shape `function(input_value, context=context)`, using keyword-only context delivery without signature introspection, positional-context fallback, hidden globals, registries, implicit runtime containers, device movement, RNG, or schema conversion.
- Return `OperationResult` from both `.run()` and `__call__` with identical public semantics.
- Accept a callable-returned `OperationResult` when valid and compatible, or wrap a bare callable output into a new `OperationResult` when the callable returns a raw value.
- Validate accepted or wrapped results against operation name, role, declared output type, result metadata/provenance mapping shape, and side-effect evidence shape through public behavior.
- Preserve context metadata/provenance for bare-output wrapping and preserve callable-returned result metadata/provenance/side-effect evidence without hidden merging or durable serialization, identity, cache, export, or workflow semantics.
- Add exactly the exercised concrete execution errors `InvalidOperationInputError` and `OperationExecutionError`; reuse existing operation errors for constructor, context, and result validation as detailed below.
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
- The public constructor is fixed as `Operation(function: FunctionalKernel, *, name: str | None = None, contract: OperationContract | None = None)`. There are no constructor-level metadata, provenance, side-effect-evidence, registry, resolver, runtime-container, or parameter-injection fields.
- `contract=None` means `OperationContract()`. `name=None` means infer a non-empty name from `function.__name__` for functions or from the callable object's class name; unstable examples should pass `name=` explicitly.
- Context defaults to `OperationContext()` when omitted; required context keys are satisfied only by `OperationContext.metadata`, not provenance.
- Bare-output result wrapping uses the operation's own name and contract role, copies `context.metadata` into result metadata, copies `context.provenance` into result provenance, and uses empty `side_effect_evidence`.
- Callable-returned `OperationResult` must be validated and returned as-is when compatible. The wrapper must not merge context metadata/provenance into a returned result and must not synthesize side-effect evidence.
- `InvalidOperationResultError` is reused for incompatible returned results, output type mismatches, operation-name or role mismatches, and side-effect evidence that conflicts with the declared mutation policy or side-effect labels.
- Direct functional kernels remain ordinary Python callables and may be called outside `Operation`; Phase 2 tests should demonstrate this boundary with synthetic stdlib payloads only.

## Scope Contract

Phase 2 changes public behavior by adding `Operation` execution only. Public imports from `rphys.ops` should include the existing Phase 1 names plus `Operation`; no other new public operation-family or pipeline names should appear. `rphys.errors` may add only the exercised Phase 2 execution errors `InvalidOperationInputError` and `OperationExecutionError`.

`Operation.run(input_value, context=None)` and `Operation.__call__(input_value, context=None)` must both return `OperationResult`. They must not return bare callable outputs, and no `run_raw`, `call_raw`, `apply`, `execute_raw`, `raw`, `output`, or equivalent raw-output public API is allowed in this phase. Users access the underlying value through `result.output`.

Before invoking the callable, `Operation` must validate any declared `input_type` with normal runtime type semantics and must validate that all `contract.required_context` keys are present in `OperationContext.metadata`. Input mismatch uses `InvalidOperationInputError`; invalid context values or missing context metadata keys use `InvalidOperationContextError`. These failures must include structured context such as `operation_name`, `field`, `expected`, `actual`, `missing`, or `role`.

Callable invocation must use exactly `function(input_value, context=context)`. The implementation must not infer signatures, try alternate calling conventions, or inject `Sample`, `Batch`, device, RNG, schema, datasource, IO, or workflow state. Callable objects are supported because they are callable, not because they implement a public `OperationLike` interface.

After invocation, if the callable returns `OperationResult`, the wrapper validates it and returns it without merging context metadata or provenance. If the callable returns any other object, the wrapper creates an `OperationResult` around that object using the operation name, contract role, context metadata, context provenance, and empty side-effect evidence. In both cases, declared `output_type` must be checked against `result.output` when present, result `operation_name` must match the wrapper name, result `role` must match the contract role, and side-effect evidence must match the refined declaration rules. Result records must not become durable serialization contracts or identity/cache/export/workflow records.

Callable exceptions must be wrapped as `OperationExecutionError` under `RemotePhysOperationError` while preserving the original exception as `__cause__`. Error context must include the operation name and enough execution phase detail to diagnose invocation failure. Do not collapse original causes into strings only.

Mutation and side effects remain declared behavior only in Phase 2. `OperationMutationPolicy.MAY_MUTATE` can document that the callable may mutate its input, and `SIDE_EFFECTING` can document side-effect labels/evidence, but Phase 2 must not police field-level writes, locator permissions, export targets, or external side-effect completion. Any side-effect evidence returned or wrapped must stay generic and mapping-shaped.

## Expanded-Path Refinement Decisions

The public `Operation` API is intentionally small:

```python
Operation(
    function: FunctionalKernel,
    *,
    name: str | None = None,
    contract: OperationContract | None = None,
)
Operation.run(input_value: object, context: OperationContext | None = None) -> OperationResult
Operation.__call__(input_value: object, context: OperationContext | None = None) -> OperationResult
```

The wrapper may expose read-only public `name` and `contract` attributes. The wrapped callable should remain an implementation detail, for example `_function`, so Phase 2 does not freeze a callable-inspection API. Constructor validation uses `InvalidOperationContractError` for non-callable `function`, invalid or empty `name`, or non-`OperationContract` `contract` values after the `None` default is resolved.

Callable invocation has exactly one convention: `function(input_value, context=context)`. There is no one-argument fallback, positional-context fallback, signature introspection, `**context.metadata` expansion, parameter injection, `_target_` resolution, registry lookup, or runtime-container adaptation. Callable objects are supported because Python can call them with this same convention. Kernel examples should use a plain function or callable object that accepts `context` as a keyword and can also be invoked directly outside the wrapper with the same explicit argument.

Result handling has two paths. If the callable returns an `OperationResult`, validate it and return that same semantic result without merging context mappings into it. If the callable returns any other object, create `OperationResult(output, operation_name=name, role=contract.role, metadata=context.metadata, provenance=context.provenance, side_effect_evidence=None)`. The wrapper does not add constructor-level metadata/provenance because that would turn `Operation` into a durable identity or serialization record before Stage 7/8 pressure exists.

Side-effect evidence is validated only as a generic runtime mapping against declared operation behavior. For `OperationMutationPolicy.PURE` and `MAY_MUTATE`, any non-empty result `side_effect_evidence` is an `InvalidOperationResultError`. For `SIDE_EFFECTING`, evidence keys must be a subset of `contract.side_effects`; empty evidence is allowed because Phase 2 records declarations and evidence but does not prove external side-effect completion. No export target, file path, artifact, cache key, or workflow status is introduced.

Output type validation is `isinstance(result.output, contract.output_type)` when `output_type` is declared, using the concrete type or tuple of concrete types accepted by `OperationContract`. `output_type=None` disables output validation. The wrapper does not coerce outputs, inspect schemas, unpack containers, validate array shape, move devices, or materialize lazy fields. A bare `None` output is valid only when the declared output type allows it.

Phase 2 adds exactly two exercised concrete execution errors if implementation follows this plan:

- `InvalidOperationInputError`: raised before invocation when `contract.input_type` is declared and `input_value` does not satisfy it.
- `OperationExecutionError`: raised when the wrapped callable raises during the single invocation convention, with the original exception preserved as `__cause__`.

Existing errors are reused as follows: `InvalidOperationContractError` for wrapper declaration and constructor failures; `InvalidOperationContextError` for non-`OperationContext` context arguments or missing required metadata keys; `InvalidOperationResultError` for returned/wrapped result incompatibility, declared output type mismatch, operation-name mismatch, role mismatch, invalid result mapping shape, or side-effect evidence mismatch. Do not add `MissingOperationContextError`, `OperationOutputTypeError`, `OperationCallableError`, pipeline errors, or other placeholder execution names in Phase 2.

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

- Expected PR size and shape: small execution-focused PR adding one core wrapper module, exact `rphys.ops` export updates, `InvalidOperationInputError` and `OperationExecutionError`, and focused package/unit/contract tests.
- Files and areas to inspect: `src/rphys/ops/core.py`, `src/rphys/ops/__init__.py`, `src/rphys/ops/kernels.py` only if docs/example text changes, private `src/rphys/ops/_validation.py` only if execution validation reuses it, `src/rphys/errors.py`, `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`, `tests/unit/rphys/ops/test_core.py`, `tests/unit/rphys/ops/test_kernels.py`, `tests/unit/rphys/test_errors.py`, and `tests/contracts/test_operation_execution_contract.py`.
- Scope-control checks: `Operation` is the only new `rphys.ops` execution public name; no raw-output API; no pipeline names or behavior; no Protocol/base/registry; no SampleOp/BatchOp/runtime-container imports; no hidden RNG/device/schema conversion; no IO/datasource/heavy imports; no private helper docs/tests; no unexercised public errors.

## Implementation Steps

1. Add `src/rphys/ops/core.py` with the fixed `Operation(function, *, name=None, contract=None)` wrapper, public `name`/`contract` inspection, private callable storage, constructor validation, and imports limited to stdlib, Phase 1 operation records, and `rphys.errors`.
2. Implement `.run(input_value, context=None)` and `__call__(input_value, context=None)` parity with explicit `OperationContext()` defaulting, `InvalidOperationInputError` input-type validation, `InvalidOperationContextError` required-metadata validation, and the single callable invocation shape `function(input_value, context=context)`.
3. Implement result acceptance/wrapping and output/result validation: return compatible callable-produced `OperationResult` without context merging, wrap bare outputs with context metadata/provenance and empty side-effect evidence, validate declared output type, operation name, role, and side-effect evidence rules, and reuse `InvalidOperationResultError` for result incompatibility.
4. Add only the exercised concrete execution errors `InvalidOperationInputError` and `OperationExecutionError`, preserving original callable exceptions as `__cause__` and structured `RemotePhysError.context`; reuse existing contract/context/result errors for all other Phase 2 validation failures.
5. Update package exports/import-boundary tests for `Operation` and `rphys.ops.core`, add unit tests for wrapper execution and functional-kernel direct-call examples, and add contract tests for public execution semantics and guardrail absences.
6. Run focused Phase 2 validation and stop for manager review if implementation requires pipeline behavior, raw-output execution, public Protocol/base, registry lookup, runtime-container imports, hidden RNG/device/schema conversion, or unexercised public errors.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`; `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` includes `Operation` plus existing Phase 1 public names and no `OperationPipeline`, `SampleOp`, `BatchOp`, `Transform`, registry, raw-output helper, Protocol/base, or Stage 7/8 placeholder names; `rphys.ops.core.__all__` exposes exactly `["Operation"]`; root `rphys` still does not re-export operation names; `rphys.errors.__all__` adds exactly `InvalidOperationInputError` and `OperationExecutionError` for Phase 2; importing `rphys.ops.core` does not load heavy optional modules, `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules, `tests.support`, or workflow/artifact packages.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_core.py`; `tests/unit/rphys/ops/test_kernels.py`; `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: `Operation` wraps functions and callable objects through `function(input_value, context=context)` only; `.run()` and `__call__` return equivalent `OperationResult` shapes; omitted context becomes empty `OperationContext`; declared `input_type` is checked before invocation with `InvalidOperationInputError`; missing required context keys fail before invocation with `InvalidOperationContextError`; bare outputs are wrapped with context metadata/provenance and empty side-effect evidence; callable-returned `OperationResult` is accepted only when valid and compatible and is not context-merged; output type mismatches use `InvalidOperationResultError`; result metadata/provenance/side-effect evidence remain mapping-shaped and immutable through `OperationResult`; callable exceptions raise `OperationExecutionError` with `__cause__`; direct kernels remain callable without `Operation`; no raw-output method, registry, Protocol/base, SampleOp/BatchOp, runtime-container, RNG, device, or schema conversion behavior is present.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_execution_contract.py`
- Required assertions or deferral reason: public execution contract proves `Operation` is wrapper-first with the fixed constructor and call signatures, context is explicit, `required_context` keys come from `OperationContext.metadata`, successful calls always return `OperationResult`, users unwrap `.output`, bare-output and returned-result metadata/provenance behavior follows the refined rules, input/context/result/callable failures are typed and cause-preserving, and Stage 6 execution has no raw-output API, registry, public Protocol/base, pipeline behavior, or later-stage domain semantics.

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
- The fixed keyword-context convention may require small adapters around existing one-argument callables; adding an automatic fallback is a stop condition, not Phase 2 scope.

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
- Decisions the executor must not revisit: `Operation(function, *, name=None, contract=None)`; `.run(input_value, context=None)` and `__call__(input_value, context=None)` return `OperationResult`; callable invocation is only `function(input_value, context=context)`; bare-output wrapping copies context metadata/provenance and uses empty side-effect evidence; returned `OperationResult` is not context-merged; no raw-output API; wrapper-first concrete `Operation`; no public Protocol/base; no registry; no pipeline behavior; no SampleOp/BatchOp/runtime-container dependency; no hidden RNG/device/schema conversion; no durable identity/serialization/context fields; no unexercised public errors beyond `InvalidOperationInputError` and `OperationExecutionError`.
- Conditions that require stopping for the manager: implementation needs constructor-level metadata/provenance/side-effect fields; needs multiple callable signature conventions or signature introspection; callable-object support appears impossible without a public Protocol/base; preserving exception causes requires broad new error taxonomy; result metadata/provenance requires hidden merge policy beyond the refined rules; output validation requires coercion, schema inspection, device movement, or lazy-field materialization; execution needs runtime-container, IO, datasource, codec, workflow, RNG, device, or schema conversion imports; tests require pipeline semantics, direct private-helper imports, or a raw-output API.

## Refinement And Review Budget Status

- Phase execution plan refinement: completed 2026-05-14
- Phase implementation refinement: unused
- PR review: consumed by manager review 2026-05-14
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed 2026-05-14 in the assigned worktree
- Final phase execution plan: completed 2026-05-14 after expanded-path refinement
- Implementation summary:
  - Added concrete operation execution wrapper in `src/rphys/ops/core.py` with fixed `Operation(function, *, name=None, contract=None)` constructor, read-only `name`/`contract` accessors, exact `context` handling, keyword-only context-callable invocation, output/input/context/result validation, and cause-preserving execution errors.
  - Added `InvalidOperationInputError` and `OperationExecutionError` in `src/rphys/errors.py`, preserving existing concrete-error reuse and inheritance.
  - Extended `rphys.ops` exports to include `Operation`; added `rphys.ops.core.__all__` contract surface and updated package/import-boundary tests to import and guard lightweight `rphys.ops.core` loading.
  - Added unit coverage for wrapper execution and kernel boundaries (`tests/unit/rphys/ops/test_core.py`, `tests/unit/rphys/ops/test_kernels.py`), operation execution contracts (`tests/contracts/test_operation_execution_contract.py`), and updated error contract tests and imports for phase-2 errors.
  - Documented completion notes in this phase file with implemented behavior and validation status.
- Implementation validation: complete (`make test-package`, `make test-unit`, `make test-contract`, `git diff --check` passed)
- Refinement summary: completed; locked exact `Operation` constructor/run/call signatures, keyword-context callable invocation, result wrapping and no-merge rules, side-effect evidence validation, output type validation, `InvalidOperationInputError`/`OperationExecutionError`, package/import-boundary guardrails, raw-output API absence checks, and stop conditions
- Pre-submit blocker gate: cleared after `make validate-pr`, `uv lock --check`, `make test-summary`, `uv build`, and `git diff --check` passed.
- PR preparation: PR body draft complete in `docs/roadmap/stage-6/phases/operation-wrapper-kernel-execution-pr-body.md`; expanded-path metadata refinement completed after PR [#40](https://github.com/samcantrill/rphys/pull/40) opened against `develop`.
- Automated review: passed manager review 2026-05-14; diff matches Phase 2 scope, validation evidence is current for code/test changes, and the only post-validation changes are docs/PR metadata recorded with `git diff --check`.
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known before implementation
