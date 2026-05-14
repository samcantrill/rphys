# Phase Assignment: Stage 4 Prep 1 Field Container Protocol

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `Preparation Phase 1: Field Container Protocol`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `field-container-protocol`
- Stage descriptor: `Codecs And Lazy Sample Construction`
- Phase descriptor: `Field Container Protocol`
- Branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep1-field-container-protocol`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase Prep 1: Field Container Protocol`
- Workflow path: fast path
- Expanded-path trigger: none assigned; keep scope narrow and stop if lazy-field-specific protocol design becomes necessary.
- Plan quality gate: passed in `docs/roadmap/stage-4/implementation-plan.md`; maintainer implementation approval supplied in the current request.
- Phase isolation: dedicated branch and worktree required before any phase edit; one PR to `develop`; no local-only completion.
- Blockers: none at assignment.

## Scope

- Goal: add the public runtime `FieldContainer` protocol and public field iteration surface before lazy fields widen runtime semantics.
- In scope: `rphys.data.containers`, `rphys.data.contracts`, `rphys.data.collation`, conditional `rphys.data` export, focused runtime unit/contract/package tests, and phase documentation artifacts.
- Out of scope: `SampleField`, codecs, `SampleBuilder`, payload loading, lazy state, retry/cache policy, datasource behavior, collation policy expansion, or changed loaded `Sample`/`Batch` accessor semantics.
- Decisions already approved: public field-container protocol; `Sample` and `Batch` expose `field_items()`; `SampleContract` and LIST collation use public protocol behavior; import-boundary cleanliness remains required.
- Future-phase exclusions: lazy field compatibility belongs to primary Phase 3; codec and registry behavior belongs to primary Phases 1 and 2; builder provenance belongs to primary Phase 4.

## Validation Obligations

- Package: `make test-package` must pass if `rphys.data` exports `FieldContainer`.
- Unit: targeted `make test-unit` coverage for containers, contracts, and collation must pass.
- Contract: `make test-contract` must pass, including runtime core coverage.
- Integration: deferred; no integration behavior is in scope.
- E2E: deferred; no e2e behavior is in scope.
- Acceptance: deferred; no acceptance marker is expected for this prep phase.
- Final local gate: run `git diff --check`; broaden to `make validate-pr` and `make test-summary` during PR preparation if feasible.

## Phase Isolation Checks

- Control checkout status reviewed: clean on `develop` before worktree creation.
- Dedicated phase branch created or verified: created from `develop`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep1-field-container-protocol`.
- Branch base verified as current `develop`: `e7d95fc docs: revised roadmap items`; `origin/develop` matches.
- Earlier phase status verified as merged or blocked: no earlier Stage 4 phase exists.
- GitHub push and PR creation available: `gh auth status`, `gh auth setup-git`, Git HTTPS check, fetch, and open-PR check passed with approved network access.
- Stop if any check fails: yes.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: not needed unless fast-path plan has a blocker
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Implementing this phase requires `SampleField`, codec imports, payload loading, datasource behavior, collation redesign, or changed loaded-runtime accessor semantics.
- The public protocol needs lazy-field-specific types before primary Phase 3.
- Import-boundary tests show `FieldContainer` cannot be exported without pulling heavy or unrelated modules.
- Runtime unit or contract tests expose a loaded-sample compatibility break that cannot be fixed within this phase.
