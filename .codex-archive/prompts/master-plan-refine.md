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
5. Verify that the `Intent And Functionality Approval` records explicit maintainer approval before design discussion.
6. Verify that the `Design Decision Classification` records implementation details, recorded recommendations, needs-discussion decisions, and deferred/blocking decisions without forcing the maintainer through every design choice.
7. Verify that the `Maintainer Decision Walkthrough` records only the impactful unresolved design discussions and any maintainer-requested recommendation discussions, including approval/revision/deferral, resulting plan update, and remaining blocker status.
8. Verify that any required `Deep Design Review` records concrete API/invariant/failure/extension/downstream design discussion only where needed, maintainer approval/revision/deferral, resulting plan updates, and remaining blocker status.
9. Tighten phase order, file/module ownership, acceptance criteria, suite-level test obligations, standard/fast pathway guidance, review requirements, pre-submit blocker expectations, and stop conditions.
10. Confirm that Stage 3 uses one live `implementation-plan.md`, implements phases sequentially, and is not gated by human review.
11. Mark the refine pass complete in master-plan metadata.

Rules:

- Do not implement code.
- Do not erase confirmed user decisions.
- Do not convert proposed defaults into accepted decisions unless the walkthrough records maintainer approval or a safe explicit deferral.
- Do not treat high-level functionality approval as sufficient design approval for foundational or public-contract packages.
- Do not require the maintainer to step through every design decision; discuss only impactful decisions without strong recommendations and any recommendation the maintainer asks to discuss.
- Do not defer implementation decisions that Stage 3 agents need.
- If a decision remains ambiguous, record the exact question and stop for maintainer input.
- Do not create separate refinement, execution-playbook, phase-plan, checklist, phase-notes, review-report, or PR-body documents by default.
