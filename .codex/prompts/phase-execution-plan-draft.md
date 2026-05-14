You are creating the phase execution plan for one assigned rphys phase. This
prompt is intended for the `rphys_phase_planner` custom agent.

This is the default fast-path planning pass for a phase artifact. Create the
branch, create the worktree, inspect enough source and documentation context to
make the plan accurate, and write the durable phase execution plan artifact.

Read:

- `AGENTS.md`
- The selected implementation plan assigned by the manager
- The assigned phase
- `.codex/templates/phase-assignment.md`
- `.codex/templates/phase-execution-plan.md`

Create the phase branch/worktree from `develop`, then create a phase execution
plan from `.codex/templates/phase-execution-plan.md` using this destination:

```text
docs/roadmap/stage-<N>/phases/<phase-slug>.md
```

Worktree setup:

```bash
gh auth status
gh auth setup-git
git fetch origin
BRANCH="agent/<roadmap-slug>-p<n>-<phase-slug>"
BASE_BRANCH="develop"
WORKTREE_ROOT="/home/samcantrill/work/rphys-worktrees"
WORKTREE="$WORKTREE_ROOT/<roadmap-slug>-p<n>-<phase-slug>"
mkdir -p "$WORKTREE_ROOT"
git worktree add -b "$BRANCH" "$WORKTREE" "$BASE_BRANCH"
cd "$WORKTREE"
```

If GitHub or remote synchronization is unavailable, continue from the local
recorded `develop` only when the manager authorizes that fallback and record
the limitation in the phase execution plan.

The draft phase execution plan must include:

1. Branch, worktree, PR target `develop`, stage descriptor, phase descriptor,
   and intended PR title using
   `Stage <N> <Stage-Descriptor> - Phase <M>: <Phase-Descriptor>`.
2. Source implementation plan and source phase.
3. Workflow path: fast path by default or expanded path when assigned.
4. Objective, full-plan context, in-scope work, out-of-scope work, assumptions,
   design impact, future compatibility, alternatives rejected, and debt.
5. Scope contract covering public behavior, module boundaries, data shapes,
   error behavior, scientific semantics, and edge cases the executor must not
   redesign.
6. Files and areas to inspect.
7. Three to six implementation slices, not a line-by-line code recipe.
8. Test plan grouped by package, unit, contract, integration, e2e, and
   acceptance suites. For each suite, state required coverage, expected paths,
   assertions, or explicit deferral reason.
9. Validation commands, including targeted commands for development and final
   `make validate-pr`, `make test-summary`, and `git diff --check` unless
   explicitly unavailable.
10. Refinement and review budget status.
11. Handoff notes for implementation and stop conditions.

Planning rules:

- Be specific enough that the executor can implement without another planning
  pass on the fast path.
- Spend planning detail on scope boundaries, acceptance criteria, test
  obligations, risky decisions, and stop conditions.
- Do not expand the phase beyond its stated scope.
- Identify future-phase work and keep it out of scope.
- Explain how this phase preserves maintainability, extensibility, import
  boundaries, and scientific meaning.
- Commit only the phase execution plan with `git commit -m "plan: add phase execution plan"`.
- Stop after committing the phase execution plan. Do not implement code, run
  broad validation, open a PR, or refine the plan in this pass.
