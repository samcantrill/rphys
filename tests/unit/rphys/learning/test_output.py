from __future__ import annotations

import pytest

from rphys.errors import RemotePhysLearningError
from rphys.learning import BackwardableScalar, require_backwardable_scalar


class FakeScalar:
    def __init__(self) -> None:
        self.backward_calls = 0

    def backward(self) -> None:
        self.backward_calls += 1


def test_backwardable_scalar_accepts_minimal_backward_surface() -> None:
    scalar = FakeScalar()

    returned = require_backwardable_scalar(scalar)
    returned.backward()

    assert isinstance(scalar, BackwardableScalar)
    assert scalar.backward_calls == 1


def test_backwardable_scalar_rejects_plain_values() -> None:
    with pytest.raises(RemotePhysLearningError) as exc_info:
        require_backwardable_scalar(1.0)

    assert exc_info.value.context["expected"] == "object with backward()"
    assert exc_info.value.context["actual"] == "float"
