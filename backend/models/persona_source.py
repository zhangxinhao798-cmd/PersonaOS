"""External persona source boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class PersonaSource:
    """External persona information source data boundary."""

    id: str = ""
    name: str = ""
    source_type: str = ""
    content: str = ""
    metadata: dict = field(default_factory=dict)
