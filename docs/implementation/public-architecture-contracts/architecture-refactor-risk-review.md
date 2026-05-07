# Architecture Refactor-Risk Review: Public Architecture Contracts

## Metadata

- Reviewed plan: `docs/implementation/public-architecture-contracts/master-plan.md`
- Architecture source: `docs/rphys_architecture_plan_v3.md`
- Planning notes: `docs/implementation/public-architecture-contracts/planning-notes.md`
- Review gate: Stage 2 architecture refactor-risk review
- Status: passed with accepted risks

## Review Summary

No blocking architecture refactor-risk findings remain for Stage 3.

The master plan intentionally locks only package homes, dependency direction, API-label policy, error-family naming, uv/tooling conventions, temporary rights status, and validation gates. It avoids locking concrete runtime signatures, data model internals, IO reference fields, dataset adapter protocols, transform class APIs, learning APIs, and evaluation behavior. This is the correct level of commitment for the first public architecture contract.

## Findings

| Severity | Area | Finding | Decision | Revisit trigger |
| --- | --- | --- | --- | --- |
| Accepted risk | First-wave module homes | `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms` are stable import homes before concrete behavior exists. | Accept. Module homes are needed to unblock later design work, and the plan forbids stable placeholder domain classes. | Revisit only if later package planning proves a first-wave concept cannot live in its assigned owner without circular dependencies. |
| Accepted risk | `rphys.io` ownership | `FieldRef`, `TemporalIndexSlice`, and `FieldView` ownership under `rphys.io` differs from the broader v3 public API list that initially mentioned them under `rphys.data`. | Accept. Stage 1 explicitly confirmed IO ownership for lazy external field access, which better preserves the data/IO boundary. | Revisit during Dataset IO and index core only if runtime data containers need non-IO field-reference abstractions. |
| Accepted risk | Future module deferral | `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, and `testing` are not created yet. | Accept. Creating empty homes early would harden future API prematurely. | Revisit in the owning roadmap package when behavior and signatures are ready. |
| Accepted risk | Optional dependency categories | Extras are category-level (`video`, `signal`, `torch`, `training`, `analysis`) rather than exact packages. | Accept. Exact dependencies should follow concrete backend behavior. | Revisit when implementing actual codecs, dataset adapters, torch-backed training, or analysis reports. |
| Accepted risk | Registry policy | Registries are limited to symbolic-name cases, while `_target_` import paths remain the main extension mechanism. | Accept. This avoids a mandatory global registry that would constrain external research code. | Revisit only if a future standard component truly needs symbolic lookup for config stability. |
| Accepted risk | Cross-repo `loom` enforcement | The plan documents `loom` must not depend on `rphys`, but cannot enforce this across both repos yet. | Accept. Current package is structural and can enforce only local non-duplication. | Revisit when `loom` and `rphys` CI/workspaces can run cross-repo import-boundary checks. |

## Boundary Checks

- Module ownership remains aligned with the v3 separation of concerns:
  - `rphys.data`: runtime field/data containers and contracts.
  - `rphys.io`: lazy external field access, views, slices, codecs, and IO backends.
  - `rphys.datasets`: dataset/record references, schemas, filtering, splitting, and indexing.
  - `rphys.transforms`: runtime sample transforms, checks, augmentation, extraction, export, and materialization support.
- The plan avoids forcing dataset formatting into `rphys.datasets`; formatting remains materialization/export.
- The plan avoids putting generic config, recipe expansion, DAG execution, run stores, artifact stores, executors, resume logic, locking, and `_target_` instantiation in `rphys`; those remain `loom` responsibilities.
- The plan does not create stable `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, `SampleTransform`, method, training, loss, metric, or evaluation placeholders.
- The plan keeps all v3 deferred decisions possible: collate policies, codec/export lists, mesh support, nested/multi-view samples, spatial/time slices, multi-member index items, entry-point plugins, self-supervised learners, signal-processing methods, materialization exporters, and reports.

## Gate Decision

- Blocking findings: none.
- Ready for master-plan confirmation review: yes.
- Required follow-up: later package master plans must perform their own API-level refactor-risk reviews before concrete signatures are marked stable.
