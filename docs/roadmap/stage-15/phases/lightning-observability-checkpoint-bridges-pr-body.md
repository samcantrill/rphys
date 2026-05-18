# Summary

- Added a Lightning callback/profiler bridge that normalizes public Lightning lifecycle hooks into shared rphys events, spans, resource traces, monitor lifecycle records, writer results, probe results, and checkpoint evidence.
- Added checkpoint policy mapping for public `ModelCheckpoint` kwargs plus restart-selector to `ckpt_path` resolution.
- Added fake-Lightning bridge tests covering rank/device attribution, resource monitors, async profile writers, model/data probes, checkpoint save/restore/prune evidence, recency-pruner evidence, and profiler spans.
- Kept Lightning-specific behavior isolated to `rphys.training.lightning`; base training imports remain dependency-light.

# Scientific And Contract Implications

- Outputs remain shared `TrainingResult` and `TrainingProfile` records; no Lightning-specific result/profile family is introduced.
- Public Lightning hooks are treated as evidence adapters only. Raw Lightning trainer state, private callback internals, checkpoint payloads, tensors, and framework profiler timelines are not exposed.
- Recency retention is recorded as rphys pruning evidence because Lightning's built-in `ModelCheckpoint` does not directly implement rolling keep-last-N retention.
- Probe failures under the bridge are recorded as unavailable diagnostic evidence with record-and-continue behavior.

# Validation

- Focused suite: `uv run pytest tests/unit/rphys/training/test_lightning.py tests/unit/rphys/training/test_policies.py tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 15 passed
- Optional installed-Lightning preflight - reported `absent`; real installed-Lightning acceptance skipped without importing Lightning
- `make test-package` - 72 passed
- `make test-unit` - 804 passed
- `make test-contract` - 192 passed
- `make test-integration` - 32 passed
- `make test-summary` - package 72, unit 804, contract 192, integration 32; e2e and acceptance suites not present
- `make validate-pr` - passed
- `uv lock --check` - passed
- `git diff --check` - passed

# Assumptions And Residual Risk

- Optional installed-Lightning acceptance depends on the local environment. The adapter still performs metadata-only preflight first and blocks known unsafe versions by default.
- Phase 7 covers public callback/profiler/checkpoint hooks and fake DDP-style rank attribution, not full distributed/private-state parity.
