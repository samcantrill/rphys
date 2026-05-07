You are refining a Stage 2 rphys master implementation plan before quality review.

Read:

- `AGENTS.md`
- `.codex/workflows/stage-2-master-plan.md`
- `.codex/templates/master-implementation-plan.md`
- `docs/implementation/<roadmap-slug>/planning-notes.md`
- `docs/implementation/<roadmap-slug>/master-plan.md`
- Relevant repository files needed to verify current boundaries

Task:

1. Refine the same master-plan artifact until it is decision-complete for Stage 3.
2. Tighten behavior model, public/agent-visible behavior, unsupported behavior, failure behavior, and resume behavior.
3. Tighten structure, ownership boundaries, dependency direction, extension points, and coupling avoided.
4. Ensure every material decision records alternatives, rationale, maintainability/extensibility impact, validation obligation, residual risk, and revisit trigger for debt.
5. Tighten phase order, file/module ownership, acceptance criteria, suite-level test obligations, standard/fast pathway guidance, review requirements, pre-submit blocker expectations, and stop conditions.
6. Confirm that Stage 3 uses one live `implementation-plan.md`, implements phases sequentially, and is not gated by human review.
7. Mark the refine pass complete in master-plan metadata.

Rules:

- Do not implement code.
- Do not erase confirmed user decisions.
- Do not defer implementation decisions that Stage 3 agents need.
- If a decision remains ambiguous, record the exact question and stop for maintainer input.
- Do not create separate refinement, execution-playbook, phase-plan, checklist, phase-notes, review-report, or PR-body documents by default.
