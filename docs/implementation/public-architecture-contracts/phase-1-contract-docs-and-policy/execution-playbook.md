# Execution Playbook: Public Architecture Contracts Phase 1 Contract Docs And Policy

Status: ready for phase implementation planning
Master plan: `docs/implementation/public-architecture-contracts/master-plan.md`
Roadmap item: `docs/roadmap/index.md`
Branch: `agent/public-architecture-contracts-p1-contract-docs-and-policy`
Worktree: `../rphys-worktrees/public-architecture-contracts-p1-contract-docs-and-policy`
Phase notes: `docs/implementation/public-architecture-contracts/phase-1-contract-docs-and-policy/phase-notes.md`
Public PR body: `docs/implementation/public-architecture-contracts/phase-1-contract-docs-and-policy/pr-body.md`
Quality gate: Stage 1 accepted; Stage 2 accepted; master-plan quality gate passed
Blockers: GitHub auth is invalid for `samcantrill`, blocking PR creation and merge until re-authenticated

## Compact Context Capsule

Goal: land the public architecture contract as a policy artifact before package tooling or code hardens public behavior.

Accepted decisions: first stable wave is `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, plus `rphys.errors`; API labels are `stable`, `provisional`, and `private/internal`; docs define ownership and policy, while implemented code becomes the contract after behavior exists; `loom` owns generic workflow/config/execution machinery; `_target_` import paths are the default extension mechanism and generic instantiation belongs to `loom`; registries are symbolic-name-only.

Constraints: this is docs-only. Do not create package code, tests, tooling, module homes, registry implementations, recipes, stages, or generated API reference.

## Ownership

- Files/modules owned by this phase:
  - `docs/architecture/public-contracts.md`
  - `README.md` link only if it materially improves discoverability
  - `docs/roadmap/index.md` implementation note only if needed and preserving existing local changes
- Files/modules explicitly out of scope:
  - `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, `LICENSE`
  - `src/rphys/**`
  - `tests/**`
  - future module homes for `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing`
- Public interfaces allowed to change:
  - Documentation policy and ownership text only.
  - No importable Python API is created or changed.
- Other active branches/worktrees to avoid:
  - Any phase branch under `../rphys-worktrees/public-architecture-contracts-p*-*` not owned by this worker.
  - Unrelated dirty changes in the foreground checkout.

## Current Source And Harness Findings

- Existing files that constrain this phase: `planning-notes.md`, `master-plan.md`, `architecture-refactor-risk-review.md`, and roadmap row for `Public architecture contracts`.
- Existing tests or harness behavior: no package/tooling harness is established yet; validation is manual docs review plus `git diff --check`.
- Import-boundary or dependency constraints: docs must keep generic workflow/config/execution/store/resume/locking/resource machinery in `loom`, not `rphys`.
- Scientific contract constraints: docs must require later public scientific components to document units, shapes, dtypes, coordinate frames, sampling rates, temporal alignment, leakage risks, failure behavior, and validation tests.
- GitHub status: `gh auth status` reports an invalid token for `samcantrill`; record this in phase notes and do not attempt PR creation until fixed.

## Scope Contract

The phase defines public policy, not runtime behavior. It must document:

- Stable first-wave module homes and central errors.
- Future/provisional module map and explicit deferral of later domains.
- API-label obligations for stable, provisional, and private/internal surfaces.
- Code-backed docs policy: no duplicate handwritten signatures once implementation exists.
- Strict `loom`/`rphys` boundary.
- `_target_` import paths as the default extension path and symbolic registries only.
- Optional dependency categories and lightweight base-import policy.
- Scientific-contract expectations for later packages.

No public Python import path, data shape, error class, or runtime behavior changes in this phase.

## Tasks

- Draft `docs/architecture/public-contracts.md` from the accepted planning notes and master plan.
- Include first-wave stable homes, future/provisional modules, forbidden early module homes, and ownership of `FieldRef`, `TemporalIndexSlice`, and `FieldView` under future `rphys.io`.
- Document `RemotePhysError` as the accepted root error name, with broad family errors planned for Phase 3.
- Document uv/Python 3.12 and temporary rights expectations at policy level without creating tooling files.
- Add only necessary discoverability links, preserving unrelated dirty content.
- Record commands and link-review evidence in phase notes.

