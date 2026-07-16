"""Tests for Memory Runtime Integration v1."""

import copy

from backend.engine.prompt_builder import PromptBuilder
from backend.engine.prompt_renderer import PromptRenderer
from backend.engine.runtime_context_assembler import RuntimeContextAssembler
from backend.models import LLMResponse
from backend.models.context import (
    MemoryContext,
    PersonaContext,
    PersonaOSContext,
)
from backend.models.memory_record import MemoryRecord
from backend.runtime import RuntimeMemoryRetriever, RuntimeSession

from tests.test_runtime_session import FakeChatRuntime, make_entry


def make_memory(
    content: str,
    category: str = "preference",
    confidence: float = 0.8,
    importance: float = 0.8,
) -> MemoryRecord:
    return MemoryRecord(
        content=content,
        category=category,
        confidence=confidence,
        importance=importance,
        source="test-memory",
        timestamp="2026-07-16T00:00:00Z",
    )


def make_context(memories: list[MemoryRecord]) -> PersonaOSContext:
    return PersonaOSContext(
        query="runtime memory test",
        persona=PersonaContext(
            name="Memory Runtime Architect",
            traits=["careful"],
            values=["boundaries"],
            style="precise",
        ),
        memories=MemoryContext(memories=memories),
    )


def test_runtime_memory_retriever_returns_relevant_memories() -> None:
    relevant = make_memory("User prefers Porsche sports cars.")
    unrelated = make_memory("User likes tea in the morning.", "lifestyle")
    context = make_context([unrelated, relevant])

    result = RuntimeMemoryRetriever().retrieve_relevant_memories(
        "porsche car preference",
        context,
    )

    assert result.memories == [relevant]
    assert result.relevance[0]["rank"] == 1
    assert result.relevance[0]["score"] > 0
    assert result.relevance[0]["source"] == "test-memory"


def test_runtime_memory_retriever_handles_no_memory() -> None:
    context = make_context([])

    result = RuntimeMemoryRetriever().retrieve_relevant_memories(
        "anything",
        context,
    )

    assert result.memories == []
    assert result.relevance == []


def test_runtime_memory_retriever_combines_multiple_memories() -> None:
    first = make_memory("User prefers long-term investment analysis.", "finance")
    second = make_memory("User asks about investment risk controls.", "finance")
    third = make_memory("User enjoys cooking pasta.", "lifestyle")
    context = make_context([first, second, third])

    result = RuntimeMemoryRetriever(limit=3).retrieve_relevant_memories(
        "investment risk",
        context,
    )

    assert result.memories == [second, first]
    assert [item["rank"] for item in result.relevance] == [1, 2]


def test_runtime_session_passes_retrieved_memory_into_runtime_context() -> None:
    relevant = make_memory("User prefers Porsche sports cars.")
    unrelated = make_memory("User enjoys quiet mornings.", "lifestyle")
    context = make_context([relevant, unrelated])
    runtime = FakeChatRuntime(
        responses=[LLMResponse(content="memory-aware reply", provider="fake")]
    )
    session = RuntimeSession(
        id="memory-session",
        persona_entry=make_entry(),
        persona_os_context=context,
        chat_runtime=runtime,
        memory_retriever=RuntimeMemoryRetriever(),
    )

    session.send("Tell me about my Porsche preference.")

    runtime_context = runtime.calls[0]["persona_os_context"]
    assert runtime_context.memories.memories == [relevant]
    assert runtime_context.memories.relevance[0]["rank"] == 1
    assert runtime_context.metadata["memory_retrieval"] == {
        "enabled": True,
        "retrieved_count": 1,
        "source": "RuntimeMemoryRetriever",
    }


def test_runtime_memory_read_path_does_not_mutate_source_records() -> None:
    memory = make_memory("User prefers Porsche sports cars.")
    context = make_context([memory])
    before_memory = copy.deepcopy(memory.__dict__)
    before_context_memories = list(context.memories.memories)
    runtime = FakeChatRuntime()
    session = RuntimeSession(
        id="memory-session",
        persona_entry=make_entry(),
        persona_os_context=context,
        chat_runtime=runtime,
        memory_retriever=RuntimeMemoryRetriever(),
    )

    session.send("Porsche")

    assert memory.__dict__ == before_memory
    assert context.memories.memories == before_context_memories


def test_runtime_context_contains_independent_memory_section() -> None:
    memory = make_memory("User prefers Porsche sports cars.")
    context = make_context([memory])
    context.memories.relevance = [
        {
            "rank": 1,
            "score": 2.4,
            "source": "test-memory",
            "category": "preference",
        }
    ]

    runtime_context = RuntimeContextAssembler().assemble(context)

    assert runtime_context.active_persona.name == "Memory Runtime Architect"
    assert runtime_context.memories == [
        {
            "content": "User prefers Porsche sports cars.",
            "category": "preference",
            "source": "test-memory",
            "confidence": 0.8,
            "importance": 0.8,
            "timestamp": "2026-07-16T00:00:00Z",
            "relevance": {
                "rank": 1,
                "score": 2.4,
                "source": "test-memory",
                "category": "preference",
            },
        }
    ]


def test_prompt_contains_memory_section_without_polluting_persona() -> None:
    memory = make_memory("User prefers Porsche sports cars.")
    context = make_context([memory])
    context.memories.relevance = [
        {
            "rank": 1,
            "score": 2.4,
            "source": "test-memory",
            "category": "preference",
        }
    ]
    runtime_context = RuntimeContextAssembler().assemble(context)

    prompt_package = PromptBuilder().build(runtime_context, "What do I like?")
    rendered = PromptRenderer().render(prompt_package)

    assert "## Memory" in rendered.text
    assert "User prefers Porsche sports cars." in rendered.text
    assert "## Persona" in rendered.text
    assert "Memory Runtime Architect" in rendered.text
    assert "User prefers Porsche sports cars." not in str(prompt_package.persona)
    assert prompt_package.memory is runtime_context.memories
