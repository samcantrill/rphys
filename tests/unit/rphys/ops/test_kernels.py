from __future__ import annotations

from rphys.ops import FunctionalKernel, OperationContext


def add_value(value: int, *, context: OperationContext) -> int:
    return value + context.metadata.get("offset", 0)


class MultiplyKernel:
    def __init__(self, factor: int) -> None:
        self.factor = factor

    def __call__(self, value: int, context: OperationContext) -> int:
        return value * self.factor


def test_functional_kernel_type_alias_accepts_plain_callables() -> None:
    kernel: FunctionalKernel = add_value

    assert kernel(3, context=OperationContext(metadata={"offset": 2})) == 5


def test_callable_object_remains_a_functional_kernel() -> None:
    kernel: FunctionalKernel = MultiplyKernel(3)

    assert kernel(2, context=OperationContext()) == 6
