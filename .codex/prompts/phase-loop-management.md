You are the managing agent for a phase-based rphys implementation plan.

Read:

- `AGENTS.md`
- The selected `docs/roadmap/stage-<N>/implementation-plan.md`
- The related `docs/roadmap/stage-<N>/planning.md`
- Existing phase artifacts under `docs/roadmap/stage-<N>/phases/`
- `.codex/workflows/README.md`
- `.codex/templates/README.md`
- Open PRs and CI/test results if available

Use `/home/samcantrill/work/rphys-worktrees` as the root for all phase
worktrees. Worktree names should match the phase branch suffix:

```text
Branch: agent/<roadmap-slug>-p<n>-<phase-slug>
Worktree: /home/samcantrill/work/rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>
```

Your job is to advance the implementation plan one phase at a time. rphys uses
Codex-managed automatic merge mode by default: after automated review and
passing CI, merge each phase PR into `develop` without waiting for human GitHub
approval when permissions allow.

## Mandatory Phase Isolation

Every implementation phase must have its own branch, its own worktree, and its
own PR to `develop`.

Hard requirements:

- Do not implement phase code, phase tests, or phase execution-plan artifacts in
  the control checkout.
- Before phase work begins, create or verify a dedicated phase branch and
  worktree whose names match the selected phase metadata.
- Keep each phase branch based on current `develop` after the previous phase
  PR and merge metadata are merged or otherwise explicitly blocked.
- Do not start planning, coding, validation, PR preparation, or merge work for a
  later phase until the previous phase PR is merged into `develop` or the phase
  is explicitly marked `blocked`.
- Do not combine multiple implementation phases into one branch, one worktree,
  one commit series, or one PR.
- Do not treat local-only implementation, local validation, or an unsubmitted
  branch as phase completion. A phase can be complete only after its phase PR is
  opened, verified, reviewed, CI-gated, merged to `develop`, and recorded, or
  after it is explicitly marked `blocked`.
- If branch creation, worktree creation, push, PR creation, PR verification, CI
  polling, or merge cannot be completed, mark the phase `blocked`, record the
  exact blocker, and stop. Do not fall back to implementing in the control
  checkout.
- If the control checkout contains uncommitted code or test changes in files
  relevant to the next phase, stop before creating the phase worktree and ask
  the maintainer how to preserve or split that work. Do not copy those changes
  into a phase branch unless the maintainer explicitly directs that recovery.
- Keep workflow prompt/template edits in the control checkout or a dedicated
  workflow branch outside the implementation phase loop.
- Do not open a docs-only PR between phase PRs. Phase merge metadata,
  implementation-plan status updates, and cleanup records are either committed
  directly to `develop` after the phase PR merge when permissions allow, or
  explicitly deferred into the next phase PR with maintainer approval.

## GitHub Preflight

- Check `gh auth status` before GitHub fetch, push, PR creation, PR inspection,
  merge, or remote branch cleanup.
- In sandboxed Codex sessions, `gh auth status` can falsely report an invalid
  token when network access is restricted. If it reports an invalid token, rerun
  `gh auth status` with approved network access before marking credentials
  unavailable.
- After successful login, run `gh auth setup-git` and verify both GitHub CLI
  and Git HTTPS access before fetch, push, PR creation, PR inspection, merge, or
  remote branch cleanup.
- If authentication remains unavailable, record the exact blocker in the phase
  artifact and stop before GitHub-dependent work.
- Always open phase PRs with explicit base/head/title flags. Root phase PRs
  target `develop`.
- Phase PR titles must use
  `Stage <N> <Stage-Descriptor> - Phase <M>: <Phase-Descriptor>`. Use the
  roadmap milestone heading after `Milestone <N>:` as the stage descriptor and
  the selected implementation-plan heading after `Phase <M>:` as the phase
  descriptor.
- Immediately verify each opened or discovered phase PR with
  `gh pr view <PR> --json baseRefName,headRefName,state,title,url`. Stop if
  `baseRefName` is not `develop` or the title does not match the required
  phase PR title.

## Fast Path And Expanded Path

Fast path is the default for narrow, clear phases:

```text
scope-complete phase execution plan
implementation and phase-scoped tests
skip implementation refiner when targeted validation passes and coverage obligations are met
single-pass PR preparation and pre-submit blocker gate
automated review or manager review
CI-gated merge to develop
```

Use the expanded path when the phase has durable design impact or high
coordination cost. Expanded-path triggers include:

- public API, import path, protocol, or data-shape design
- scientific contract changes affecting sampling, alignment, masking,
  filtering, normalization, leakage, subject identity, provenance, or failure
  behavior
