# Phase Assignment: Stage 4 Phase 2 Explicit Registry And Synthetic Codec Operations

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-2-explicit-registry-and-synthetic-codec-operations`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `codec-registry-synthetic-ops`
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Explicit Registry And Synthetic Codec Operations
- Branch: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 2: Explicit Registry And Synthetic Codec Operations`
- Workflow path: fast path
- Expanded-path trigger: none currently; expand only if registry matching requires unapproved symbolic names, hidden discovery, or public fake-codec support.
- Plan quality gate: passed in `docs/roadmap/stage-4/implementation-plan.md`; Phase 1 dependency merged and recorded.
- Phase isolation: dedicated branch and worktree required before any phase edit;
  one PR to `develop`; no local-only completion.
- Blockers: none known.

## Scope

- Goal: prove deterministic codec resolution and dependency-light probe/load/save behavior through explicit registry instances.
- In scope: `CodecRegistry` behavior in `src/rphys/io/codecs.py`; typed registry/operation diagnostics under existing error bases; private tests/support synthetic codec behavior; unit/contract coverage for probe without load, load, save, metadata policies, unsupported operation/index, dependency-unavailable, no match, ambiguity, and deterministic ordering.
- Out of scope: global discovery, process-global mutable registries, symbolic codec keys, real codecs or optional dependency stacks, public fake codec exports, hidden full-resource fallback, metadata manifest writes, metadata handler interfaces, export orchestration, runtime `SampleField`, and `SampleBuilder`.
- Decisions already approved: DD-1, DD-2, DD-3, DD-4, DD-5, DD-8, DD-10, DD-11, plus Phase 1 canonical `rphys.io.codecs` import boundary.
- Future-phase exclusions: lazy field state/loading is Phase 3; builder-side datasource provenance and lazy sample construction are Phase 4; closeout docs/examples/final validation are Phase 5.

## Validation Obligations

- Package: run `make test-package` if public exports or import boundaries change; otherwise run focused package import tests to prove no export drift.
- Unit: run targeted unit tests for `CodecRegistry`, operation wrappers, typed failures, and private synthetic codec behavior.
- Contract: run `make test-contract` with executable codec probe/load/save coverage.
- Integration: not required unless implementation crosses datasource/runtime boundaries, which should trigger a scope review.
- E2E: not required.
- Acceptance: not required.
- Final local gate: `make validate-pr`, `make test-summary`, and `git diff --check` before PR submission unless unavailable with reason recorded.

## Phase Isolation Checks

- Control checkout status reviewed: clean `develop` at `bf93003 docs: record stage 4 phase 1 cleanup`.
- Dedicated phase branch created or verified: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p2-codec-registry-synthetic-ops`.
- Branch base verified as current `develop`: yes, created from `origin/develop` after Phase 1 cleanup metadata.
- Earlier phase status verified as merged or blocked: Prep 1, Prep 2, and Phase 1 are merged and recorded.
- GitHub push and PR creation available: previously exercised in this workflow; verify again before PR.
- Stop if any check fails: stop before product code edits and return to manager if isolation, target branch, or PR infrastructure cannot be maintained.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: unused
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Registry matching requires global mutable registry state, hidden plugin discovery, symbolic codec names, or unapproved priority heuristics.
- Synthetic codec behavior must become public API or importable from the package surface.
- Probe/load/save behavior requires real optional dependencies, datasource-aware codec contexts, export layout policy, metadata handler interfaces, or manifest writes.
- Unsupported field indexes require hidden full-resource fallback instead of a typed unsupported failure.
- Runtime `SampleField` or `SampleBuilder` behavior is needed to complete this phase.
