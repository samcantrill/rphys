# Phase 5 Execution Plan: Descriptor-Only Derived Datasource Assembly And Final Synthetic Round Trip

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v8`
- Feature focus: derived datasource descriptors from export evidence
- Stage descriptor: Save/Export Ops And Derived DataSources
- Phase descriptor: Descriptor-Only Derived Datasource Assembly And Final Synthetic Round Trip
- PR title: `Stage 8 Save/Export Ops And Derived DataSources - Phase 5: Descriptor-Only Derived Datasource Assembly And Final Synthetic Round Trip`
- Branch: `agent/stage-8-p5-derived-datasource-roundtrip`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p5-derived-datasource-roundtrip`
- Phase execution plan path: `docs/roadmap/stage-8/phases/derived-datasource-roundtrip.md`
- Full plan: `docs/roadmap/stage-8/implementation-plan.md`
- Planning document: `docs/roadmap/stage-8/planning.md`
- Source phase: Phase 5
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: dedicated branch/worktree/PR to `develop`
- Plan quality gate: passed in implementation plan review
- Draft pass: manager-local fast path
- Refine pass: not needed unless targeted validation exposes a blocker
- Setup limitations: existing unrelated control-checkout `docs/roadmap.md` and `docs/roadmap/stage-9/` changes were not copied
- Blockers: none

## Objective

Add descriptor-only derived datasource assembly that converts successful
in-memory export results into ordinary `DataSourceRef` and ordered `RecordRef`
descriptors, then prove the synthetic export-to-derived-reload vertical slice
through existing index and lazy sample machinery.

## Full-Plan Context

Phases 1 through 4 are merged. Export specs, selection, save execution,
idempotency, and link/copy lineage are implemented under `rphys.ops.export`.
This phase owns only derived descriptor assembly under
`rphys.datasources.derived` and the final Stage 8 round-trip proof.

## Scope Contract

Derived assembly must not save/export fields, scan output directories, write or
define durable derived manifests, reuse `DataSourceIndexManifest` as a derived
manifest, mutate source descriptors, or introduce cache/materialization,
prediction/evaluation, metric, analysis, or training behavior.

## Implementation Steps

1. Add `DerivedDataSourceAssembly` and `DerivedDataSourceBuilder` under
   `rphys.datasources.derived`.
2. Assemble new derived `DataSourceRef` and ordered `RecordRef`s from
   successful `FieldExportResult` evidence, preserving source provenance and
   actual target resources.
3. Keep failed fields out of derived records and treat explicit skipped fields
   as usable existing-target evidence.
4. Add unit tests for no-rescan/no-manifest behavior, source descriptor
   immutability, target-resource lineage, failure handling, and scoped public
   imports.
5. Add the synthetic export-to-derived-datasource integration proof, including
   an ordinary prediction-like field exported and loaded as a normal field.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/datasources/test_derived.py tests/integration/test_stage8_export_derived_datasource_flow.py
uv run pytest tests/integration/test_stage5_synthetic_datasource_flow.py
make test-integration
make test-package
rg -n "SaveOp|CodecSelectionOp|to_dict|JSON|DataSourceIndexManifest|report file" docs src tests
make test
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local fast path.
- Final phase execution plan: scope-complete for Phase 5.
- Implementation summary: added descriptor-only derived datasource assembly and
  final synthetic export-to-derived-index-to-sample reload coverage.
- Implementation validation: targeted derived tests, Stage 5 baseline,
  `make test-integration`, `make test-package`, `make test`,
  `make validate-pr`, `make test-summary`, and `git diff --check` passed
  locally.
- Grep gate: findings are existing Stage 3/5 descriptor/index serialization,
  existing Stage 8 deferral text, and full public names containing roadmap
  shorthand substrings; no new derived manifest, report serialization, output
  rescan, or shorthand alias surface was added.
- Pre-submit blocker gate: passed; `rphys.datasources.derived` is
  descriptor-only and contains no save/export execution, durable derived
  manifest schema, `DataSourceIndexManifest` reuse, or output directory scan.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.
