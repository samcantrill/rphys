# Summary

Implements Stage 7 Phase 2 sample operation public foundations.

This PR adds the first code-backed `SampleOperation` surface over existing
`Sample` containers, parsed `FieldLocator` declarations, and Stage 6
`OperationStep` execution. It introduces immutable, inspectable sample-specific
records for field permissions, sample operation contracts, execution context,
and replay evidence while preserving the generic `OperationResult` envelope and
generic pipeline compatibility.

This phase intentionally stops at the public foundation. It does not implement
sample transforms, checks, augmentations, mutation snapshot enforcement,
specialized sample pipelines, batch APIs, export/cache/loader behavior,
trainer/workflow policy, root `rphys` exports, shorthand aliases, registries, or
heavy optional imports.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-7/phases/sample-foundations.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/planning.md`

# Phase Isolation

- Branch: `agent/stage-7-p2-sample-foundations`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p2-sample-foundations`
- Base branch: `develop`
- Head branch: `agent/stage-7-p2-sample-foundations`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleOperation` accepts `Sample` input and returns a Stage 6
  `OperationResult` whose output is a `Sample`. Bare `Sample` callable returns
  are normalized into `OperationResult`; explicit `OperationResult` returns are
  validated.
- Units/shapes/dtypes: this phase does not inspect numerical payload units,
  shapes, dtypes, devices, masks, rates, or temporal slices. Field declarations
  remain locator addresses over existing sample fields.
- Sampling/alignment/provenance: execution context and replay records carry
  dependency-light provenance seed material such as run seed, epoch, worker id,
  item id, sample id, operation index, operation name, view name, and optional
  caller-provided RNG stream. They are runtime evidence, not durable export,
  cache, loader, or manifest schemas.
- Pipeline-order implications: `SampleOperation` satisfies `OperationStep` and
  composes in the generic `OperationPipeline` without changing generic pipeline
  mapping/raw-callable rejection or adding specialized sample pipeline behavior.
- Leakage or subject/split implications: caller metadata/provenance can carry
  subject, split, or grouping identifiers, but this phase does not compute,
  enforce, or validate split policy.
- Legacy parity or intentional behavior changes: Stage 6 operation result,
  context, compatibility, and typed failure behavior are preserved. The new
  sample-specific contract is separate from the adapted generic
  `OperationContract`, which remains `input_type=Sample`, `output_type=Sample`,
  and `OperationRole.GENERIC`.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests (suite not present)
- [x] Acceptance or opt-in checks, if applicable (suite not present)
- [x] Scientific/workflow contract review completed

Commands run:

```text
uv run pytest tests/unit/rphys/ops/test_sample.py
uv run pytest tests/package/test_import_boundaries.py -k ops_sample
make test-unit
make test-contract
make test-package
git diff --check
make validate-pr
```

`make validate-pr` passed, including `uv lock --check`, `make test-summary`,
package/unit/contract/integration summaries, sdist/wheel build, and
`git diff --check`.

Test summary from `build/test-summary.md`:

| Suite | Status | Passed | Failed | Errors | Skipped | Deselected | Total | Duration | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| package | passed | 31 | 0 | 0 | 0 | 0 | 31 | 1.52s | 40% |
| unit | passed | 442 | 0 | 0 | 0 | 0 | 442 | 2.19s | 93% |
| contract | passed | 78 | 0 | 0 | 0 | 0 | 78 | 1.28s | 82% |
| integration | passed | 3 | 0 | 0 | 0 | 0 | 3 | 1.14s | 62% |
| e2e | not present | 0 | 0 | 0 | 0 | 0 | 0 | 0.00s | N/A |
| acceptance | not present | 0 | 0 | 0 | 0 | 0 | 0 | 0.00s | N/A |
| Overall | passed | 554 | 0 | 0 | 0 | 0 | 554 | 6.12s | - |

# Risks And Follow-Up

- Write, delete, and dynamic-write declarations are inspectable public contract
  data in this phase, but enforcement is intentionally deferred to Phase 3.
- Replay records and context fields are runtime evidence only; durable
  serialization, export/cache identity, and loader integration remain later
  roadmap work.
- Required-read preflight validates field presence without materializing lazy
  payloads; payload schema, numerical validity, masks, sampling rates, and
  operation-specific physiological checks remain future transform/check
  responsibilities.
