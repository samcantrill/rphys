# Summary

Implements Stage 14 Phase 4 by completing the synthetic scan-to-report smoke
tail through real Stage 13 public APIs: Batch-returning learner output,
explicit uncollation, sample artifact export/reload, metric fields,
visualization/report records, and grouped/stitched collection outputs.

# Links

- Roadmap stage: `docs/roadmap/stage-14/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-14/phases/stage13-scan-to-report-tail.md`
- Implementation plan: `docs/roadmap/stage-14/implementation-plan.md`
- Scientific review: Stage 14 design review in `docs/roadmap/stage-14/implementation-plan.md`

# Phase Isolation

- Branch: `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
- Base branch: `develop`
- Head branch: `agent/stage-14-synthetic-smoke-hardening-p4-stage13-scan-to-report-tail`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: generated synthetic datasource descriptors, scan validation
  reports, datasource index manifests, lazy samples, LIST-collated batches,
  returned prediction batches, uncollated samples, exported/reloaded sample
  artifacts, metric fields, visualization descriptors, report rows, and
  stitched record-level output fields.
- Units/shapes/dtypes: the smoke uses a deterministic two-sample BVP/timestamp
  window and preserves `signal.bvp.v1` schemas through prediction, export, and
  reload.
- Sampling/alignment/provenance: subject, split, record, manifest, uncollation,
  export target, derived datasource, metric, visualization, and report
  provenance remain inspectable.
- Pipeline-order implications: scan, validation, grouping, splitting, indexing,
  sample building, sample operation preparation, collation, learner prediction,
  uncollation, sample artifact export/reload, metric, visualization, report,
  group/view/concat operations are exercised in order.
- Leakage or subject/split implications: subject-level split metadata is
  preserved into report rows and collection grouping; no global statistics,
  real data, external network, GPU, or heavy optional dependency is introduced.
- Legacy parity or intentional behavior changes: this is test/documentation
  coverage only; no public `rphys` API changes.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests
- [x] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
uv run pytest tests/integration/test_stage14_scan_to_report_tail.py
uv run pytest tests/package/test_import.py -k stage_13
make test-package
make test-contract
make test-integration
make test-e2e
make test-summary
make validate-pr
uv lock --check
git diff --check
```

`make test-e2e` reported no e2e files are present. The clean summary reported
package 72 passed, unit 752 passed, contract 174 passed, integration 30
passed, e2e not present, and acceptance not present.

# Risks And Follow-Up

This completes the Stage 14 planned phase scope. Future work should keep public
helper extraction, real datasource smoke, acceptance datasets, Stage 15
profiling/data-path optimization, and broader golden snapshots behind separate
roadmap decisions.
