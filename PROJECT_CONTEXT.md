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
        retrieval.py
        knowledge.py
        skill.py
        confidence.py
        evolution.py
    fusion/
        __init__.py
        persona_memory.py
    engine/
        __init__.py
        context_builder.py
        persona_os.py
    models/
        __init__.py
        context.py
        fusion.py
        schemas.py
        persona_profile.py
        memory_record.py
        memory_state.py
    main.py
```

`backend/core/` contains the core engine classes. These classes represent the major architectural components of PersonaOS. The Memory Layer v1 implementation includes `MemoryEngine` and `MemoryRetriever`. The Persona system foundation includes a profile-backed `PersonaEngine`. Persona-Memory integration now allows persona memory preferences to influence memory priority without merging the engines. Knowledge Engine v1 manages structured source-backed knowledge records with deterministic retrieval. Skill Engine v1 manages governed capability records. Evolution Engine v1 manages explicit controlled-change proposals without mutating other engines automatically.

`backend/fusion/` contains cross-engine interpretation layers that preserve engine ownership. `PersonaMemoryFusion` interprets raw memories from the active persona perspective without modifying PersonaEngine or MemoryEngine.

`backend/engine/` contains the top-level orchestration layer. `persona_os.py` defines the `PersonaOS` class, which composes the modular engines and now acts as the first orchestration entry point. `context_builder.py` defines `ContextBuilder`, which converts engine and fusion outputs into the shared context data model.

`backend/models/` contains shared model definitions. `context.py` contains the `PersonaOSContext` boundary models used by orchestration. `fusion.py` contains `FusionContext` for persona-aware memory interpretation output. `schemas.py` currently contains placeholder schema boundary classes. `memory_record.py` contains the concrete lightweight `MemoryRecord` model, `memory_state.py` defines the memory lifecycle states, and `persona_profile.py` defines persistent persona identity data.

`backend/main.py` contains the backend entry point. It provides `create_app()` and prints a minimal startup log when run with `python -m backend.main`.

The current engines are:

- Persona Engine: Coordinates identity traits through a profile-backed foundation and exposes memory preferences.
- Memory Engine: Manages experience-derived continuity. Memory Layer v1 is complete with in-memory creation, retrieval filtering, update, forgetting, lifecycle state support, keyword retrieval, and persona-aware priority calculation.
- Knowledge Engine: Manages structured source-backed reference information through Knowledge Engine v1.
- Skill Engine: Manages governed capability records through Skill Engine v1.
- Confidence Engine: Evaluates memory confidence with deterministic source, evidence, confirmation, and uncertainty signals.
- Evolution Engine: Manages explicit controlled-change proposals through Evolution Engine v1.

The orchestration layer currently includes:

- PersonaOS: Coordinates engine and fusion calls and returns an integrated operating context.
- PersonaMemoryFusion: Interprets retrieved memories from the active persona perspective without owning persona or memory storage.
- ContextBuilder: Converts engine and fusion outputs into `PersonaOSContext`.
- PersonaOSContext: Defines the shared communication format between engines and orchestration.

PersonaOS coordinates engines but does not own engine logic. Persona, memory, knowledge, skills, confidence, and evolution responsibilities remain inside their owning engines. Context data is only a structured communication boundary; it is not memory storage, knowledge storage, persona management, confidence calculation, persistence, or a frontend API.

The architecture documentation also describes a future Context Engine. No `ContextEngine` backend class exists yet.

The current Persona layer now supports structured import and version snapshots through explicit data and transformation boundaries:

```text
PersonaSource
    -> PersonaImporter
    -> PersonaImportResult
    -> PersonaProfileBuilder
    -> PersonaProfile
    -> PersonaVersion
    -> PersonaLibraryEntry
    -> PersonaReview
    -> PersonaActivation
    -> PersonaLibrary
