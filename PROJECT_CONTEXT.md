# PersonaOS Project Context

## 1. Project Overview

PersonaOS is an operating system for digital minds.

It is not a chatbot framework, a prompt wrapper, or a single model interface. The project is designed as a long-term architecture for persistent, adaptive, memory-bearing software entities that can develop coherent identities, reason over knowledge, use modular capabilities, express calibrated confidence, and evolve in controlled ways over time.

The long-term vision is to build infrastructure around language models rather than treating the model as the whole system. PersonaOS aims to provide the operating layer that manages identity, memory, knowledge, skills, context, confidence, and evolution so a digital mind can remain understandable, inspectable, and extensible.

This project exists because most AI systems are organized around isolated conversations. They respond to the current prompt, but the continuity, identity, and long-term state of the system are usually implicit or temporary. PersonaOS explores a different foundation: a digital mind should have explicit architecture for what it remembers, what it knows, which persona is active, which skills it can use, how confident it should be, and how it may change.

A normal chatbot is primarily a conversation interface. PersonaOS treats conversation as only one interface into a larger system. The project is about building the backend and conceptual architecture for digital minds that can persist across interactions, carry meaningful memory forward, use tools responsibly, and grow without losing their structure.

## 2. Core Philosophy

PersonaOS treats personality as a structured system.

Persona is not intended to be a loose prompt fragment. It is an architectural layer that defines identity, behavioral frame, preferences, boundaries, and continuity. The Persona Engine should eventually coordinate the active identity of a digital mind while keeping memory, knowledge, skills, confidence, and evolution separate.

Memory is meaningful experience, not raw chat history. A memory should represent selected, durable, experience-derived context that may matter beyond the moment it was created. Conversation history is the record of what was said; memory is the structured interpretation of what should persist.

Skills are modular abilities. They are capabilities, not personalities. A skill may represent a tool, workflow, procedure, integration, or action boundary. Different personas may eventually use different skill sets, but access to a skill should not redefine who a persona is.

Evolution is controlled improvement. PersonaOS should support growth, but not uncontrolled drift. Long-term changes to identity, preferences, behavior, skill usage, confidence rules, or operating patterns should be explicit, traceable, versioned, and reversible where possible.

Confidence is reliability awareness. PersonaOS should help a digital mind distinguish what it knows, what it remembers, what it infers, what it can verify, and what remains uncertain. Confidence mechanisms should prevent fluent but unsupported overconfidence.

## 3. Current Architecture

The repository currently contains documentation, a Python backend skeleton, tests, and empty top-level project directories reserved for future use.

Current top-level structure includes:

- `backend/`
- `config/`
- `docs/`
- `frontend/`
- `knowledge/`
- `memory/`
- `personas/`
- `scripts/`
- `tests/`
- `pytest.ini`
- `AGENTS.md`
- `README.md`

The current backend structure is:

```text
backend/
    core/
        __init__.py
        persona.py
        memory.py
        knowledge.py
        skill.py
        confidence.py
        evolution.py
    engine/
        __init__.py
        persona_os.py
    models/
        __init__.py
        schemas.py
        memory_record.py
    main.py
```

`backend/core/` contains the core engine classes. These classes represent the major architectural components of PersonaOS. Most are currently placeholders with responsibility docstrings, while `MemoryEngine` has the first minimal implementation.

`backend/engine/` contains the top-level orchestration layer. `persona_os.py` defines the `PersonaOS` class, which composes the modular engines and acts as the initial backend assembly point.

`backend/models/` contains shared model definitions. `schemas.py` currently contains placeholder schema boundary classes. `memory_record.py` contains the first concrete lightweight model, `MemoryRecord`.

`backend/main.py` contains the backend entry point. It provides `create_app()` and prints a minimal startup log when run with `python -m backend.main`.

The current engines are:

- Persona Engine: Intended to coordinate identity, behavior, and the active operating frame.
- Memory Engine: Manages experience-derived continuity. Currently implemented as a simple in-memory list.
- Knowledge Engine: Intended to manage source-backed reference information.
- Skill Engine: Intended to manage governed capabilities available to a digital mind.
- Confidence Engine: Intended to evaluate reliability awareness, uncertainty, and risk.
- Evolution Engine: Intended to govern controlled long-term change.

The architecture documentation also describes a future Context Engine. No `ContextEngine` backend class exists yet.

## 4. Current Implementation Status

PersonaOS is currently an early architectural foundation.

Completed so far:

- Initial backend package structure under `backend/`.
- Core engine class files for Persona, Memory, Knowledge, Skill, Confidence, and Evolution.
- Top-level `PersonaOS` runtime class that creates and stores engine instances.
- Minimal backend startup entry point in `backend/main.py`.
- Startup output when running `python -m backend.main`:
  - `PersonaOS Booting...`
  - `Persona Engine: OK`
  - `Memory Engine: OK`
  - `Knowledge Engine: OK`
  - `Skill Engine: OK`
  - `Confidence Engine: OK`
  - `Evolution Engine: OK`
  - `PersonaOS Ready.`
