# Summary

- Wired `NativeTrainingEngine` into the shared Stage 15 observability contracts by attaching `TrainingResult.training_profile` for native runs that start setup.
- Added typed `TrainingPlan` inputs for resource monitors, async profile writers, generic training probes, checkpoint catalogs, checkpoint policies, restart selectors, and checkpoint hooks.
- Recorded native setup, teardown, loop, step, validation, checkpoint, resource, writer, probe, failure, and summary evidence through the shared `TrainingProfileRecorder` without introducing native-only profile/checkpoint families.
- Addressed automated review blockers by making teardown failures fail the returned result, recording metric-triggered checkpoint skip/unavailable evidence, and honoring non-failing `ProbeFailurePolicy` values with `UnavailableProbeEvidence`.

# Scientific And Contract Implications

- Native profile evidence is primitive and inspectable: event logs, scalar spans, resource traces, writer lifecycle records, probe results, checkpoint selection/restore/save/prune results, and deterministic compatibility summaries.
- Checkpoint hooks own serialization and deletion. Native coordinates policy timing and normalized evidence only, preserving the boundary between execution observability and artifact storage.
- Resource monitors and profile writers remain optional and dependency-light. Failures are recorded as evidence where possible while preserving fail-loud behavior for native observers/callbacks.
- Missing train batches before setup still return a stopped result without a profile; completed, failed, stopped-after-setup, validation, test, and predict paths attach profile evidence.

# Validation

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/training/test_plan.py tests/unit/rphys/training/test_backend.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_profiling.py tests/unit/rphys/training/test_probes.py tests/contracts/test_stage15_training_profile_contract.py tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/contracts/test_stage12_observability_contract.py tests/integration/test_stage15_native_observability_flow.py` - 63 passed
- `make test-package` - 72 passed
- `make test-unit` - 794 passed
- `make test-contract` - 187 passed
- `make test-integration` - 31 passed
- `make test-summary` - package 72, unit 794, contract 187, integration 31; e2e and acceptance suites not present
- `make validate-pr` - passed
- `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` - passed
- `git diff --check` - passed

# Assumptions And Residual Risk

- Tests use deterministic fake monitors, writers, probes, and checkpoint hooks; no real hardware profiler or durable checkpoint storage backend is added in this phase.
- Lightning bridge behavior, Stage 9 data-path producer instrumentation, and final documentation examples remain in later phases.
