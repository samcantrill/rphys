# Summary

Implements roadmap Stage 7 Phase 4, adding reproducible sample augmentation support on top of the Phase 3 sample-operation enforcement path.

The PR adds `SampleAugmentationParams` and `SampleAugmentation`, with separate parameter sampling and deterministic parameter application, runtime replay metadata, linked-field and view-locator evidence, explicit field-permission enforcement for generated view writes, and package/contract/integration coverage for the public surface.

# Links

- Roadmap stage: `docs/roadmap/stage-7/planning.md`
- Phase plan: `docs/roadmap/stage-7/phases/sample-augmentation-views.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/planning.md`

# Phase Isolation

- Branch: `agent/stage-7-p4-sample-augmentation-views`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p4-sample-augmentation-views`
- Base branch: `develop`
- Head branch: `agent/stage-7-p4-sample-augmentation-views`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleAugmentation` accepts one `Sample` and returns the same execution `Sample` through `OperationResult`, preserving Phase 3 copy-mode and field-effect behavior.
- Units/shapes/dtypes: the base augmentation wrapper remains dependency-light and does not interpret payload units, shapes, dtypes, devices, or backend arrays. `SampleAugmentationParams.values` accepts only immutable primitive or nested lightweight values.
- Sampling/alignment/provenance: sampling and application are split into public `sample_params()` and `apply_params()` methods. `run()` samples exactly once, applies the sampled params, and records runtime replay evidence including context seed material, linked fields, and view locators.
- Pipeline-order implications: the wrapper remains an `OperationStep` through `SampleOperation`; specialized pipeline composition remains Phase 5 scope.
- Leakage or subject/split implications: no split, subject, loader, cache, trainer, or model policy is introduced. Replay evidence is runtime metadata only.
- Legacy parity or intentional behavior changes: this is additive Stage 7 behavior. It preserves Phase 3 exact locator mutation enforcement and rejects reserved replay metadata collisions.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present
- [x] Acceptance or opt-in checks not present
- [x] Scientific/workflow contract review completed through phase-plan readback and pre-submit gate

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

Suite evidence from `make test-summary`:

| Suite | Result | Evidence |
| --- | --- | --- |
| package | passed | 32 passed |
| unit | passed | 483 passed |
| contract | passed | 85 passed |
| integration | passed | 9 passed |
| e2e | not present | 0 tests |
| acceptance | not present | 0 tests |

# Risks And Follow-Up

- User-provided augmentation callables can still hide their own RNG use; the base wrapper prevents package-level global/default RNG behavior and records replay evidence for sampled params.
- Replay metadata is intentionally runtime evidence, not a durable cache/export schema.
- Phase 5 owns specialized sample pipeline composition; Phase 6 owns provisional batch behavior.
