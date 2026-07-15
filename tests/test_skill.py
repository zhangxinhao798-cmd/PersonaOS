from backend.core.skill import SkillEngine, SkillRecord


def make_skill(
    name: str = "memory_search",
    description: str = "Retrieve relevant memories.",
    category: str = "memory",
    confidence: float = 0.8,
    metadata: dict | None = None,
) -> SkillRecord:
    return SkillRecord(
        name=name,
        description=description,
        category=category,
        confidence=confidence,
        metadata=metadata or {"permission": "read"},
    )


def test_create_skill_stores_and_returns_skill():
    engine = SkillEngine()
    skill = make_skill()

    created = engine.create_skill(skill)

    assert created is skill
    assert engine.get_skills() == [skill]


def test_get_skills_returns_stored_skills():
    engine = SkillEngine()
    memory_skill = make_skill(name="memory_search")
    knowledge_skill = make_skill(
        name="knowledge_lookup",
        description="Retrieve source-backed knowledge.",
        category="knowledge",
    )

    engine.create_skill(memory_skill)
    engine.create_skill(knowledge_skill)

    assert engine.get_skills() == [memory_skill, knowledge_skill]


def test_update_skill_updates_provided_fields():
    engine = SkillEngine()
    skill = make_skill()
    engine.create_skill(skill)

    updated = engine.update_skill(
        skill,
        name="memory_ranker",
        description="Rank relevant memories.",
        category="memory",
        confidence=0.95,
        metadata={"permission": "read", "version": "v1"},
    )

    assert updated is skill
    assert skill.name == "memory_ranker"
    assert skill.description == "Rank relevant memories."
    assert skill.category == "memory"
    assert skill.confidence == 0.95
    assert skill.metadata == {"permission": "read", "version": "v1"}


def test_remove_skill_removes_and_returns_skill():
    engine = SkillEngine()
    skill = make_skill()
    engine.create_skill(skill)

    removed = engine.remove_skill(skill)

    assert removed is skill
    assert engine.get_skills() == []