- Lightweight `MemoryRecord` model in `backend/models/memory_record.py`.
- First simple `MemoryEngine` implementation in `backend/core/memory.py`.
- Basic pytest configuration in `pytest.ini` with `pythonpath = .`.
- Runtime initialization test in `tests/test_runtime.py`.
- Memory engine tests in `tests/test_memory.py`.

Current verification status:

- `tests/test_runtime.py` verifies that `create_app()` returns a `PersonaOS` instance with Persona, Memory, Knowledge, Skill, Confidence, and Evolution engines initialized.
- `tests/test_memory.py` verifies that `MemoryEngine.create_memory()` stores and returns a memory, and that `get_memories()` returns stored memories.
- Earlier work noted that `pytest` was not installed in one environment. The repository now has `pytest.ini`, and the tests are written in pytest style. Future agents should run the test suite in the active environment before and after changes.

Current implementation limits:

- Memory storage is in-memory only.
- There is no persistence layer yet.
- There is no retrieval ranking, filtering, update, consolidation, or forgetting logic yet.
- Persona, Knowledge, Skill, Confidence, and Evolution engines are placeholders.
- Context Engine is documented in architecture but not yet implemented in backend code.
- No frontend behavior is implemented.

## 5. Memory System Design

Memory in PersonaOS means experience-derived context that may be useful beyond the moment in which it was created.

Memory is not the same as conversation history. Conversation history is the raw record of what was said. Memory is a curated, structured representation of what should persist. A digital mind should not treat every message as permanent identity or permanent fact. Passing comments, temporary task instructions, confirmed preferences, and long-term user context require different treatment.

The intended memory lifecycle is:

- Create: Turn significant interactions, events, observations, or system decisions into memory candidates.
- Retrieve: Select memories relevant to the current context.
- Update: Revise memories when new evidence changes their accuracy, confidence, importance, or usefulness.
- Consolidate: Combine related memories into clearer long-term representations.
- Forget: Remove, expire, suppress, or archive memories that are outdated, superseded, low-value, sensitive, or no longer permitted.

Possible memory categories include:

- Working memory: Short-term context for the current task, session, or reasoning window.
- Episodic memory: Records of meaningful events and interactions.
- Semantic memory: Generalized understanding derived from experience, such as stable preferences or recurring patterns.
- Procedural memory: Optional learned routines, workflows, methods, or behavior patterns.

The current concrete `MemoryRecord` model contains:

- `content`: The remembered content.
- `category`: The memory category, such as working, episodic, semantic, or procedural.
- `confidence`: A reliability signal for the memory.
- `importance`: A signal for how much the memory should matter if relevant.
- `source`: Where the memory came from.
- `timestamp`: When the memory was created or recorded.

Importance and confidence are intentionally separate. A memory can be important but uncertain, or reliable but minor.

## 6. Persona System

The Persona system is intended to make identity explicit.

Future goals include supporting multiple personalities or personas within a shared PersonaOS environment. Each persona should be able to have its own identity, preferences, behavioral rules, boundaries, memory scope, knowledge access, and skill permissions.

Persona configuration will likely become a first-class part of the backend. A persona should not be defined only by a prompt string. It should have structured state that can be inspected, versioned, and used to assemble the active operating context.

Different personas may eventually load different skills. For example, one persona may be configured for software engineering workflows while another may be configured for writing, research, or operations. Skill access should remain governed and separate from identity.

Personality consistency is a central goal. PersonaOS should preserve stable identity over time while allowing controlled refinement. The Evolution Engine should help prevent personality drift by ensuring that durable persona changes are explicit, justified, and traceable.

## 7. Skill System

Skills are modular capabilities.

The Skill Engine is intended to manage what a digital mind can do, not who it is. Skills may represent tools, workflows, external integrations, local actions, domain routines, or multi-step procedures.

Future skill direction includes:

- Skill discovery.
- Skill registration with metadata.
- Skill loading based on persona, project, or environment.
- Permission-aware execution.
- Skill evaluation and reliability tracking.
- Skill composition for multi-step workflows.
- Possible integration with external skill ecosystems or marketplaces.

Different personas should eventually be able to load different skill sets. Skill access may depend on persona role, user permission, project context, environment, risk level, or governance policy.

Skill discovery and management should remain modular. The system should be able to add or remove capabilities without rewriting persona, memory, or knowledge architecture.

## 8. Knowledge System

Knowledge in PersonaOS means durable, referenceable information from sources outside personal experience.

Possible knowledge sources include:

- Project documentation.
- Source code and repository metadata.
- User-provided files.
- Structured databases.
- APIs and external services.
- Manuals, specifications, standards, and research notes.
- Curated knowledge bases.

The Knowledge Engine is intended to ingest, index, retrieve, update, and remove source-backed information. Knowledge retrieval should preserve source metadata, freshness, authority, and access constraints.

Knowledge is different from memory. Knowledge preserves reference material. Memory preserves experience. A style guide document belongs to knowledge; a user's repeated preference for a certain summary style belongs to memory.

