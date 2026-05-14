"""Package home for dependency-light lazy IO descriptors.

Codec contract records live in ``rphys.io.codecs``. This package does not
provide real codecs, builders, registries, datasource scanning, or runtime
payload hooks.
"""

from .fields import FieldRef, FieldView
from .indexes import FieldIndex, TemporalIndexSlice
from .resources import ResourceRef

__all__ = [
    "ResourceRef",
    "FieldRef",
    "FieldIndex",
    "TemporalIndexSlice",
    "FieldView",
]