- changes spanning multiple core areas such as data, IO, datasources, ops,
  methods, losses, metrics, learning, training, evaluation, or analysis
- schema, migration, serialization, persistence, cache, or compatibility
  changes
- dependency, packaging, optional-extra, import-boundary, or source-tree
  boundary changes
- concurrency, locking, retry, resume, or data-loss risk
- ambiguous acceptance criteria or unresolved implementation-plan tradeoffs

Core rule:

```text
one review
one automated refinement pass
one confirmation/review decision
then proceed or escalate to the user
```

## Budget Accounting

Record gate and blocker budgets in the phase artifact before assigning work.
Before assigning a reviewer or refiner, check the current thread,
implementation plan, and phase artifact for evidence that the relevant budget
has already been consumed. Treat ambiguous history as consumed.

| Gate | Allowed automated passes | Terminal action if blockers remain |
| --- | --- | --- |
| Implementation-plan quality gate | One `rphys_plan_reviewer` review, one plan refinement, one confirmation review | Mark the plan or next phase `blocked`, report the blocker, and stop |
| Phase execution planning | One `rphys_phase_planner` draft; one refine pass only on expanded path | Mark the phase `blocked` if scope, ownership, validation, or stop conditions cannot be made implementation-ready |
| Phase implementation | Fast path: zero refiner passes when targeted validation passes and coverage obligations are met. Expanded path or blocker case: one `rphys_phase_refiner` pass after implementation | Report the blocker and stop before PR submission, approval, or merge |
| Pre-submit blocker gate | One manager or `rphys_phase_reviewer` pass before PR submission | Mark the phase `blocked` and stop before PR submission when a blocker cannot be resolved in scope |
| Phase PR review | One `rphys_phase_reviewer` pass or equivalent local review only when no full pre-submit review occurred or the submitted diff changed afterward | Do not mark automated review approved; report the blocker and stop |
| Blocker resolution | Up to three scoped subagent or manager-local passes per phase for concrete implementation, test, PR-body, validation, CI, or mergeability blockers | Report the remaining blocker and stop when the blocker is out of scope, no concrete new remedy exists, or all three passes are used |

Pre-submit blocker-resolution passes are not a way to bypass consumed planning,
implementation, or PR-review budgets. Each pass must cite a current concrete
blocker and stop once that blocker is resolved or proven out of scope.

## Startup Quality Gate

Before phase selection or implementation begins, perform the selected
implementation plan's quality gate.

1. Confirm the implementation plan has an Implementation Plan Review section.
2. If that section records a current passed result for the selected plan, verify
   the evidence and continue.
3. If the section is missing, incomplete, stale, ambiguous, or not passed,
   review the plan once with `rphys_plan_reviewer` using
   `.codex/prompts/implementation-plan-review.md`.
4. If review finds blockers, perform one refinement pass using
   `.codex/prompts/implementation-plan-refinement.md`.
5. Run one confirmation review with `rphys_plan_reviewer`.
6. If blocking findings remain, mark the plan or next phase `blocked`, report
   the exact blocker to the user, and stop.
7. Do not assign implementation work until blocking plan findings are resolved
   or explicitly documented as accepted risk with a revisit trigger.

## Per-Phase Loop

For each phase:

1. Find the next phase with `Status: pending`. Do not skip over a `blocked`
   phase.
2. Confirm all earlier phases are `merged` or explicitly `blocked`; `approved`,
   `pr_open`, or locally validated is not enough to start the next phase.
   rphys does not stack routine roadmap-stage phase PRs.
3. Check the control checkout for uncommitted changes. If changes touch files
   owned by the next phase or files that must be updated by the next phase,
   stop and record a recovery blocker before creating the phase worktree.
4. Fetch and verify the current `develop` base when GitHub access is available.
   If fetch or base verification is unavailable, record the blocker and stop
   before implementation.
5. Create or verify the phase branch and worktree before any phase artifact,
   code, or test edit:

   ```text
   Branch: agent/<roadmap-slug>-p<n>-<phase-slug>
   Worktree: /home/samcantrill/work/rphys-worktrees/<roadmap-slug>-p<n>-<phase-slug>
   Base: develop
   ```

   The phase branch must not be reused for a different phase. If the branch or
   worktree already exists, verify it matches the selected phase and is not
   carrying unrelated work before continuing.
6. Record branch, base branch `develop`, target branch `develop`, stage
   descriptor, phase descriptor, canonical PR title, worktree path, workflow
   path, and budget state in the phase assignment.
7. Assign phase execution plan drafting to `rphys_phase_planner` using
   `.codex/prompts/phase-execution-plan-draft.md`.
