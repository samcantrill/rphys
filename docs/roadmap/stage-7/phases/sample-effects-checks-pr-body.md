# Summary

Implements Stage 7 Phase 3 sample field-effect enforcement on top of the Phase
2 `SampleOperation` foundation. The PR adds explicit sample execution
`copy_mode` support (`in_place`, `shallow`, `deep`), before/after field
snapshots, declared add/delete/replacement enforcement, and runtime
`sample_field_effects` metadata so sample-level mutations are inspectable
without materializing lazy payloads.

It also adds public deterministic sample wrappers and metadata records:
`SampleTransform`, `SampleCheck`, `SampleDecision`, and `SampleRoute`, plus the
focused `UndeclaredSampleFieldMutationError` for undeclared sample field-set
effects. Route and decision records remain informational metadata only.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-7/phases/sample-effects-checks.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/phases/sample-effects-checks.md`

# Phase Isolation

- Branch: `agent/stage-7-p3-sample-effects-checks`
- Worktree:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p3-sample-effects-checks`
- Base branch: `develop`
- Head branch: `agent/stage-7-p3-sample-effects-checks`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleOperation`, `SampleTransform`, and `SampleCheck` keep
  `Sample -> OperationResult` behavior, with `OperationResult.output` holding
  the execution `Sample`.
- Units/shapes/dtypes: no physiological payloads are resampled, filtered,
  normalized, reshaped, or moved across dtype/device boundaries in this phase.
- Sampling/alignment/provenance: declared-read preflight still uses
  non-payload field presence checks; mutation provenance is exposed as runtime
  `sample_field_effects` metadata with `copy_mode`, `added`, `removed`, and
  `replaced` locator strings.
- Pipeline-order implications: execution order is preflight, copy selection,
  before snapshot, callable execution, result validation, after snapshot,
  declared-effect enforcement, and metadata attachment.
- Leakage or subject/split implications: this phase does not inspect subject
  IDs, split labels, datasource records, loader policy, or trainer behavior.
  `SampleRoute` labels are opaque metadata and do not control drop/retry/split
  or workflow routing.
- Legacy parity or intentional behavior changes: Phase 2 sample operation
  behavior is preserved while adding deterministic enforcement for declared
  additions, deletions, renames-as-remove-plus-add, and same-locator
  `FieldValue` replacements. Payload-internal mutation inside an unchanged
  `FieldValue` and transparent read tracking remain explicitly out of scope.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not applicable for this phase
- [x] Acceptance or opt-in checks not applicable for this phase
- [x] Scientific/workflow contract review completed

Suite summary from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 31 | 31 |
| unit | passed | 471 | 471 |
| contract | passed | 82 | 82 |
| integration | passed | 8 | 8 |
| Overall | passed | 592 | 592 |

Commands run:

```text
make test-unit
make test-contract
make test-integration
make test-package
make validate-pr
make test-summary
git diff --check
```

`make validate-pr` passed `uv lock --check`, suite summary generation, sdist
and wheel build, and `git diff --check`.

# Risks And Follow-Up

- Payload-internal mutation under an unchanged `FieldValue` is not detected by
  this snapshot boundary; concrete transforms that mutate payloads must make
  their own scientific assumptions inspectable.
- Transparent read tracking is not implemented; declared reads remain an
  explicit operation contract.
- Exact-locator `dynamic_writes` may need broader view-family semantics during
  the later augmentation/view-writing phase.
- Future phases still own augmentation, sample pipeline mapping, batch APIs,
  export/cache/loader/trainer workflow behavior, payload-internal mutation
  detection, and transparent read tracking.
