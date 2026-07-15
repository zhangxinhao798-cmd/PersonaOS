from backend.core.knowledge import KnowledgeEngine, KnowledgeRecord


def make_record(
    content: str,
    category: str = "architecture",
    source: str = "project-notes",
    confidence: float = 0.8,
    timestamp: str = "2026-07-15",
) -> KnowledgeRecord:
    return KnowledgeRecord(
        content=content,
        category=category,
        source=source,
        confidence=confidence,
        timestamp=timestamp,
    )


def test_create_knowledge_stores_and_returns_record():
    engine = KnowledgeEngine()
    record = make_record("PersonaOS separates knowledge from memory.")

    created = engine.create_knowledge(record)

    assert created is record
    assert engine.get_knowledge() == [record]


def test_retrieve_knowledge_returns_relevant_records():
    engine = KnowledgeEngine()
    relevant = make_record(
        "PersonaOS uses modular engines for digital mind architecture.",
        category="architecture",
    )
    unrelated = make_record(
        "The project journal records daily development progress.",
        category="process",
    )
    engine.create_knowledge(relevant)
    engine.create_knowledge(unrelated)

    results = engine.retrieve_knowledge("modular architecture")

    assert relevant in results
    assert unrelated not in results


def test_update_knowledge_updates_provided_fields():
    engine = KnowledgeEngine()
    record = make_record(
        "Knowledge records preserve source metadata.",
        source="draft",
        confidence=0.4,
    )
    engine.create_knowledge(record)

    updated = engine.update_knowledge(
        record,
        confidence=0.9,
        source="architecture-spec",
    )

    assert updated is record
    assert record.confidence == 0.9
    assert record.source == "architecture-spec"


def test_retrieve_knowledge_ignores_unrelated_records():
    engine = KnowledgeEngine()
    unrelated = make_record(
        "Skill descriptors define governed capabilities.",
        category="skills",
    )
    engine.create_knowledge(unrelated)

    results = engine.retrieve_knowledge("confidence calibration")

    assert results == []
