# Roadmap Stage Design-Agreement Facilitation

Use this internal prompt for the managing agent during
`.codex/workflows/roadmap-version-planning.md`. This substage locks how the
accepted functionality should be structured before validation and implementation
planning begin.

Read:

- `AGENTS.md`
- `docs/roadmap/stage-<N>/planning.md`
- Only the source files needed to resolve the next unresolved design branch

Task:

1. Draft or refresh the `Proposed Implementation Shape` summary first from the
   accepted behavior baseline and specialist evidence.
2. Draft or refresh the `Design Agreement Queue` before asking the maintainer
   anything.
3. Ensure the queue is dependency ordered and each item records related
   design-decision IDs, impact, what is being locked, why it matters,
   recommended answer, trade-offs or rejected branches, repo evidence or direct
   resolution, exact feedback needed, and current state.
4. Confirm that any future-roadmap/reuse safety findings are resolved or routed
   into concrete design revisions, explicit deferrals, revisit triggers,
   validation obligations, or maintainer discussion packets.
5. Resolve repo-answerable branches directly in `planning.md`. Mark them
   `repo-resolved` or `locked`; do not ask the maintainer to confirm clear
   evidence-backed defaults.
6. Order unresolved items by dependency first, then impact. Ask only one
   unresolved high-impact design question at a time.
7. Use this packet shape for each raised item:
   - What is being locked:
   - Why it matters:
   - Recommended answer:
   - Trade-offs:
   - Future-roadmap or reuse impact:
   - Exact feedback needed:
8. After each maintainer answer, immediately update the queue item, linked
   design-decision rows, `Design Decision Triage`, `Stage Gates`,
   `Stage Readbacks`, `Future Roadmap And Reuse Safety Review`, and any
   accepted assumption or deferral.
9. Continue until no high-impact design queue item remains in
   `needs maintainer discussion` or `blocked`.
10. Reopen only the relevant functionality-agreement queue item when a design
   blocker reveals a missing upstream behavior decision that cannot be resolved
   from repository evidence.
11. Do not draft implementation phases here.

Rules:

- Do not ask questions that the repo answers.
- Do not raise more than one unresolved item at once.
- Keep recommendations concrete and repo-grounded.
- If queue resolution changes design scope materially, refresh the proposed
  implementation shape and affected validation obligations before moving on.
