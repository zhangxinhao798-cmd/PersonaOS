from backend.core.evolution import EvolutionEngine, EvolutionRecord


def make_evolution(
    target: str = "persona",
    change: str = "Add clearer collaboration preference.",
    reason: str = "Repeated user preference for concise technical updates.",
    confidence: float = 0.8,
    timestamp: str = "2026-07-15",
) -> EvolutionRecord:
    return EvolutionRecord(
        target=target,
        change=change,
        reason=reason,
        confidence=confidence,
        timestamp=timestamp,
    )


def test_propose_evolution_stores_and_returns_record():
    engine = EvolutionEngine()
    evolution = make_evolution()

    proposed = engine.propose_evolution(evolution)

    assert proposed is evolution
    assert engine.get_evolutions() == [evolution]


def test_get_evolutions_returns_all_records():
    engine = EvolutionEngine()
    persona_evolution = make_evolution(target="persona")
    memory_evolution = make_evolution(
        target="memory",
        change="Increase importance for recurring project preferences.",
    )

    engine.propose_evolution(persona_evolution)
    engine.propose_evolution(memory_evolution)

    assert engine.get_evolutions() == [persona_evolution, memory_evolution]


def test_apply_evolution_returns_approved_record():
    engine = EvolutionEngine()
    evolution = make_evolution()
    engine.propose_evolution(evolution)

    applied = engine.apply_evolution(evolution)

    assert applied is evolution


def test_apply_evolution_keeps_evolution_history():
    engine = EvolutionEngine()
    evolution = make_evolution()
    engine.propose_evolution(evolution)

    engine.apply_evolution(evolution)

    assert engine.get_evolutions() == [evolution]
