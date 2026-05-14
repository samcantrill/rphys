# Summary

Implements Stage 6 Phase 3 ordered pipeline composition for generic operations.

This PR adds `OperationPipeline` as a narrow sequence-only wrapper over concrete
`Operation` instances. Pipelines store an immutable `operations` tuple, validate
adjacent declared `output_type`/`input_type` compatibility, propagate one
`OperationContext` object unchanged through all steps, forward each
`OperationResult.output` to the next step, and return the final
`OperationResult`.

It also adds the two exercised concrete pipeline errors:
`InvalidOperationPipelineError` for construction/static compatibility failures
and `OperationPipelineExecutionError` for runtime pipeline failures with
step-aware context and preserved causes.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-6/phases/ordered-pipeline-composition.md`
- Implementation plan: `docs/roadmap/stage-6/implementation-plan.md`
- Scientific review: encoded in the phase plan and automated phase review

# Phase Isolation

- Branch: `agent/stage-6-p3-ordered-pipeline-composition`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p3-ordered-pipeline-composition`
- Base branch: `develop`
- Head branch: `agent/stage-6-p3-ordered-pipeline-composition`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: generic Python payloads only; pipeline steps receive the prior
  step's `OperationResult.output`.
- Units/shapes/dtypes: no numerical units, shapes, dtypes, sampling rates, or
  device policy are introduced.
- Sampling/alignment/provenance: pipeline order is explicit sequence order;
  no sampling, alignment, provenance aggregation, cache identity, or durable
  workflow trace is introduced.
- Pipeline-order implications: operations run in stored order, static
  compatibility requires every declared upstream output type to be accepted by
  the downstream input declaration, and runtime mismatches fail through
  step-aware pipeline execution errors.
- Leakage or subject/split implications: none; no dataset, subject, split, or
  grouping policy is touched.
- Legacy parity or intentional behavior changes: `rphys.ops` now exposes
  `OperationPipeline`; ordered mappings, named entries, DAG/routing, retries,
  resume, workflow state, raw-output APIs, `SampleOp`, `BatchOp`, and export
  pipelines remain out of scope and absent.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present
- [x] Acceptance or opt-in checks not present
- [x] Scientific/workflow contract review completed

Commands run:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/ops/test_pipelines.py tests/contracts/test_operation_pipeline_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
make validate-pr
make test-package
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/ops/test_pipelines.py tests/contracts/test_operation_pipeline_contract.py tests/unit/rphys/test_errors.py
git diff --check develop...HEAD
```

Latest `make validate-pr` evidence:

```text
package: passed (29 passed)
unit: passed (416 passed)
contract: passed (70 passed)
integration: passed (3 passed)
e2e: not present
acceptance: not present
uv lock --check: passed
uv build: passed
git diff --check: passed
```

# Risks And Follow-Up

Sequence-only construction intentionally leaves step naming and ordered mapping
support for later phases if Stage 7 pressure proves the semantics. Phase 4 owns
runtime-container-as-payload examples and public docs expansion. No blocking
issues were found in automated phase review.