The Knowledge Engine should work closely with the Confidence Engine. Source reliability, freshness, evidence strength, and conflicting references should affect how strongly retrieved knowledge influences system behavior.

## 9. Confidence System

AI systems need confidence awareness because fluent generation can sound certain even when support is weak.

The Confidence Engine is intended to help PersonaOS evaluate reliability. It should distinguish between verified knowledge, remembered experience, inferred assumptions, weak evidence, missing context, and uncertainty.

Future confidence work should include:

- Evidence evaluation.
- Source reliability assessment.
- Memory confidence assessment.
- Uncertainty detection.
- Conflict detection.
- Risk analysis.
- Calibration of claims and actions.
- Guidance on when to ask for clarification, retrieve more context, cite sources, qualify an answer, or avoid action.

Confidence is not just a probability score. It is broader reliability awareness. It should help prevent overconfidence by ensuring that the system's behavior reflects the strength and risk of its available evidence.

## 10. Evolution System

Evolution in PersonaOS means controlled long-term improvement.

The Evolution Engine is intended to govern durable changes to persona, behavior, preferences, operating rules, skill usage, confidence policies, and other long-term patterns. Evolution should not happen automatically just because an interaction occurred.

Future evolution mechanisms should include:

- Detecting possible change signals.
- Creating explicit proposals.
- Evaluating evidence, risk, identity impact, and reversibility.
- Requiring approval before permanent changes when appropriate.
- Applying approved changes through the correct owning engine.
- Versioning changes.
- Supporting rollback or supersession.

Evolution is especially important for preventing uncontrolled personality changes. Temporary instructions, low-confidence inferences, isolated interactions, or repeated local context should not silently redefine identity. A digital mind may grow, but it should remain coherent and traceable.

## 11. Development Roadmap

### Phase 1: Foundation

- Maintain backend architecture.
- Keep tests passing.
- Expand core models carefully.
- Preserve modular engine boundaries.
- Keep documentation aligned with code.

Current status: partially complete. The backend skeleton, runtime initialization, `MemoryRecord`, basic `MemoryEngine`, and initial tests exist.

### Phase 2: Memory System

- Add persistent storage for memories.
- Add memory retrieval beyond returning all records.
- Add memory ranking by relevance, importance, confidence, category, and recency.
- Add update, consolidation, and forgetting behavior.
- Add tests for persistence and retrieval behavior.

### Phase 3: Persona System

- Define persona configuration structures.
- Add persona profiles.
- Support multiple personas.
- Connect personas to memory scopes, skill permissions, and operating constraints.
- Add tests for persona initialization and selection.

### Phase 4: Skill System

- Define skill descriptors.
- Add skill loading and registration.
- Add permission and governance metadata.
- Explore a skill marketplace or registry concept.
- Connect skills with personas and context.

### Phase 5: Knowledge And Reasoning

- Define knowledge record models.
- Add knowledge source ingestion.
- Add retrieval and source metadata.
- Connect knowledge retrieval with confidence assessment.
- Preserve the boundary between memory and knowledge.

### Phase 6: Evolution And Self-Improvement

- Define evolution proposals.
- Add versioning and traceability.
- Add approval workflows for durable changes.
- Add rollback support.
- Add drift detection and confidence-aware evolution thresholds.

## 12. Development Guidelines For Future AI

Understand the architecture before modifying code. Read `docs/architecture.md` and the relevant engine document before implementing behavior in that area.

Prefer small incremental changes. PersonaOS is intended to grow carefully. Avoid broad rewrites unless the user explicitly asks for them and the architecture justifies it.

Keep documentation updated. When implementation changes the architecture or behavior, update the relevant docs in a separate, explicit step unless the user has asked not to modify documentation.

Do not rewrite existing systems unnecessarily. Preserve current names, folders, and modular boundaries. Build on the existing `backend/core`, `backend/engine`, and `backend/models` structure.

Run tests after changes. The current test setup uses pytest style tests under `tests/`, with `pytest.ini` setting `pythonpath = .`.

Preserve project philosophy. PersonaOS is not a chatbot framework. Keep identity, memory, knowledge, skills, confidence, and evolution distinct. Avoid designs that collapse everything into prompts, a monolithic class, or hidden state.

Treat destructive actions as permission-only. Do not delete files, rename folders, or overwrite user work without explicit permission.

Prioritize the Python backend first. Frontend work is intentionally deferred unless explicitly requested.

## 13. Current Next Steps

Recommended immediate tasks:

- Improve `MemoryEngine` while keeping it simple and tested.
- Add persistent memory storage.
- Add memory retrieval by category, importance, confidence, source, and timestamp.
- Create persona configuration models.
- Connect personas with memory scopes and skill permissions.
- Begin defining the Skill Engine interface.
- Expand tests around runtime initialization, memory records, and memory engine behavior.

The project is currently in the foundation stage. The best next work is small, well-tested backend progress that turns the documented architecture into simple, inspectable runtime behavior.
