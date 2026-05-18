"""Compatibility-free returned-Batch output helpers for methods.

``Method.predict`` now returns ``Batch`` directly. Generic returned-batch
validation lives in ``rphys.data.output`` and is re-exported here only as a
module-level convenience for method adapters.
"""

from __future__ import annotations

from rphys.data.output import BatchOutputFieldSpec, BatchOutputSpec, project_batch_fields

__all__ = ["BatchOutputFieldSpec", "BatchOutputSpec", "project_batch_fields"]
