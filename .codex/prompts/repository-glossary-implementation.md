You are implementing a repository glossary and vocabulary guide in the current
repository.

Goal:

- Create a glossary file that clarifies the language used in the repository and
  improves consistency across code, docs, tests, and contributor guidance.
- Base the glossary primarily on existing repository vocabulary and documented
  contracts rather than inventing a new taxonomy.
- Link the glossary from the repository's agent or contributor instructions
  when an appropriate file exists, such as `AGENTS.md`, `CONTRIBUTING.md`, or a
  docs index.

Default naming rule:

- If the file is mainly definitional, prefer `docs/GLOSSARY.md`.
- Use `docs/LANGUAGE.md` only when the repository clearly wants a broader
  writing or style guide rather than a glossary.

Read first:

- `AGENTS.md` if present
- `README.md`
- `docs/` architecture, roadmap, design, API, and terminology docs
- Public package/module docstrings for naming-heavy modules
- Contract or API tests that demonstrate vocabulary
- Any contributor docs such as `CONTRIBUTING.md`

Before editing:

1. Inspect `git status` and preserve unrelated local changes.
2. Inspect existing terminology used in docs, public APIs, tests, and naming
   contracts.
3. Determine whether the repository already has a glossary, terminology guide,
   naming guide, or equivalent file.

If the user has not already clarified intent, ask a short bounded quiz before
writing:

1. Is the goal mainly definitions, a style guide, or both?
2. Should the document be descriptive, normative, or both?
3. Who is the primary audience: contributors, maintainers, downstream users, or
   all three?
4. Should it cover only domain nouns, or also naming rules and discouraged
   terms?
5. Should it summarize existing language, replace conflicting language, or
   both?

Implementation task:

1. Decide on the right file name, usually `docs/GLOSSARY.md`.
2. Draft the glossary as a concise, contributor-facing reference.
3. Make it both descriptive and normative when that matches the user's intent:
   describe how the repository currently uses terms and state preferred future
   usage.
4. Prefer terms that are already code-backed, documented, or test-backed.
5. When helpful, include an "avoid", "discourage", or "distinguish from"
   column so nearby terms do not get conflated.
6. Cover both high-level and low-level vocabulary when the repository has both.
7. Keep the glossary practical. It should help contributors choose words and
   names, not just define concepts abstractly.
8. If needed, add small cross-links from canonical docs so the glossary is
   discoverable, but do not create contradictions about source-of-truth status.
9. Add a small link to the glossary in `AGENTS.md` or the nearest equivalent
   contributor guide when appropriate.

Preferred document shape:

- Short introduction explaining that the file standardizes repository language.
- A note explaining whether the file is descriptive, normative, or both.
- A short "How to use this file" section.
- Grouped glossary sections such as:
  - repository and workflow terms
  - domain or modeling terms
  - data and naming terms
  - runtime, IO, or lifecycle terms
  - common metadata or identity terms
- A short set of usage rules or naming heuristics near the end.
- A "See also" section linking to the canonical docs or tests the glossary is
  derived from.

Quality bar:

- Do not silently redefine established public API terms.
- Do not create a second competing architecture document.
- Distinguish clearly between:
  - canonical API terms
  - descriptive English allowed in prose
  - discouraged or out-of-scope terms
- Use repository-local evidence for claims whenever possible.
- Keep wording concrete enough that maintainers can review individual entries.

If you find conflicts:

- Prefer existing code-backed public contracts and canonical architecture docs.
- Use the glossary to summarize and clarify them.
- Only edit canonical docs when a small cross-link or contradiction fix is
  necessary.

Validation:

- Run `git diff --check`.
- If the repository has fast doc validation or linting relevant to Markdown,
  run the smallest appropriate check.
- Summarize what changed, what was linked, and any unresolved vocabulary
  conflicts or terms that still need maintainer decisions.
