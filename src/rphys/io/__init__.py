"""Package home for dependency-light lazy IO descriptors.

Stage 3 exports are added only when descriptor behavior is implemented. This
package does not provide codecs, builders, registries, or runtime payload hooks.
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
