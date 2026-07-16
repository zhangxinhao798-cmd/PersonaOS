"""Final rendered prompt model for PersonaOS runtime boundaries."""

from dataclasses import dataclass, field


@dataclass
class FinalPrompt:
    """Rendered prompt artifact produced from a PromptPackage.

    This model is not a provider request. It stores deterministic rendered
    prompt text and carries metadata forward for later runtime boundaries.
    """

    text: str = ""
    metadata: dict = field(default_factory=dict)

