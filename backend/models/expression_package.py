"""Expression package boundary models for PersonaOS."""

from dataclasses import dataclass, field


@dataclass
class ExpressionPackageManifest:
    """Manifest metadata for a file-backed expression package."""

    package_id: str = ""
    name: str = ""
    version: str = ""
    description: str = ""
    persona_id: str = ""
    style_path: str = "style.json"
    examples_path: str = "examples.json"
    metadata: dict = field(default_factory=dict)


@dataclass
class ExpressionStyle:
    """Text expression style distilled from source material."""

    tone: str = ""
    rhythm: str = ""
    pacing: str = ""
    vocabulary: list[str] = field(default_factory=list)
    catchphrases: list[str] = field(default_factory=list)
    sentence_patterns: list[str] = field(default_factory=list)
    pause_patterns: list[str] = field(default_factory=list)
    emphasis_patterns: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)


@dataclass
class ExpressionPackage:
    """Loaded expression package data before runtime use."""

    manifest: ExpressionPackageManifest = field(
        default_factory=ExpressionPackageManifest
    )
    style: ExpressionStyle = field(default_factory=ExpressionStyle)
    examples: list[dict] = field(default_factory=list)
    package_path: str = ""


@dataclass
class ExpressionPackageValidationResult:
    """Validation result for an expression package directory."""

    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
