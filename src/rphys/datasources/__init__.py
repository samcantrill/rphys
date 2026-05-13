"""Package home for dependency-light datasource descriptors.

Stage 3 exports are added only when descriptor behavior is implemented. This
package does not provide scanning, filtering, builders, manifests, or runtime
payload hooks.
"""

from .refs import DataSourceRef, RecordRef
from .schemas import DataSourceSchema

__all__ = [
    "DataSourceRef",
    "RecordRef",
    "DataSourceSchema",
]
