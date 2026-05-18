# Summary

- Added descriptive Stage 15 tier and restart records under `rphys.training.tiers`.
- Exported the new code-backed public names through `rphys.training` and package/import-boundary tests.
- Added unit and contract tests for standard tiers, same-path validation, restart checkpoint links, fingerprints, completion markers, compatibility notes, and primitive metadata.
- Added Stage 15 examples plus glossary/test-doc updates for public profile, checkpoint, tier, restart, data-path, Native, and Lightning evidence boundaries.

# Scientific And Contract Implications

- Tiers are descriptive evidence only. They record scale knobs and expected evidence for the same execution path; they do not schedule work, define speed thresholds, or introduce alternate fake paths.
- Restart snapshots link checkpoint refs or ids to loader, materialization, data-path, profile, checkpoint, completion-marker, and compatibility evidence without owning checkpoint payloads or restore execution.
- Records remain dependency-light and primitive at public edges, preserving base import boundaries.

# Validation

- Focused suite: `uv run pytest tests/unit/rphys/training/test_tiers.py tests/contracts/test_stage15_tier_restart_contract.py tests/package/test_import.py::test_stage_12_training_package_exports_only_code_backed_contract_names tests/package/test_import.py::test_stage_12_training_modules_export_only_code_backed_names tests/package/test_import_boundaries.py::test_stage_12_training_imports_do_not_load_frameworks_or_datasources` - 10 passed
- Optional installed-Lightning preflight - reported `absent`; real installed-Lightning acceptance skipped without importing Lightning
- `make test-package` - 72 passed
- `make test-unit` - 808 passed
- `make test-contract` - 195 passed
- `make test-integration` - 32 passed
- `make test-summary` - package 72, unit 808, contract 195, integration 32; e2e and acceptance suites not present
- `make validate-pr` - passed
- `UV_CACHE_DIR=/tmp/uv-cache uv lock --check` - passed
- `git diff --check` - passed

# Assumptions And Residual Risk

- Optional installed-Lightning acceptance remains environment-dependent and may be skipped with explicit absent/unsafe preflight evidence.
- Downstream orchestration may need additive tier or restart fields later, but fields that imply scheduling, artifact lifecycle, cost dashboards, or alternate execution paths remain out of scope.