## Pathway Eligibility

- Recommended pathway: fast, if the phase remains docs-only and accepted design decisions are not reopened.
- Fast-path rationale, if applicable: no code, package metadata, tests, public imports, dependencies, or scientific runtime behavior are changed.
- Criteria that would force standard pathway:
  - Any package code, tests, tooling metadata, dependency metadata, or public import path is added.
  - Accepted module ownership, API labels, `RemotePhysError`, registry policy, `_target_` policy, or `loom` boundary is changed.

## Implementation Plan Output

- Detailed implementation plan path: `docs/implementation/public-architecture-contracts/phase-1-contract-docs-and-policy/implementation-plan.md`
- Fast-path checklist path, if used: `docs/implementation/public-architecture-contracts/phase-1-contract-docs-and-policy/fast-path-checklist.md`

## Expected Commits

- Phase 0 playbooks, if this is the first Stage 3 implementation branch commit.
- Planning/checklist documents.
- Contract docs and any minimal docs links.
- Validation evidence and phase notes.
- Cleanup if review or checklist requires wording fixes.

## Design Impact

- Maintainability: separates policy from later code and avoids duplicate API signatures.
- Extensibility: reserves future module directions without making them importable or stable.
- Scientific workflow safety: records scientific documentation obligations before runtime APIs land.
- Source-tree boundaries: keeps this phase under docs and avoids package/tooling churn.

## Future Compatibility

Later packages can add concrete APIs under the documented module homes and link to code-backed API reference without rewriting the policy. Future docs may append references to implemented code as each owning package stabilizes behavior.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Wait to write contract docs until after code exists | Later phases need policy before they harden public imports and metadata. |
| Put all architecture policy in module docstrings | Module docstrings are poor governance artifacts and would require code before policy is reviewed. |
| Handwrite detailed signatures in docs | Accepted docs policy says code becomes the contract after implementation. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Docs mention planned module homes before all are importable | Policy must land before package skeleton | Phase 3 import skeleton lands or a module ownership decision is reopened |
| Exact optional dependency packages remain absent | Concrete backend behavior is deferred | Implementing real IO, torch, training, or analysis behavior |

## Reviewability

- Expected PR size and shape: small docs-only PR.
- Files and areas to inspect: public contract policy, roadmap/README links if changed, and consistency with accepted Stage 1/2 decisions.
- Scope-control checks: verify no code, tests, package metadata, dependencies, or future module homes were added.

## Verification

- Phase-specific commands:
  - `git diff --check`
  - `git diff --check -- docs/architecture/public-contracts.md docs/roadmap/index.md README.md`
- Full-suite command:
  - Not required for docs-only phase before tooling exists; record as not available if no project harness exists.
- Expected evidence to record:
  - Diff-check output.
  - Manual link review for touched docs.
  - Checklist confirming accepted labels and boundaries are present.

### Suite Obligations

- Package: not required.
- Unit: not required.
- Contract: manual review against planning notes and master plan.
- Integration: not required.
- E2E: not required.
- Opt-in: not required.

## Review Focus

- Standard pathway code review: only needed if the phase exceeds docs-only scope.
- Standard pathway scientific/workflow review: confirm scientific-contract obligations and `loom` boundary if standard pathway is triggered.
- Fast-path manager checklist: docs-only, no public import behavior, no dependencies, no design decisions reopened, links checked, `git diff --check` passed.

## Stop Conditions

- GitHub auth remains invalid when PR creation or merge is required.
- The docs cannot preserve accepted Stage 1/2 decisions without reopening them.
- Any implementation needs code, tooling, dependencies, future module homes, or runtime placeholders.
- Another worker has overlapping edits to `docs/architecture/public-contracts.md` or the same roadmap/README lines.

## Budget Status

- Implementation blocker cycles used: 0 of 2.
- Code review: not started; only required if standard pathway is selected.
- Scientific/workflow review: not started; only required if standard pathway is selected.
- Fast-path checklist: pending pathway decision.
- Pre-submit blocker gate: pending.

## Completion Notes

- Implementation summary: pending.
- Validation summary: pending.
- Review summary: pending.
- PR preparation: blocked until `gh auth status` succeeds.
- Merge and cleanup: pending.
- Remaining blockers: GitHub auth invalid for `samcantrill`.
