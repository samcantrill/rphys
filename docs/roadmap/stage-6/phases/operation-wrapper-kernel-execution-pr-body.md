# Summary

Implements Stage 6 Phase 2 by adding the concrete `Operation` wrapper for
single-callable execution over the Phase 1 operation contracts, context, result,
and functional-kernel vocabulary.

The wrapper keeps Stage 6 execution explicit and dependency-light: callables are
invoked as `function(input_value, context=context)`, `.run()` and `__call__`
always return `OperationResult`, and callers unwrap user payloads through
`result.output`. Bare callable outputs are wrapped with the operation name,
contract role, context metadata, context provenance, and empty side-effect
evidence. Callable-returned `OperationResult` values are validated and returned
without hidden context merging.

# Links

- Roadmap stage: `docs/roadmap/stage-6/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-6/phases/operation-wrapper-kernel-execution.md`
- Implementation plan: `docs/roadmap/stage-6/implementation-plan.md`
- Scientific review: covered by the Stage 6 planning and phase execution-plan
  scientific contract notes

# Phase Isolation

- Branch: `agent/stage-6-p2-operation-wrapper-kernel-execution`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p2-operation-wrapper-kernel-execution`
- Base branch: `develop`
- Head branch: `agent/stage-6-p2-operation-wrapper-kernel-execution`
- Scope statement: this PR contains one roadmap implementation phase only.

# PR Submission Metadata

- Title: `Stage 6 Operation Foundations And Functional Kernels - Phase 2: Operation Wrapper And Kernel Execution`
- Base: `develop`
- Head: `agent/stage-6-p2-operation-wrapper-kernel-execution`
- Status: opened as [#40](https://github.com/samcantrill/rphys/pull/40)

# Scientific Contract

- Inputs/outputs: `OperationContract.input_type` is checked before callable
  invocation when declared; `OperationContract.output_type` is checked against
  `OperationResult.output` after invocation or wrapping. No output coercion,
  schema inspection, device movement, or lazy-field materialization is added.
- Units/shapes/dtypes: this phase does not introduce physiological units, array
  shape contracts, dtype policy, filtering, normalization, or concrete rPPG
  kernels. Tests use synthetic stdlib payloads to prove execution semantics.
- Sampling/alignment/provenance: no sampling-rate validation, temporal
  alignment, resampling, windowing, masking, or subject/split policy is added.
  Runtime metadata and provenance remain generic inspectable mappings copied
  from explicit `OperationContext` only for bare-output wrapping.
- Pipeline-order implications: no `OperationPipeline` or ordered composition is
  introduced. The uniform `OperationResult` return shape prepares Phase 3 to
  forward `result.output` explicitly between steps.
- Leakage or subject/split implications: no dataset split, subject identity, or
  leakage policy is changed. Required context keys are satisfied only by
  `OperationContext.metadata`, not by provenance or hidden global state.
- Legacy parity or intentional behavior changes: Stage 6 intentionally adds a
  new wrapper-first generic operation surface, not parity with prior project
  structures. Callable objects are supported by composition; no public
  operation protocol, registry, raw-output API, SampleOp/BatchOp dependency, or
  runtime-container dependency is introduced.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
make validate-pr
uv lock --check
make test-summary
uv build
git diff --check
```

Final validation evidence:

```text
make validate-pr passed
uv lock --check passed
test-summary passed with 500 total tests
uv build passed
git diff --check passed
```

# Risks And Follow-Up

- Phase 3 owns ordered pipeline composition, adjacent compatibility validation,
  and explicit `result.output` forwarding.
- Phase 4 owns runtime-container and lazy-field compatibility examples plus
  public documentation expansion.
- Mutation and side-effect behavior remains declared and mapping-validated; this
  phase does not prove field-level writes, export completion, filesystem
  effects, cache keys, or workflow artifacts.
- The callable invocation convention is deliberately narrow. Existing
  one-argument callables need small adapters that accept the explicit
  keyword-only `context` argument.