```

This flow defines how external persona information can be represented, deterministically converted into import results, transformed into profile structure, captured as version snapshots, and prepared for library management. It does not yet imply persistence, runtime activation, LLM integration, or automatic persona modification.

The current Persona Library architecture now includes lifecycle, review, and activation boundaries. `PersonaLibraryEntry` is the lifecycle owner for persona library records. A library entry connects persona identity, lifecycle state, review status, activation history, the current version reference, the linked `PersonaProfile`, linked `PersonaVersion` records, and source references. `PersonaVersion` remains the immutable historical snapshot boundary.

Current Persona Library responsibility boundaries:

- `PersonaLibraryEntry` owns mutable library lifecycle state, review availability, activation records, current version reference, source references, and selectability checks.
- `PersonaVersion` preserves immutable persona profile snapshots and source tracking for historical traceability.
- `PersonaActivationManager` activates only approved personas with a valid current version reference and preserves activation history by marking activations inactive instead of deleting them.
- `PersonaSelector` performs runtime selection only after the library entry reports that it is approved, active, and backed by a valid version reference.

The current implemented Persona flow is:

```text
PersonaSource
    -> PersonaImporter
    -> PersonaImportResult
    -> PersonaProfileBuilder
    -> PersonaProfile
    -> PersonaVersion
    -> PersonaLibraryEntry
    -> PersonaReview
    -> PersonaActivation
    -> PersonaSelector
