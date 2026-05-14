# Phase Assignment: Stage 4 Phase 4 SampleBuilder Bridge And Provenance Contracts

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-4-samplebuilder-bridge-and-provenance-contracts`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `sample-builder-provenance`
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: `SampleBuilder` Bridge And Provenance Contracts
- Branch: `agent/codecs-lazy-samples-p4-sample-builder-provenance`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p4-sample-builder-provenance`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 4: SampleBuilder Bridge And Provenance Contracts`
- Workflow path: expanded path
- Expanded-path trigger: main bridge behavior phase; use extra review if provenance or accessor semantics become ambiguous.
- Plan quality gate: passed in `docs/roadmap/stage-4/implementation-plan.md`; Phase 1 through Phase 3 dependencies merged and recorded.
- Phase isolation: dedicated branch and worktree required before any phase edit;
  one PR to `develop`; no local-only completion.
- Blockers: none known.

## Scope

- Goal: build lazy `Sample`s from one `IndexItem` with all/subset/one/probe/eager paths while keeping codec contexts datasource-neutral and provenance inspectable.
- In scope: `src/rphys/data/sample_builders.py`; optional package/import-boundary coverage; unit/contract tests for all/subset/one, missing-request prevalidation, probe without load, eager load through `SampleField`, ordered resources, provenance retention, and descriptor/index-item non-mutation.
- Out of scope: datasource scans, bulk index manifests, split/view construction, item IDs/fingerprints, member/alignment semantics, datasource-aware codec contexts, model formatting, caching, device movement, export operations, and save orchestration.
- Decisions already approved: DD-3, DD-4, DD-6, DD-7, DD-8, DD-9, DD-10, DD-12, plus private synthetic codec support from DD-11 for validation only.
- Future-phase exclusions: final docs/examples/validation closeout is Phase 5.

## Validation Obligations

- Package: run import/export tests if builder public surface or import boundaries change; otherwise prove canonical `rphys.data.sample_builders` import stays lightweight.
- Unit: run targeted `SampleBuilder` tests and relevant lazy field/codec tests.
- Contract: run `make test-contract` with lazy sample construction/provenance coverage.
- Integration: optional only if a vertical slice is adopted because unit/contract coverage is too fragmented.
- E2E: not required.
- Acceptance: not required.
- Final local gate: `make validate-pr`, `make test-summary`, and PR-range `git diff --check origin/develop...HEAD` before PR submission unless unavailable with reason recorded.

## Phase Isolation Checks

- Control checkout status reviewed: clean `develop` at `89a6d3f docs: record stage 4 phase 3 cleanup`.
- Dedicated phase branch created or verified: `agent/codecs-lazy-samples-p4-sample-builder-provenance`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p4-sample-builder-provenance`.
- Branch base verified as current `develop`: yes, created from `origin/develop` after Phase 3 cleanup metadata.
- Earlier phase status verified as merged or blocked: Prep 1, Prep 2, and primary Phases 1 through 3 are merged and recorded.
- GitHub push and PR creation available: previously exercised in this workflow; verify again before PR.
- Stop if any check fails: stop before product code edits and return to manager if isolation, target branch, or PR infrastructure cannot be maintained.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: unused
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Builder requires datasource index iteration, split semantics, datasource-aware codec contexts, export orchestration, model formatting, cache/device behavior, member/alignment semantics, or new stable item identity.
- Missing requested locators cannot fail before partial sample construction.
- Probe paths load payloads, descriptors/index items are mutated, or record/item provenance must be pushed into codec contexts.
