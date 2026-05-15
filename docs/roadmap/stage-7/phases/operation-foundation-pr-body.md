# Summary

Stage 7 Phase 1 refactors the shared operation foundation around a public
`OperationStep` execution interface so generic pipelines and later specialized
sample/batch operation families can compose step objects without depending on
concrete `Operation` instances.

This PR preserves Stage 6 operation semantics except for the approved broader
generic pipeline input type: ordered `OperationPipeline` entries may now be
`OperationStep` objects. `Operation` remains the ordinary callable-first wrapper
path, direct `OperationStep` implementation is the advanced adapter path, and
generic pipelines still reject raw callables, mappings, tuple named entries,
text inputs, arbitrary non-step objects, and empty sequences.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-7/phases/operation-foundation.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/planning.md`

# Phase Isolation

- Branch: `agent/stage-7-p1-operation-foundation`
- Worktree:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p1-operation-foundation`
- Base branch: `develop`
- Head branch: `agent/stage-7-p1-operation-foundation`
- Scope statement: this PR contains one roadmap implementation phase only.

Future-phase exclusions are preserved: this PR does not add sample/batch
operation contracts, locator permissions, mutation enforcement, augmentations,
specialized mapping pipelines, export/cache identities, loader/trainer policy,
workflow runtime behavior, registries, graph/DAG execution, retry/resume
behavior, root `rphys` exports, or heavy optional imports.

# Scientific Contract

- Inputs/outputs: generic operation inputs and outputs remain ordinary Python
  payloads. `OperationStep.run(input_value, context=None)` must return the
  existing `OperationResult` record, and `OperationPipeline` continues to
  forward each step's `OperationResult.output`.
- Units/shapes/dtypes: no units, shapes, dtypes, devices, sampling rates, or
  temporal semantics are introduced or interpreted by this foundation phase.
- Sampling/alignment/provenance: sampling, alignment, masks, subject identity,
  splits, field locators, and lazy materialization remain untouched. Runtime
  metadata/provenance remain the existing `OperationContext` and
  `OperationResult` mappings.
- Pipeline-order implications: generic pipeline order remains the explicit
  caller-provided sequence. Adjacent compatibility checks continue to use each
  step's `OperationContract`.
- Leakage or subject/split implications: no split, grouping, subject identity,
  route, loader, or retry policy is added.
- Legacy parity or intentional behavior changes: Stage 6 behavior is preserved
  except that generic `OperationPipeline` accepts ordered `OperationStep`
  entries in addition to concrete `Operation` instances. Raw callable,
  mapping, named tuple-entry, text, invalid context, compatibility, and step
  failure diagnostics remain typed and inspectable.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present for this phase
- [x] Acceptance or opt-in checks not present for this phase
- [x] Scientific/workflow contract review completed

Commands run:

```text
make test-unit
make test-contract
make test-package
git diff --check
make validate-pr
```

Final PR-prep gate:

```text
make validate-pr
```

`make validate-pr` passed. It ran `uv lock --check`, generated
`build/test-summary.md`, ran package/unit/contract/integration summaries with
529 total tests passing, built the source distribution and wheel, and ran
`git diff --check`.

Suite summary from `build/test-summary.md`:

| Suite | Status | Passed | Failed | Errors | Skipped | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| package | passed | 29 | 0 | 0 | 0 | 29 |
| unit | passed | 423 | 0 | 0 | 0 | 423 |
| contract | passed | 74 | 0 | 0 | 0 | 74 |
| integration | passed | 3 | 0 | 0 | 0 | 3 |
| e2e | not present | 0 | 0 | 0 | 0 | 0 |
| acceptance | not present | 0 | 0 | 0 | 0 | 0 |
| Overall | passed | 529 | 0 | 0 | 0 | 529 |

# Risks And Follow-Up

- Later phases must keep `OperationStep` as an execution interface, not a
  registry, workflow abstraction, export/cache identity, loader policy, or
  trainer policy.
- Sample operation contracts, field-permission enforcement, stochastic
  augmentation replay, specialized mapping pipelines, and provisional batch
  operation surfaces remain deferred to later Stage 7 phases.
- No blockers are known for this phase.
