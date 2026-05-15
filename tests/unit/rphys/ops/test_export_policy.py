from __future__ import annotations

import pytest

from rphys.errors import RemotePhysOperationError
from rphys.ops.export import (
    ExportMaterialization,
    ExportPolicy,
    FieldExportOutcome,
    IdempotencyPolicy,
)


def test_export_policy_defaults_to_fail_on_existing_write() -> None:
    policy = ExportPolicy()

    assert policy.idempotency == IdempotencyPolicy.FAIL_ON_EXISTING
    assert policy.materialization == ExportMaterialization.WRITE
    assert policy.allow_link_copy_fallback is False
    assert policy.continue_on_field_error is False
    assert policy.new_target_outcome() == FieldExportOutcome.WRITTEN
    with pytest.raises(RemotePhysOperationError):
        policy.existing_target_outcome()


@pytest.mark.parametrize(
    ("policy", "expected"),
    [
        (
            ExportPolicy(idempotency=IdempotencyPolicy.SKIP_EXISTING),
            FieldExportOutcome.SKIPPED,
        ),
        (
            ExportPolicy(idempotency=IdempotencyPolicy.REPLACE_EXISTING),
            FieldExportOutcome.REPLACED,
        ),
    ],
)
def test_existing_target_policy_outcomes_are_explicit(
    policy: ExportPolicy,
    expected: FieldExportOutcome,
) -> None:
    assert policy.existing_target_outcome() == expected


@pytest.mark.parametrize(
    ("materialization", "expected"),
    [
        (ExportMaterialization.WRITE, FieldExportOutcome.WRITTEN),
        (ExportMaterialization.LINK, FieldExportOutcome.LINKED),
        (ExportMaterialization.COPY, FieldExportOutcome.COPIED),
    ],
)
def test_new_target_materialization_outcomes_are_explicit(
    materialization: ExportMaterialization,
    expected: FieldExportOutcome,
) -> None:
    assert ExportPolicy(materialization=materialization).new_target_outcome() == expected


def test_export_policy_rejects_unsupported_or_implicit_modes() -> None:
    with pytest.raises(RemotePhysOperationError):
        ExportPolicy(idempotency="overwrite")
    with pytest.raises(RemotePhysOperationError):
        ExportPolicy(materialization="symlink_or_copy")
    with pytest.raises(RemotePhysOperationError):
        ExportPolicy(allow_link_copy_fallback="yes")  # type: ignore[arg-type]
