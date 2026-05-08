"""Field-level collation policy declarations.

Phase 1 intentionally exposes only the policy enum. The execution context and
``collate_samples`` implementation land later with ``Sample`` and ``Batch``.
"""

from __future__ import annotations

from enum import Enum

__all__ = ["CollatePolicy"]


class CollatePolicy(Enum):
    """Supported field-level collation policies.

    API stability: Stable for the exposed ``LIST`` member.

    ``LIST`` means a later collation step may preserve per-sample payloads as a
    Python list without stacking, padding, truncation, missing-field handling, or
    backend-specific tensor behavior. No default policy is implied by this enum:
    fields still need an explicit policy before collation is allowed.

    Equality, hashing, copying, and serialization:
        Enum member identity, equality, hashing, copy/deep-copy behavior, and
        the ``name``/``value`` tokens are public for ``LIST``. Future or reserved
        policy names are unsupported until implemented and tested.
    """

    LIST = "list"
