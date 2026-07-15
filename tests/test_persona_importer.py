"""Tests for PersonaImporter boundary behavior."""

from backend.core import PersonaImporter
from backend.models import PersonaImportResult, PersonaSource


def test_importer_accepts_persona_source() -> None:
    importer = PersonaImporter()
    source = PersonaSource(
        id="source-1",
        name="Reflective Analyst Notes",
        source_type="user notes",
        content="",
    )

    result = importer.import_persona(source)

    assert result.source_id == "source-1"


def test_importer_returns_persona_import_result() -> None:
    importer = PersonaImporter()

    result = importer.import_persona(PersonaSource())

    assert isinstance(result, PersonaImportResult)


def test_importer_extracts_fields_from_source() -> None:
    importer = PersonaImporter()
    source = PersonaSource(
        id="source-1",
        name="Fallback Name",
        source_type="article",
        content=(
            "trait: reflective, analytical\n"
            "value: clarity\n"
            "thinking: compare evidence before deciding\n"
            "style: calm, structured"
        ),
        metadata={
            "persona_name": "Reflective Analyst",
            "traits": ["careful"],
            "values": "truthfulness",
            "confidence": "0.75",
        },
    )

    result = importer.import_persona(source)

    assert result.source_id == "source-1"
    assert result.persona_name == "Reflective Analyst"
    assert result.traits == ["careful", "reflective", "analytical"]
    assert result.values == ["truthfulness", "clarity"]
    assert result.thinking_patterns == [
        "compare evidence before deciding"
    ]
    assert result.communication_style == ["calm", "structured"]
    assert result.confidence == 0.75


def test_importer_empty_source_does_not_crash() -> None:
    importer = PersonaImporter()

    result = importer.import_persona(PersonaSource())

    assert result == PersonaImportResult()
