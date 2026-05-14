"""Public entrypoint for Stage 6 operation bindings.

Importing from :mod:`rphys.ops` is the package boundary for Stage 6 runtime
operations.

    from rphys.ops import (
        Operation,
        OperationContract,
        OperationContext,
        OperationResult,
        OperationPipeline,
        FunctionalKernel,
    )

Plain callables remain plain callables: define a runtime kernel and call it
directly when no declaration/context/result envelope is needed.

    def add_one(value: int, *, context: OperationContext) -> int:
        return value + 1

    add_one(3, context=OperationContext())

Wrap a kernel with :class:`Operation` when you need explicit boundary declarations,
context checks, and inspectable execution output:

    op = Operation(
        add_one,
        contract=OperationContract(input_type=int, output_type=int),
    )
    result = op(3, context=OperationContext(metadata={"phase": "test"}))
    sample = result.output

`Operation` always returns :class:`OperationResult`; users must read payloads through
the ``.output`` attribute.

Operations do not define pipeline names, stable step APIs, export/save/cache
bindings, workflow provenance, or Stage 7/8/9 specialized operation families.
Those concerns are explicitly deferred to later stages.
"""

from .contracts import (
    OperationContract,
    OperationMutationPolicy,
    OperationRole,
)
from .core import Operation
from .context import OperationContext, OperationResult
from .pipelines import OperationPipeline
from .kernels import FunctionalKernel

__all__ = [
    "OperationRole",
    "OperationMutationPolicy",
    "OperationContract",
    "Operation",
    "OperationContext",
    "OperationResult",
    "OperationPipeline",
    "FunctionalKernel",
]