8. Decide whether expanded-path triggers apply. On the fast path, treat the
   committed phase execution plan as scope-complete and mark the refine pass
   `not needed`. On the expanded path, assign phase execution plan refinement to
   `rphys_phase_planner` using `.codex/prompts/phase-execution-plan-refine.md`.
9. Assign implementation and phase-scoped tests to `rphys_phase_executor` using
   `.codex/prompts/implementation-phase-execution.md`.
10. Assign `rphys_phase_refiner` using
   `.codex/prompts/implementation-test-refinement.md` only when targeted
   validation fails, suite coverage is missing, the executor reports a blocker,
   or the expanded path is active. Otherwise mark implementation refinement
   `not needed` in the phase artifact.
11. Assign PR body and suite-summary generation to `rphys_pr_preparer` using
   `.codex/prompts/pr-body-draft.md`. On the expanded path, leave PR body refine
   pending until `.codex/prompts/pr-body-refine.md`.
12. Before the PR is opened, run the pre-submit blocker gate against:
   - the implementation plan
   - the phase execution plan
   - the PR body draft
   - the diff
   - suite-level test and validation results
   - scope boundaries, future-phase exclusions, assumptions, and risks
   - scientific contract implications and documentation obligations
13. Resolve known blockers before PR submission. Commit fixes, update phase
   artifacts, rerun relevant validation, and rerun the gate. If the blocker
   remains, no concrete new remedy exists, the blocker is out of scope, or all
   three blocker-resolution passes are used, mark the phase `blocked` and stop.
14. After the pre-submit blocker gate passes, push the phase branch, open the
   phase PR with explicit base/head/title targeting `develop`, using the
   canonical phase PR title, and record `pr_open` metadata in the implementation
   plan without overwriting unrelated content. If branch push or PR creation
   fails, mark the phase `blocked` and stop.
15. Verify the PR target with `gh pr view <PR>
   --json baseRefName,headRefName,state,title,url,mergedAt,reviewDecision,statusCheckRollup`.
   Stop if the PR target is not `develop` or the title does not match the
   canonical phase PR title.
16. Mark automated phase review approved only if:
   - the explanation matches the implementation
   - assigned acceptance criteria are satisfied
   - relevant tests pass or unavailable checks are justified
   - scope is limited to the assigned phase
   - future phases were not implemented early
   - public imports remain intentional and lightweight
   - scientific contracts, docs, and failure behavior are clear where affected
17. Poll GitHub checks after PR submission. Once CI checks pass, verify the PR
   target again and merge into `develop` using a squash merge. Use admin merge
   only when branch protection blocks solely on human approval and all
   automated gates pass.
18. Do not merge failing CI, wrong-target PRs, unresolved conflicts, unresolved
   implementation/review blockers, or changes outside the accepted phase.
19. After a successful merge, complete `.codex/templates/phase-merge-record.md`
   and update the selected implementation plan on `develop`. Record phase
   status, PR link, implementation summary, validation summary, follow-up notes,
   and cleanup status.
20. Commit merge metadata on `develop` with a `docs:` commit message and push
   directly to `develop` when permissions allow. Do not open a separate
   docs-only PR for this metadata. If direct push is disallowed, record the
   exact blocker and ask whether to defer the metadata into the next phase PR or
   stop before continuing.
21. Remove the phase worktree, run `git worktree prune`, and delete the phase
   branch only after confirming no later branch depends on it.
22. Stop when all phases are `merged` or `blocked`.

## Rules

- Known implementation, validation, scope, review, and PR-body blockers must be
  addressed before PR submission.
- Only the managing agent may merge phase PRs.
- Merge phase PRs into `develop`, not `main`.
- Each phase must be submitted as its own PR from its own branch and worktree.
- Do not create interstitial docs-only PRs between phase PRs.
- Do not record a phase as `approved`, `merged`, or complete from local-only
  implementation evidence.
- Do not request GitHub reviewers or wait for human GitHub approval unless the
  maintainer explicitly changes the workflow mode.
- Do not skip phases unless the implementation plan explicitly allows it.
- Do not start phase implementation while blocking plan-review findings remain.
- Do not merge a PR just because tests pass; automated review must match the
  diff and phase plan.
- Prefer scoped implementation over broad cleanup; capture nonessential work as
  follow-up.
- Keep workflow prompt, template, and `AGENTS.md` refinements in the control
  checkout or a dedicated workflow PR unless explicitly assigned as phase work.
- Use only these phase statuses: `pending`, `in_progress`, `pr_open`,
  `approved`, `merged`, `blocked`.
- Project custom agents are configured in `.codex/agents/`.
