# Phase Assignment: Stage 4 Phase 3 Lazy SampleField Runtime Compatibility

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-3-lazy-samplefield-runtime-compatibility`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `lazy-sample-field-runtime`
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Lazy `SampleField` Runtime Compatibility
- Branch: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 3: Lazy SampleField Runtime Compatibility`
- Workflow path: expanded path if runtime compatibility review finds accessor ambiguity; otherwise fast path
- Expanded-path trigger: loaded `Sample` contract regression, ambiguous payload-demanding accessor semantics, or need for a parallel `LazySample` container.
- Plan quality gate: passed in `docs/roadmap/stage-4/implementation-plan.md`; Phase 1 and Phase 2 dependencies merged and recorded.
- Phase isolation: dedicated branch and worktree required before any phase edit;
  one PR to `develop`; no local-only completion.
- Blockers: none known.

## Scope

- Goal: add lazy `SampleField` handles while preserving loaded `Sample` semantics and public `FieldContainer` behavior.
- In scope: `src/rphys/data/sample_fields.py`; additive runtime container compatibility updates in `src/rphys/data/containers.py`; conditional package exports/import-boundary coverage; unit/contract tests for state, load-on-payload, eager load, failed-state retention, no-load `field()` access, and loaded-sample compatibility.
- Out of scope: `SampleBuilder`, datasource scanning/provenance joining, retry/reset/cache policy, async behavior, device movement, operation pipelines, public loader handler interfaces, collation redesign, global registries, and replacement of loaded `FieldValue` behavior.
- Decisions already approved: DD-6, DD-7, DD-8, DD-10, DD-12, Phase 1 `FieldContainer` public iteration, and Phase 2 registry load result/error behavior.
- Future-phase exclusions: `SampleBuilder` and builder-side provenance are Phase 4; closeout examples/docs/final validation are Phase 5.

## Validation Obligations

- Package: run package import/export tests if `SampleField` is exported from `rphys.data`; otherwise prove canonical `rphys.data.sample_fields` import stays lightweight.
- Unit: run targeted `SampleField`, existing container, collation, and runtime-contract unit tests.
- Contract: run `make test-contract`, including existing runtime core contract and new lazy-field contract coverage.
- Integration: not required unless runtime/container behavior crosses into builder-style sample construction.
- E2E: not required.
- Acceptance: not required.
- Final local gate: `make validate-pr`, `make test-summary`, and PR-range `git diff --check origin/develop...HEAD` before PR submission unless unavailable with reason recorded.

## Phase Isolation Checks

- Control checkout status reviewed: clean `develop` at `7eb39f3 docs: record stage 4 phase 2 cleanup`.
- Dedicated phase branch created or verified: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p3-lazy-sample-field-runtime`.
- Branch base verified as current `develop`: yes, created from `origin/develop` after Phase 2 cleanup metadata.
- Earlier phase status verified as merged or blocked: Prep 1, Prep 2, Phase 1, and Phase 2 are merged and recorded.
- GitHub push and PR creation available: previously exercised in this workflow; verify again before PR.
- Stop if any check fails: stop before product code edits and return to manager if isolation, target branch, or PR infrastructure cannot be maintained.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: unused
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Loaded `Sample` contracts must be broken or existing loaded `FieldValue` behavior must be replaced.
- Lazy handles must be wrapped as `FieldValue.payload` instead of stored as field objects.
- Loading must replace the handle in the sample and erase retained diagnostics/provenance.
- Runtime behavior requires broad cache/retry/reset policy, async state, public loader handler interfaces, `SampleBuilder`, datasource-aware codec contexts, or collation redesign.
