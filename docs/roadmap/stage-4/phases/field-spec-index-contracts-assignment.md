# Phase Assignment: Stage 4 Prep 2 FieldSpec And FieldIndex Contract Tightening

## Manager Assignment

- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `Preparation Phase 2: FieldSpec And FieldIndex Contract Tightening`
- Roadmap slug: `codecs-lazy-samples`
- Phase slug: `field-spec-index-contracts`
- Stage descriptor: `Codecs And Lazy Sample Construction`
- Phase descriptor: `FieldSpec And FieldIndex Contract Tightening`
- Branch: `agent/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Base branch: `develop`
- Target branch: `develop`
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase Prep 2: FieldSpec And FieldIndex Contract Tightening`
- Workflow path: fast path
- Expanded-path trigger: none assigned; stop if immutability exposes documented public workflow pressure or if indexes need a real extension protocol.
- Plan quality gate: passed in `docs/roadmap/stage-4/implementation-plan.md`; implementation approval supplied in the user's current request.
- Phase isolation: dedicated branch and worktree required before any phase edit; one PR to `develop`; no local-only completion.
- Blockers: none at assignment.

## Scope

- Goal: freeze `FieldSpec` and clarify `FieldIndex` as a subclass-based base interface before codec and builder APIs depend on these declarations.
- In scope: `src/rphys/data/fields.py`, `src/rphys/io/indexes.py`, focused field/schema/index unit tests, lazy descriptor contract tests, package tests, docstrings in touched modules, and phase documentation artifacts.
- Out of scope: `FieldSpec.to_dict()`, schema manifests, descriptor fingerprints, field-index registries, seconds/spatial indexes, codecs, `SampleField`, `SampleBuilder`, datasource scanning, or public serialization additions.
- Decisions already approved: `FieldSpec` becomes frozen/slotted while explicitly unhashable; `DataSourceSchema` stores immutable declarations directly; `FieldIndex` wording changes from protocol to base class/interface with no registry or structural dispatch.
- Future-phase exclusions: codec contract work belongs to primary Phase 1; registry behavior belongs to primary Phase 2; lazy runtime and builder behavior belong to primary Phases 3 and 4.

## Validation Obligations

- Package: `make test-package` must pass with no unintended public export changes beyond Prep 1's `FieldContainer`.
- Unit: targeted fields, datasource schema, and IO index unit coverage must pass; broaden to `make test-unit`.
- Contract: `make test-contract` must pass, including runtime and lazy descriptor contracts.
- Integration: deferred; no integration behavior is in scope.
- E2E: deferred; no e2e behavior is in scope.
- Acceptance: deferred; no acceptance marker is expected for this prep phase.
- Final local gate: run `git diff --check`; broaden to `make validate-pr` and `make test-summary` during PR preparation if feasible.

## Phase Isolation Checks

- Control checkout status reviewed: clean on `develop` after Prep 1 metadata and cleanup.
- Dedicated phase branch created or verified: created from `develop`.
- Dedicated phase worktree created or verified: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep2-field-spec-index-contracts`.
- Branch base verified as current `develop`: `3b58ff0 docs: record stage 4 prep 1 cleanup`; `origin/develop` matches.
- Earlier phase status verified as merged or blocked: Prep 1 merged via PR #21 and recorded in the implementation plan.
- GitHub push and PR creation available: GitHub auth, fetch, push, PR creation, and merge were exercised successfully in Prep 1; open-PR check before Prep 2 returned none.
- Stop if any check fails: yes.

## Budget State

- Phase execution planning: unused
- Phase execution plan refinement: not needed unless fast-path plan has a blocker
- Implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Stop Conditions

- Freezing `FieldSpec` breaks a documented public workflow that cannot be adjusted within this phase.
- Implementation requires public `FieldSpec` serialization, schema snapshots instead of freezing, or a registry/structural protocol for indexes.
- `FieldIndex` behavior changes beyond wording, direct-construction failure, current serialized tag handling, or the existing `TemporalIndexSlice` implementation.
- Runtime, datasource schema, lazy IO, package, or contract tests expose a compatibility regression that cannot be fixed in scope.
