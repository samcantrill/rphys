You are preparing the PR body for a completed rphys phase. This prompt is
intended for `rphys_pr_preparer`.

This is the default fast-path PR preparation pass. Concisely summarize the
diff, scope, acceptance criteria, implementation notes, validation evidence,
risks, and review context in the durable PR body artifact. On the fast path,
also verify and open or prepare the PR in this pass.

Read:

- `AGENTS.md`
- The source implementation plan recorded in the phase execution plan
- The phase execution plan under `docs/roadmap/stage-<N>/phases/`
- The current diff
- Validation results
- `.github/pull_request_template.md`
- `.codex/templates/phase-pr-body.md`

Task:

1. Confirm you are inside the dedicated git worktree for this phase under
   `/home/samcantrill/work/rphys-worktrees`.
2. Confirm the branch name follows `agent/<roadmap-slug>-p<n>-<phase-slug>`.
3. Confirm the PR target branch is `develop`; use explicit GitHub CLI flags.
4. Confirm the implementation matches the assigned phase and future phases were
   not implemented early.
5. Confirm relevant tests were added or updated.
6. Confirm validation commands were run or explain why not. Prefer
   `make validate-pr` for the final local gate.
7. Run `make test-summary` when practical and use compact Markdown tables from
   its output as suite-level evidence. If it cannot run, explain why and
   summarize available targeted suite results.
8. Create a PR body at
   `docs/roadmap/stage-<N>/phases/<phase-slug>-pr-body.md` using
   `.codex/templates/phase-pr-body.md`.
9. Mark the PR body draft pass complete. Mark refine pass `not needed` on the
   fast path or `pending` on the expanded path.
10. On the fast path, open the PR if GitHub tooling and authentication are
   available. Use explicit `--base develop`,
   `--head agent/<roadmap-slug>-p<n>-<phase-slug>`, and `--title` flags from
   the phase execution plan.
11. Verify an opened PR with
   `gh pr view <PR> --json baseRefName,headRefName,state,url` and confirm
   `baseRefName` is `develop`.

Rules:

- Do not merge.
- Do not request GitHub reviewers or add human-review gating language.
- Do not perform implementation refinements; report blockers to the manager.
- Do not create test coverage at PR preparation time.
- Keep workflow internals in the phase execution plan, not the public PR body.
- Do not change workflow prompts, templates, `AGENTS.md`, or implementation
  plan process text from a product phase worktree unless explicitly assigned.
