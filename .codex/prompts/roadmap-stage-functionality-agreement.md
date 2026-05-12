# Roadmap Stage Functionality-Agreement Facilitation

Use this internal prompt for the managing agent during
`.codex/workflows/roadmap-version-planning.md`. This substage locks what is
being built and why before design work begins.

Read:

- `AGENTS.md`
- `docs/roadmap/stage-<N>/planning.md`
- Only the source files needed to resolve the next unresolved requirement branch

Task:

1. Draft or refresh the `Functionality Agreement Queue` before asking the
   maintainer anything.
2. Ensure the queue is dependency ordered and each item records related
   requirement IDs, impact, what is being locked, why it matters, recommended
   answer, trade-offs or rejected branches, repo evidence or direct resolution,
   exact feedback needed, and current state.
3. Resolve repo-answerable branches directly in `planning.md`. Mark them
   `repo-resolved` or `locked`; do not ask the maintainer to confirm clear
   evidence-backed defaults.
4. Order unresolved items by dependency first, then impact. Ask only one
   unresolved high-impact requirement question at a time.
5. Use this packet shape for each raised item:
   - What is being locked:
   - Why it matters:
   - Recommended answer:
   - Trade-offs:
   - Exact feedback needed:
6. After each maintainer answer, immediately update the queue item, linked
   functional-requirement rows, `Behavior Confirmation`, `Stage Gates`,
   `Stage Readbacks`, and any accepted assumption or deferral.
7. Continue until no high-impact functionality queue item remains in
   `needs maintainer discussion` or `blocked`.
8. If a new question is lower impact and does not block behavior confirmation or
   design work, record the recommendation and defer it instead of stalling the
   workflow.
9. Do not draft implementation phases or design decisions here.

Rules:

- Do not ask questions that the repo answers.
- Do not raise more than one unresolved item at once.
- Keep recommendations concrete and repo-grounded.
- If queue resolution changes scope materially, update capability triage and the
  module behavior map before moving on.
