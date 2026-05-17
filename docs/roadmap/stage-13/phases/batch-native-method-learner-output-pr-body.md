# Summary

Implemented Stage 13 Phase 2. Methods and learners now return ordinary
`Batch` values; generic returned-batch output validation lives in `rphys.data`;
and native training consumes objective/loss/metric/diagnostic fields declared by
`TrainingOutputSpec` on `TrainingPlan`.

# Links

- Roadmap stage: `docs/roadmap.md` Milestone 13
- Phase plan: `docs/roadmap/stage-13/phases/batch-native-method-learner-output.md`
- Implementation plan: `docs/roadmap/stage-13/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-13/planning.md`

# Phase Isolation

- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
- Base branch: `develop`
- Head branch: `agent/stage-13-prediction-evaluation-analysis-reports-p2-batch-native-method-learner-output`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `Method.predict` and `Learner.step` return `Batch`; output
  meaning is carried by field locators, roles, schemas, metadata, and
  provenance.
- Units/shapes/dtypes: returned-batch specs validate declared schemas and
  payload types but do not infer sampling, alignment, masks, or physiological
  semantics.
- Leakage implications: `project_batch_fields` excludes target roles by
  default, and method input specs reject target/prediction/output/score roles.
- Training implications: native training validates the returned learner batch
  through `TrainingOutputSpec` before backward, optimizer/scheduler steps, and
  summary recording; train mode requires a declared backwardable objective field.
- Intentional behavior changes: public `MethodOutput`, `MethodOutputSpec`,
  `MethodOutputAdapter`, `apply_method_output`, `StepOutput`, and
  `StepPrediction` names are removed.

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
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/unit/rphys/data/test_batch_output.py tests/unit/rphys/learning/test_supervised.py tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_plan.py
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-integration
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
git diff --check
```

Suite summary:

```text
targeted: passed (68 passed)
package: passed (68 passed)
unit: passed (738 passed)
contract: passed (153 passed)
integration: passed (24 passed)
e2e: not present
acceptance: not present
validate-pr: passed, including uv lock --check, uv build, and git diff --check
```

# Risks And Follow-Up

This phase intentionally does not implement uncollation or durable artifact
export/reload. Phase 3 consumes the returned `Batch` prediction fields and adds
explicit sample-granular uncollation/export behavior over existing export/save
and datasource contracts.
