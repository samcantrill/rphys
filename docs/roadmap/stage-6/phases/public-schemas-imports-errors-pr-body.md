# Summary

Implements Stage 6 Phase 1 by establishing the first code-backed provisional
`rphys.ops` public surface for operation declarations, runtime context/result
records, broad functional-kernel typing, and typed construction failures.

The phase adds dependency-light operation schema modules under `src/rphys/ops`,
exports only the implemented Phase 1 names from `rphys.ops`, and adds exact
package, unit, and contract coverage for schema construction, normalization,
immutability, import boundaries, and deferred-field absence.

# Links

- Roadmap stage: `docs/roadmap/stage-6/planning.md`
- Phase plan: `docs/roadmap/stage-6/phases/public-schemas-imports-errors.md`
- Implementation plan: `docs/roadmap/stage-6/implementation-plan.md`
- Scientific review: Covered by phase-plan scientific contract notes and public contract tests for schema-only operation declarations.

# Phase Isolation

- Branch: `agent/stage-6-p1-public-schemas-imports-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p1-public-schemas-imports-errors`
- Base branch: `develop`
- Head branch: `agent/stage-6-p1-public-schemas-imports-errors`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `OperationContract` now records optional `input_type` and `output_type` expectations as `None`, a `type`, or a tuple of types. No operation execution, runtime value validation, or pipeline forwarding behavior is implemented in this phase.
- Units/shapes/dtypes: no units, signal shapes, dtypes, devices, sampling rates, or numerical kernel assumptions are introduced. Type expectations remain generic Python runtime declarations only.
- Sampling/alignment/provenance: no sampling, temporal alignment, resampling, filtering, interpolation, or temporal slicing behavior is added. `OperationContext` and `OperationResult` expose shallow-copied immutable `metadata` and `provenance` mappings for runtime inspection only.
- Pipeline-order implications: no `Operation`, `OperationPipeline`, step ordering, context propagation, or result forwarding behavior is implemented. Later phases own execution and composition.
- Leakage or subject/split implications: no subject identity, split policy, grouping, dataset identity, cache key, workflow ID, or artifact identity field is added. Generic metadata can carry caller-provided labels, but this phase defines no leakage policy.
- Legacy parity or intentional behavior changes: `rphys.ops` intentionally changes from an empty deferred package to a narrow implemented provisional public surface: `OperationRole`, `OperationMutationPolicy`, `OperationContract`, `OperationContext`, `OperationResult`, and `FunctionalKernel`. Root `rphys` re-exports and placeholder future operation names remain absent.

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
make test-package
make test-unit
make test-contract
make test-summary
make validate-pr
uv lock --check
uv build
git diff --check
```

Final pre-submit gate evidence:

```text
make validate-pr: passed
uv lock --check: passed
make test-summary: passed
uv build: passed
git diff --check: passed
```

Latest recorded `build/test-summary.md` evidence:

```text
Overall Status: passed
package: 29 passed
unit: 388 passed
contract: 56 passed
integration: 3 passed
e2e: not present
acceptance: not present
Overall: 476 passed
```

# Risks And Follow-Up

The public names and field spellings introduced here are provisional but
code-backed, so later phases should treat removals or semantic changes as API
changes. `OperationMutationPolicy` is intentionally minimal and may need
additive refinement once SampleOp/BatchOp, export behavior, or RNG replay are
implemented.

Follow-up remains with later Stage 6 phases: operation wrapper execution,
ordered pipeline composition, runtime-boundary documentation, and final
validation readiness. Stage 7/8/9 concepts such as locators, export/cache
identity, durable serialization, workflow IDs, and concrete rPPG kernels remain
explicitly out of scope.
