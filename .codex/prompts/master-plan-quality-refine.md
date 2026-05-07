You are performing the single allowed master-plan quality refinement pass.

This prompt is intended for `master_plan_refiner`.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-2-master-plan.md`
- `.codex/templates/master-implementation-plan.md`
- `.codex/templates/master-plan-refinement-summary.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- The quality review findings from `master_plan_reviewer`

Task:

1. Update the master plan to resolve review findings that can be resolved safely.
2. Preserve confirmed user decisions and Stage 1 behavior commitments.
3. Tighten design choices, phase scope, validation, pathway policy, reviewability, and stop conditions.
4. Document accepted risks with revisit triggers.
5. Produce a refinement summary using `.codex/templates/master-plan-refinement-summary.md` if assigned a target path.
6. Mark the quality-gate refinement budget as used.

Rules:

- Do not implement code.
- Do not run repeated refinement loops.
- Do not invent new requirements.
- If a finding cannot be resolved without changing accepted design decisions, record the remaining blocker and stop for manager/maintainer decision.
