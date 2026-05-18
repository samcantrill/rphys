# Summary

Implemented Stage 13 Phase 4. Runtime sample streams can now group into
`SampleCollection` snapshots, collection operations can sort/project/filter and
stitch fields into revised samples, and metrics bind directly to declared
`metrics/*` fields through sample and collection operation adapters.

# Links

- Roadmap stage: `docs/roadmap.md` Milestone 13
- Phase plan: `docs/roadmap/stage-13/phases/sample-collection-metric-ops.md`
- Implementation plan: `docs/roadmap/stage-13/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-13/planning.md`

# Phase Isolation

- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
- Base branch: `develop`
- Head branch: `agent/stage-13-prediction-evaluation-analysis-reports-p4-sample-collection-metric-ops`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Grouping: `SampleCollectionGroupPlan` groups by explicit item metadata and
  optional sample field payload keys. Missing group keys fail unless the plan
  explicitly allows them.
- Sorting/projection/filtering: collection operations preserve item metadata
  and provenance, fail loudly for invalid selectors or sort keys, and return
  explicit skip diagnostics when configured.
- Stitching/concatenation: `SampleCollectionConcatPlan` maps source fields to
  output fields and uses an injected joiner or tuple joiner. It does not infer
  sampling rates, axes, masks, temporal alignment, or physiological
  reconstruction semantics.
- Metrics: metric callables must produce every declared write and may not emit
  undeclared fields. Public metrics expose `MetricValue` and ordinary
  `metrics/*` fields, not observation/result rows.
- Intentional exclusions: no public evaluator/runner/protocol/result, no
  inference engine, no public generic job API, no registry, no prediction
  storage, no `BatchCollection`/`BatchCollector`, and no `rphys.ops.collections`.

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
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_collections.py tests/unit/rphys/metrics/test_metric_contracts.py tests/unit/rphys/metrics/test_metric_observation_views.py tests/contracts/test_metric_contract.py tests/contracts/test_metric_observation_view_contract.py tests/contracts/test_stage13_sample_collection_ops_contract.py tests/contracts/test_stage13_metric_operation_contract.py tests/package/test_import.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/learning/test_supervised.py tests/integration/test_stage11_synthetic_contract_flow.py tests/integration/test_stage12_synthetic_training_flow.py tests/integration/test_stage13_synthetic_sample_collection_pipeline.py tests/unit/rphys/training/test_backend.py
env UV_CACHE_DIR=/tmp/uv-cache make test-unit
env UV_CACHE_DIR=/tmp/uv-cache make test-contract
env UV_CACHE_DIR=/tmp/uv-cache make test-integration
env UV_CACHE_DIR=/tmp/uv-cache make test-package
env UV_CACHE_DIR=/tmp/uv-cache make test-summary
env UV_CACHE_DIR=/tmp/uv-cache make validate-pr
git diff --check
```

Suite summary:

```text
targeted collection/metric/package: passed (71 passed)
targeted learner/training/integration: passed (15 passed)
unit: passed (744 passed)
contract: passed (158 passed)
integration: passed (26 passed)
package: passed (68 passed)
e2e: not present
acceptance: not present
validate-pr: passed, including uv lock --check, uv build, and git diff --check
```

# Risks And Follow-Up

Phase 5 consumes metric-field-bearing samples, `SampleCollection` values, and
operation metadata for dependency-light visualization/report builders and recipe
examples. This phase intentionally leaves report records, visualization records,
and analysis recipes for Phase 5.
