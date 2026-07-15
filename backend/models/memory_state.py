"""Memory lifecycle state model for PersonaOS."""

from enum import Enum


class MemoryState(Enum):
    """Lifecycle states for persistent PersonaOS memories."""

    NEW = "new"
    """A newly created memory that has not yet been fully lifecycle-managed."""

    ACTIVE = "active"
    """A memory available for normal retrieval and context use."""

    CONSOLIDATED = "consolidated"
    """A memory synthesized from related memories or promoted into durable form."""

    WEAKENED = "weakened"
    """A memory retained with reduced influence due to lower relevance or confidence."""

    FORGOTTEN = "forgotten"
    """A memory removed from normal retrieval or excluded from active context."""
