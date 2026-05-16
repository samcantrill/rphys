# Stage 12 Learning And Training Examples

Stage 12 separates scientific learner semantics from loop mechanics.
`Learner.step(batch, context)` returns a `StepOutput`; `TrainingEngine`
implementations own iteration, device movement, backward, optimizer and
scheduler calls, events, and primitive result summaries. `Trainer` is the
RemotePhys facade over the selected engine.

## Native Supervised Smoke Run

The native path consumes already-built `Batch` iterables. It does not scan a
datasource, build a dataloader, write checkpoints, export predictions, or parse
project configuration.

```python
from rphys.training import Trainer, TrainingPlan

plan = TrainingPlan(
    train_batches=(train_batch,),
    validation_batches=(valid_batch,),
    test_batches=(test_batch,),
    predict_batches=(predict_batch,),
    optimizer=optimizer,
)

trainer = Trainer()
fit_result = trainer.fit(plan, supervised_learner)
predict_result = trainer.predict(plan, supervised_learner)
```

`Trainer()` defaults to `NativeTrainingEngine`. Train mode uses only
`StepOutput.objective` for backward. Validate, test, and predict modes do not
call backward, optimizer, or scheduler hooks. `SupervisedLearner` returns raw
`MethodOutput` predictions by default and applies prediction fields only to a
local working batch when losses, objectives, or metrics need those fields.

## Fake External Engine Pressure

Stage 12 supports delegation to an explicit engine object that implements
`fit/validate/test/predict(plan, learner)`. The test suite includes a fake
external engine to pressure-test this boundary without importing Lightning,
JAX, torch, loggers, or framework-private state.

```python
from rphys.training import Trainer, TrainingPlan

trainer = Trainer(engine=fake_external_engine)
result = trainer.fit(TrainingPlan(train_batches=(train_batch,)), learner)
```

External engines should normalize only primitive evidence into
`TrainingResult`: metric names and values, event/callback statuses, profile
statuses, unavailable probes, and checkpoint identifiers that are already
available. They should not parse checkpoint files, logger internals,
callback-private state, or framework-private objects.

## Experimental Function Entrypoint

`run_train` is a thin experimental function for downstream wrappers that prefer
function-style delegation.

```python
from rphys.training import TrainingPlan, run_train

result = run_train(TrainingPlan(train_batches=(train_batch,)), learner)
```

It delegates to `Trainer.fit`. It does not define a workflow runtime, stable
project configuration schema, artifact store, checkpoint writer, or dataloader
builder.

## Future Compatibility Notes

Future RemotePhys stages may run `BatchOperationPipeline` objects over model
outputs, materialize prediction rows or samples, and support real Lightning or
JAX adapters. Stage 12 intentionally does not provide learner-level
post-prediction pipeline arguments, mode-specific prediction pipeline specs,
`TrainingPlan` pipeline fields, trainer-owned prediction routing, sample
uncollation adapters, prediction export/materialization, or real external
framework integrations.
