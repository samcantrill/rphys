# Summary

Implemented Stage 13 Phase 3. Returned `Batch` fields can now be explicitly
uncollated into one `Sample` per item, and uncollated samples can be exported
and reloaded through the existing export/save and derived datasource contracts
with descriptor-backed field evidence.

# Links

- Roadmap stage: `docs/roadmap.md` Milestone 13
- Phase plan: `docs/roadmap/stage-13/phases/uncollation-sample-artifacts.md`
- Implementation plan: `docs/roadmap/stage-13/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-13/planning.md`

# Phase Isolation

- Branch: `agent/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
- Base branch: `develop`
- Head branch: `agent/stage-13-prediction-evaluation-analysis-reports-p3-uncollation-sample-artifacts`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: returned `Batch` values uncollate to one `Sample` per item
  through `UncollatePlan`.
- Units/shapes/dtypes: uncollation validates payload lengths and metadata
  alignment but does not infer tensor axes, sample rates, temporal stitching,
  masks, or physiological semantics.
- Provenance: export requests require a source `RecordRef`; derived fields such
  as predictions require explicit `FieldRef` descriptor evidence before saving.
- Durable handoff: persistence delegates to existing `RecordExportRequest`,
  codec-selection, save, `ExportResult`, and `DerivedDataSourceBuilder` behavior.
- Intentional exclusions: no prediction export/storage family, no batch-as-one
  durable record, no datasource scan, no new real codecs, and no report writers.

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
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_uncollation.py tests/unit/rphys/ops/test_export_sample_artifacts.py tests/contracts/test_stage13_sample_artifact_contract.py tests/integration/test_stage13_sample_artifact_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
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
targeted: passed (74 passed)
unit: passed (746 passed)
contract: passed (156 passed)
package: passed (68 passed)
integration: passed (25 passed)
e2e: not present
acceptance: not present
validate-pr: passed, including uv lock --check, uv build, and git diff --check
```

# Risks And Follow-Up

Phase 4 consumes these sample artifact and uncollation contracts for runtime
sample collection operations and metric adapters. This phase intentionally
leaves stitching, grouping, metric operation adapters, visualization, and report
records for later phases.
