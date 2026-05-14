You are refining the PR body and submission readiness for an expanded-path
rphys phase. This prompt is intended for `rphys_pr_preparer`.

Read:

- `AGENTS.md`
- The source implementation plan
- The phase execution plan
- The existing PR body draft
- The current diff and validation evidence
- Any manager pre-submit blocker notes

Task:

1. Resolve PR-body, evidence, metadata, or explanation blockers only.
2. Verify the PR body accurately reflects the diff, scope, scientific contract
   implications, tests, risks, and follow-ups.
3. Confirm the pre-submit blocker gate has no unresolved known blockers.
4. Open or prepare the PR against `develop` with explicit base/head/title flags.
   The title must match
   `Stage <N> <Stage-Descriptor> - Phase <M>: <Phase-Descriptor>` from the phase
   execution plan.
5. Verify the opened PR target and record facts in the phase execution plan.

Rules:

- Do not change implementation code or tests.
- Do not merge.
- Do not request human GitHub reviewers.
- If implementation, validation, or scope blockers remain, report them to the
  manager instead of submitting the PR.
