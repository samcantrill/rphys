## Summary

- Update README status so it reflects the completed Stage 1-4 public contracts
  instead of the old Milestone 0 skeleton state.
- Expand glossary coverage for Stage 4 public concepts: structural codecs,
  explicit registries, load/save contexts, lazy sample fields, and the
  one-item sample builder bridge.
- Clarify public docstrings for runtime field containers, lazy sample fields,
  sample builders, builder provenance, probe results, and codec contexts.

## Scope And Scientific Contract

- Documentation-only closeout; no runtime behavior, public exports, real codec
  support, datasource discovery, export orchestration, cache policy, device
  movement, model formatting, or training behavior was added.
- The docs now state the key Stage 4 boundaries: `field()` can return lazy
  handles without loading, payload-demanding access may materialize once,
  codec contexts stay datasource-neutral, provenance remains builder-side, and
  save metadata persistence is explicit.

## Validation

- `make test-package`
  - 22 passed
- `make test-unit`
  - 310 passed
- `make test-contract`
  - 38 passed
- `make validate-pr`
  - lock check passed
  - package 22, unit 310, contract 38, integration 1 passed
  - build passed
  - `git diff --check` passed
- `make test-summary`
  - package 22, unit 310, contract 38, integration 1 passed
- `make test`
  - 371 passed
- `git diff --check origin/develop...HEAD`
  - passed

## Residual Risk

- No behavior or test logic changed in this phase. Remaining Stage 5+ work is
  still datasource discovery, views/splits/index manifests, operations, export
  orchestration, real codecs, training adapters, and downstream workflows.