```

This flow remains local, deterministic, and model-provider independent. Persona data remains separate from runtime model calls and no LLM, Ollama, persistence, or frontend behavior has been introduced.

Future PersonaOS directions may include an Expression Layer responsible for how a digital mind communicates its identity. This may include voice characteristics, speech style, TTS integration, and multimodal interfaces. Expression should remain separate from Persona identity storage, Memory, Knowledge, Skills, Confidence, Evolution, and model providers.

## 4. Current Implementation Status

PersonaOS is currently an early architectural foundation with all six core engines complete at v1/foundation level: Persona Engine, Memory Engine, Confidence Engine, Knowledge Engine, Skill Engine, and Evolution Engine.

Completed so far:

- Initial backend package structure under `backend/`.
- Core engine class files for Persona, Memory, Knowledge, Skill, Confidence, and Evolution.
- Top-level `PersonaOS` runtime class that creates and stores engine instances.
- PersonaOS Orchestrator v1 through `PersonaOS.process_context()`.
- Context boundary models in `backend/models/context.py`.
- `ContextBuilder` in `backend/engine/context_builder.py`.
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
- `MemoryState` lifecycle enum in `backend/models/memory_state.py`.
- MemoryRecord lifecycle support through the `state` field.
- Memory Layer v1 implementation in `backend/core/memory.py`.
- `MemoryRetriever` v1 keyword retrieval engine in `backend/core/retrieval.py`.
- `PersonaProfile` model in `backend/models/persona_profile.py`.
- Profile-backed `PersonaEngine` implementation in `backend/core/persona.py`.
- PersonaEngine memory preference interface.
- MemoryEngine persona-aware priority calculation.
- Confidence Engine v1 implementation in `backend/core/confidence.py`.
- `ConfidenceEngine.calculate_confidence()`.
- `ConfidenceEngine.update_confidence()`.
- `ConfidenceEngine.evaluate()` for orchestration-level confidence preparation.
- Knowledge Engine v1 implementation in `backend/core/knowledge.py`.
- `KnowledgeRecord` for structured source-backed knowledge.
- `KnowledgeEngine.create_knowledge()`.
- `KnowledgeEngine.get_knowledge()`.
- `KnowledgeEngine.retrieve_knowledge()`.
- `KnowledgeEngine.update_knowledge()`.
- Deterministic keyword-based knowledge retrieval.
- Skill Engine v1 implementation in `backend/core/skill.py`.
- `SkillRecord` for governed PersonaOS capabilities.
- `SkillEngine.create_skill()`.
- `SkillEngine.get_skills()`.
- `SkillEngine.update_skill()`.
- `SkillEngine.remove_skill()`.
- Evolution Engine v1 implementation in `backend/core/evolution.py`.
- `EvolutionRecord` for controlled change proposals.
- `EvolutionEngine.propose_evolution()`.
- `EvolutionEngine.get_evolutions()`.
- `EvolutionEngine.apply_evolution()`.
- Integration Phase Step 1 completed, moving the backend from independent engine modules into the first integrated cognitive pipeline.
- Integration Phase Step 2 completed, adding persona-memory fusion while preserving engine boundaries.
- `FusionContext` model in `backend/models/fusion.py`.
- `PersonaMemoryFusion` layer in `backend/fusion/persona_memory.py`.
- Persona-aware memory interpretation from active persona perspective.
- PersonaOS fusion integration through `PersonaOS.process_context()`.
- Fusion results in the shared context boundary alongside unchanged raw memories.
- Persona Import Pipeline completed through data and deterministic transformation boundaries.
- `PersonaSource` model for external persona information sources.
- `PersonaImportResult` model for import analysis output.
- `PersonaImporter` deterministic boundary for converting sources into import results.
- `PersonaProfileBuilder` deterministic boundary for converting import results into `PersonaProfile`.
- Persona Versioning data boundary completed through `PersonaVersion`.
- Persona version snapshots now support profile snapshots and source tracking.
- Persona Library Workflow started through the `PersonaLibraryEntry` model boundary.
- `PersonaLibraryEntry` connects `PersonaProfile`, `PersonaVersion` records, source references, lifecycle state, and the current version reference.
- Persona Library lifecycle management completed through `PersonaLibraryEntry`.
- Persona review workflow completed through review submission, approval, and rejection boundaries.
- Persona activation workflow completed through `PersonaActivationManager`.
- Persona selection now requires an approved, active persona with a valid current version reference.
- Basic pytest configuration in `pytest.ini` with `pythonpath = .`.
- Runtime initialization test in `tests/test_runtime.py`.
- Memory engine tests in `tests/test_memory.py`.
- Memory retrieval tests in `tests/test_memory_retrieval.py`.
- Memory update tests in `tests/test_memory_update.py`.
- Memory forgetting tests in `tests/test_memory_forget.py`.
- MemoryRetriever tests in `tests/test_retrieval.py`.
- PersonaOS memory retrieval integration test in `tests/test_persona_memory.py`.
- PersonaOS orchestration integration tests in `tests/test_integration.py`.
- PersonaEngine tests in `tests/test_persona.py`.
- Persona-Memory integration tests in `tests/test_persona_memory_integration.py`.
- Fusion context tests in `tests/test_fusion_context.py`.
- PersonaMemoryFusion tests in `tests/test_persona_memory_fusion.py`.
- PersonaOS fusion integration tests in `tests/test_persona_os_fusion_integration.py`.
- ConfidenceEngine tests in `tests/test_confidence.py`.
- KnowledgeEngine tests in `tests/test_knowledge.py`.
- SkillEngine tests in `tests/test_skill.py`.
- EvolutionEngine tests in `tests/test_evolution.py`.

Current verification status:

- `tests/test_runtime.py` verifies that `create_app()` returns a `PersonaOS` instance with Persona, Memory, Knowledge, Skill, Confidence, and Evolution engines initialized.
- `tests/test_memory.py` verifies that `MemoryEngine.create_memory()` stores and returns a memory, and that `get_memories()` returns stored memories.
- `tests/test_memory_retrieval.py` verifies MemoryEngine retrieval filtering.
- `tests/test_memory_update.py` verifies MemoryEngine lifecycle field updates.
- `tests/test_memory_forget.py` verifies forgotten memory state behavior without deletion.
- `tests/test_retrieval.py` verifies MemoryRetriever relevance, limits, and irrelevant-memory exclusion.
- `tests/test_persona_memory.py` verifies PersonaOS memory retrieval integration.
- `tests/test_integration.py` verifies PersonaOS initialization, context processing, confidence boundary ownership, empty context handling, and orchestration flow.
- `tests/test_persona.py` verifies default profile creation, trait storage, trait retrieval, profile access, and readable persona description.
- `tests/test_persona_memory_integration.py` verifies persona memory preferences, active persona access from MemoryEngine, base priority calculation, and persona-influenced memory priority.
- `tests/test_fusion_context.py` verifies `FusionContext` defaults and stored values.
- `tests/test_persona_memory_fusion.py` verifies persona-memory fusion output, persona-specific interpretations, relevance scoring, and raw memory preservation.
- `tests/test_persona_os_fusion_integration.py` verifies PersonaOS fusion initialization, context fusion results, and raw memory preservation.
- `tests/test_persona_source.py` verifies external persona source data.
- `tests/test_persona_import.py` verifies persona import result data.
- `tests/test_persona_importer.py` verifies deterministic persona importing.
- `tests/test_persona_profile_builder.py` verifies import-result to profile transformation.
- `tests/test_persona_version.py` verifies persona version snapshots and source tracking.
- `tests/test_persona_library_entry.py` verifies PersonaLibraryEntry initialization, lifecycle state defaults, and current version reference storage.
- `tests/test_persona_activation.py` verifies activation rules, inactive behavior, valid version requirements, and immutable version snapshots.
- `tests/test_persona_library_lifecycle_integration.py` verifies the PersonaSource to activated PersonaSelector lifecycle flow.
- `tests/test_confidence.py` verifies initial confidence calculation, confidence increase with positive evidence, confidence decrease with negative evidence, and 0-1 range clamping.
- `tests/test_knowledge.py` verifies knowledge creation, deterministic retrieval, updates, and unrelated-record exclusion.
- `tests/test_skill.py` verifies skill creation, retrieval, updates, and removal.
- `tests/test_evolution.py` verifies evolution proposal creation, retrieval, application, and history preservation.
- Current recorded test status: 120 test functions discovered with fallback verification passing.

Current implementation limits:

- Memory storage is in-memory only.
- There is no persistence layer yet.
- Memory retrieval, update, and forgetting exist in v1 form, but persistence, advanced ranking, consolidation, and durable lifecycle auditing are not implemented yet.
- Persona traits influence memory priority in v1 form, but deeper persona-aware retrieval and confidence evaluation are not implemented yet.
- PersonaMemoryFusion provides persona-aware memory interpretation in v1 form.
- Persona import, versioning, library lifecycle, review, and activation boundaries exist, but persistence, Runtime Intelligence, LLM adapter integration, and advanced persona-specific memory scopes are not implemented yet.
- Confidence evaluation exists in v1 form, but broader risk analysis and cross-engine confidence behavior are not implemented yet.
- All six core engines now have v1/foundation implementations.
- PersonaOS now has an integrated cognitive pipeline for assembling persona, memory, knowledge, confidence, and context output.
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
- `state`: The memory lifecycle state, defaulting to `MemoryState.NEW`.

Importance and confidence are intentionally separate. A memory can be important but uncertain, or reliable but minor.

Memory Layer v1 is complete. The current implementation supports `create_memory()`, `get_memories()`, `retrieve_memory()`, `update_memory()`, and `forget_memory()`. `MemoryRetriever` v1 adds keyword-based retrieval over memory content and category, weighted by confidence and importance.

## 6. Persona System

The Persona system is intended to make identity explicit.

The current foundation includes `PersonaProfile` and `PersonaEngine`. `PersonaProfile` stores persistent identity data, including name, traits, values, style, and boundaries. `PersonaEngine` manages behavior around the active profile, including trait updates, trait lookup, profile access, readable persona description, and memory preference exposure.

Future goals include supporting multiple personalities or personas within a shared PersonaOS environment. Each persona should be able to have its own identity, preferences, behavioral rules, boundaries, memory scope, knowledge access, and skill permissions.

Persona configuration will likely become a first-class part of the backend. A persona should not be defined only by a prompt string. It should have structured state that can be inspected, versioned, and used to assemble the active operating context.

Different personas may eventually load different skills. For example, one persona may be configured for software engineering workflows while another may be configured for writing, research, or operations. Skill access should remain governed and separate from identity.

Personality consistency is a central goal. PersonaOS should preserve stable identity over time while allowing controlled refinement. The Evolution Engine should help prevent personality drift by ensuring that durable persona changes are explicit, justified, and traceable.

Persona-Memory integration now allows persona traits to influence deterministic memory priority. Integration Phase Step 2 adds `PersonaMemoryFusion`, which produces persona-aware interpretations of retrieved memories without changing raw memories or merging PersonaEngine and MemoryEngine. The Persona layer now also includes structured import, version snapshot, library lifecycle, review, and activation boundaries from `PersonaSource` through `PersonaSelector`. Future design should expand this into Runtime Intelligence preparation, memory importance, confidence evaluation, and retrieval preference without collapsing persona and memory into the same system.

## 7. Skill System

Skills are modular capabilities.

The Skill Engine manages what a digital mind can do, not who it is. Skills may represent tools, workflows, external integrations, local actions, domain routines, or multi-step procedures.

Skill Engine v1 is complete. The current implementation includes `SkillRecord` with `name`, `description`, `category`, `confidence`, and `metadata`, and supports `create_skill()`, `get_skills()`, `update_skill()`, and `remove_skill()`. Skills remain in-memory only, and execution, permission enforcement, and evaluation are future work.

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

Knowledge Engine v1 is complete. The current implementation includes `KnowledgeRecord` and supports `create_knowledge()`, `get_knowledge()`, `retrieve_knowledge()`, and `update_knowledge()`. Retrieval uses deterministic keyword matching and remains in-memory only.

Knowledge is different from memory. Knowledge preserves reference material. Memory preserves experience. A style guide document belongs to knowledge; a user's repeated preference for a certain summary style belongs to memory.

The Knowledge Engine should work closely with the Confidence Engine. Source reliability, freshness, evidence strength, and conflicting references should affect how strongly retrieved knowledge influences system behavior.

## 9. Confidence System

AI systems need confidence awareness because fluent generation can sound certain even when support is weak.

The Confidence Engine is intended to help PersonaOS evaluate reliability. It should distinguish between verified knowledge, remembered experience, inferred assumptions, weak evidence, missing context, and uncertainty.

Confidence Engine v1 evaluates confidence for `MemoryRecord` objects. It supports `calculate_confidence(memory)` and `update_confidence(memory, evidence_strength)`.

Current confidence factors include:

- Source reliability.
- Repeated confirmation.
- Evidence strength.
- Uncertainty penalty.

The Confidence Engine evaluates confidence only. It does not own memory storage, does not modify MemoryEngine behavior, and does not call external models.

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

The Evolution Engine governs durable changes to persona, behavior, preferences, operating rules, skill usage, confidence policies, and other long-term patterns. Evolution should not happen automatically just because an interaction occurred.

Evolution Engine v1 is complete. The current implementation includes `EvolutionRecord` with `target`, `change`, `reason`, `confidence`, and `timestamp`, and supports `propose_evolution()`, `get_evolutions()`, and `apply_evolution()`. Evolution proposals are explicit and controlled. Applying an evolution records the decision inside the Evolution Engine, but does not automatically modify Persona, Memory, or any other engine.

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

Current status: complete for the initial foundation scope. The backend skeleton, runtime initialization, memory models, Memory Layer v1, and test coverage exist.

### Phase 2: Memory System

Current status: Memory Layer v1 complete.

- `MemoryRecord` lifecycle support exists.
- `MemoryState` support exists.
- `MemoryEngine` supports create, get, retrieve, update, and forget operations.
- `MemoryRetriever` v1 supports keyword-based relevance retrieval.
- PersonaOS memory retrieval integration test exists.
- Future work should add persistent storage, consolidation, advanced ranking, and lifecycle auditing.

### Phase 3: Persona System

- Current status: Persona system foundation complete.
- `PersonaProfile` exists.
- `PersonaEngine` is profile-backed.
- Persona trait management exists.
- PersonaEngine tests exist.
- Persona-Memory integration layer exists.
- Persona-memory fusion layer exists.
- Persona Import Pipeline boundaries exist.
- Persona Versioning boundary exists.
- PersonaLibraryEntry model boundary exists.
- Persona Library lifecycle, review, activation, and integration verification coverage exist.
- Next work should prepare Runtime Intelligence boundaries.
- Add persona profiles.
- Support multiple personas.
- Connect personas to memory scopes, skill permissions, and operating constraints.
- Add tests for persona initialization and selection.

### Phase 4: Skill System

- Current status: Skill Engine v1 complete.
- `SkillRecord` exists.
- `SkillEngine` supports create, get, update, and remove operations.
- Future work should add skill loading and registration.
- Add permission and governance metadata.
- Explore a skill marketplace or registry concept.
- Connect skills with personas and context.

### Phase 5: Knowledge And Reasoning

- Current status: Knowledge Engine v1 complete.
- `KnowledgeRecord` exists.
- `KnowledgeEngine` supports create, get, retrieve, and update operations.
- Deterministic keyword-based retrieval exists.
- Future work should add knowledge source ingestion.
- Connect knowledge retrieval with confidence assessment.
- Preserve the boundary between memory and knowledge.

### Phase 6: Evolution And Self-Improvement

- Current status: Evolution Engine v1 complete.
- `EvolutionRecord` exists.
- `EvolutionEngine` supports propose, get, and apply operations.
- Future work should add versioning and traceability.
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

- Prepare Runtime Intelligence boundaries.
- Introduce an LLM adapter boundary without binding PersonaOS to one provider.
- Add model configuration and provider abstraction layers.
- Plan runtime context assembly from persona, memory, knowledge, confidence, and fusion outputs.
- Keep persona data independent from LLM/model provider state.

The project has completed the Persona Import Pipeline boundaries, Persona Versioning data boundary, and Persona Library lifecycle foundation. The best next work is small, well-tested backend progress on Runtime Intelligence preparation while preserving the existing boundaries between persona, memory, fusion, knowledge, skill, confidence, evolution, and model-provider responsibilities.
