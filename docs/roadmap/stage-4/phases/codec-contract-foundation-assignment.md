# Phase Assignment: Stage 4 Phase 1 Codec Public Contract Foundation

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `Phase 1: Codec Public Contract Foundation`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `codec-contract-foundation`
- Stage descriptor: `Codecs And Lazy Sample Construction`
- Phase descriptor: `Codec Public Contract Foundation`
- Branch: `agent/codecs-lazy-samples-p1-codec-contract-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p1-codec-contract-foundation`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 1: Codec Public Contract Foundation`
- Workflow path: fast path
- Expanded-path trigger: none assigned; stop if codec records need datasource-aware context, manifest/export policy, public fake codec, registry behavior, or runtime sample behavior.
- Plan quality gate: passed; Prep 1 and Prep 2 are merged and recorded.
- Phase isolation: dedicated branch and worktree required before any phase edit; one PR to `develop`; no local-only completion.
- Blockers: none at assignment.

## Scope

- Goal: establish the Stage 4 IO public contract without implementing runtime lazy samples or full registry operation behavior.
- In scope: `src/rphys/io/codecs.py`, conditional `src/rphys/io/__init__.py`, exercised concrete errors in `src/rphys/errors.py`, package import/export tests, focused IO unit tests for records/errors/imports, and phase artifacts.
- Out of scope: registry matching algorithms, synthetic codec behavior, `SampleField`, `SampleBuilder`, datasource scanning, datasource-aware codec contexts, export layouts, metadata handlers, real codecs, hidden discovery, and global default registries.
- Decisions already approved: structural/duck-typed `FieldCodec`; datasource-neutral typed contexts/results; `SaveContext.target: FieldRef`; narrow `MetadataSavePolicy`; only exercised concrete errors; lightweight canonical imports.
- Future-phase exclusions: registry operations belong to Phase 2; lazy runtime fields to Phase 3; sample builder provenance to Phase 4; docs hardening to Phase 5.

## Validation Obligations

- Package: `make test-package` must pass if `rphys.io` exports codec names.
- Unit: targeted codec records/errors/imports tests must pass; broaden to `make test-unit`.
- Contract: not required by phase plan unless touched behavior warrants, but `make validate-pr` later includes it.
- Integration/E2E/Acceptance: deferred; no runtime materialization or dataset behavior is in scope.
- Final local gate: run `git diff --check`; run `make validate-pr` and `make test-summary` during PR preparation if feasible.

## Phase Isolation Checks

- Control checkout status reviewed: clean on `develop`.
- Dedicated phase branch created or verified: created from `develop`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p1-codec-contract-foundation`.
- Branch base verified as current `develop`: `32aa7d1 docs: record stage 4 prep 2 cleanup`; `origin/develop` matches.
- Earlier phase status verified as merged or blocked: Prep 1 and Prep 2 merged and recorded.
- GitHub push and PR creation available: GitHub auth, push, PR creation, and merge were exercised successfully in previous phases; open-PR check before Phase 1 returned none.
- Stop if any check fails: yes.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: not needed unless fast-path plan has a blocker
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Implementation needs registry resolution behavior, synthetic codec execution, datasource-aware codec contexts, export orchestration, metadata handlers, public fake codecs, runtime `SampleField`, `SampleBuilder`, or global discovery.
- Public names cannot remain lightweight at package import.
- Record shape requires untraced datasource provenance, manifest semantics, stable item identity, member/alignment semantics, or descriptor mutation.
