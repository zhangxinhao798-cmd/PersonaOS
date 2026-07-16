# PersonaOS Roadmap

## Project Vision

PersonaOS is a long-term effort to build an operating system for digital minds.

The goal is not to create another chatbot framework. PersonaOS is intended to provide the operating layer around AI systems: identity, memory, knowledge, skills, confidence, and controlled evolution. A digital mind should be able to persist across interactions, remember meaningful experience, reason over grounded knowledge, use modular capabilities, and improve without losing coherence.

The project should remain understandable, inspectable, and modular as it grows. Language models may provide reasoning and generation, but PersonaOS defines the surrounding architecture that makes a digital mind durable and governable.

## Development Philosophy

PersonaOS follows an architecture-first development approach. Major concepts should be defined clearly before implementation expands.

Development should follow these principles:

- Architecture first: Preserve clear boundaries between persona, memory, knowledge, skills, confidence, and evolution.
- Modular engines: Keep each core system independent, replaceable, and easy to reason about.
- Incremental implementation: Build small working pieces rather than large speculative systems.
- Documentation-driven development: Keep architectural intent visible for future developers and AI assistants.
- Testing before expansion: Add or update tests as behavior becomes real.

The project should prioritize the Python backend before frontend work unless frontend work is explicitly requested.

## Phase 1: Foundation Layer

Status: Completed / In Progress

This phase establishes the conceptual and technical base of PersonaOS.

Completed or in progress:

- Repository structure for backend, docs, tests, configuration, frontend, memory, knowledge, personas, and scripts.
- Documentation system under `docs/`.
- Project-level handoff and changelog documents.
- Backend skeleton under `backend/`.
- Core engine interfaces for Persona, Memory, Knowledge, Skill, Confidence, and Evolution.
- Top-level `PersonaOS` runtime object.
- Runtime initialization through `backend/main.py`.
- Startup logging for engine readiness.
- pytest configuration through `pytest.ini`.
- Runtime initialization tests.
- Initial memory tests.

This phase remains active while the project fills in core models and keeps documentation aligned with implementation.

## Integration Phase

Status: Current

This phase connects the completed v1 engines through explicit orchestration flows while preserving engine boundaries.

Completed:

- Integration Phase Step 1.
- Context boundary layer.
- PersonaOS Orchestrator v1.
- ContextBuilder.
- Integration tests.
- Confidence orchestration correction so confidence preparation belongs to the Confidence Engine.
- Integration Phase Step 2.
- `FusionContext`.
- `PersonaMemoryFusion`.
- Persona-aware memory interpretation.
- PersonaOS fusion integration.
- Fusion tests.
- Persona Import Pipeline:
  - [x] PersonaSource
  - [x] PersonaImportResult
  - [x] PersonaImporter
  - [x] PersonaProfileBuilder
- Persona Versioning:
  - [x] PersonaVersion data model
  - [x] profile snapshot boundary
  - [x] source tracking boundary
- Persona Library Workflow:
  - [x] PersonaLibraryEntry model boundary
  - [x] lifecycle state boundary on library records
  - [x] current version reference boundary
  - [x] profile, version, and source reference linkage
  - [x] Persona Library lifecycle management
  - [x] Persona review workflow
  - [x] Persona activation workflow
  - [x] Persona Library lifecycle integration verification
- Runtime Intelligence Phase preparation:
  - [x] runtime context assembly
  - [x] `RuntimeContext` boundary
  - [x] `RuntimeContextAssembler`
  - [x] `PromptPackage`
  - [x] `PromptBuilder`
  - [x] `FinalPrompt`
  - [x] `PromptRenderer`
  - [x] `BaseLLMAdapter`
  - [x] `LLMResponse`
  - [x] `ProviderConfig`
  - [x] `AdapterRegistry`
  - [x] `OllamaAdapter` v1
  - [x] local Ollama / `qwen3:14b` smoke verification
  - [x] `ChatRuntime`
  - [x] `RuntimeSession`
  - [x] interactive CLI runtime
  - [x] temporary in-memory conversation history
  - [x] local two-turn chat verification
  - [x] CLI commands for help, history, status, clear, and exit
  - [x] `qwen3:14b` interactive runtime verification
  - [x] Runtime Configuration System v1
  - [x] configuration file loading
  - [x] provider/model/endpoint/options loading
  - [x] adapter selection through `AdapterRegistry`
  - [x] removal of hard-coded runtime model configuration from CLI and smoke scripts
  - [x] live model switching verification
  - [x] `qwen3:14b` configuration verification
  - [x] `gemma4:12b` configuration verification
  - [x] restoration of `qwen3:14b` as default

### Runtime Intelligence Phase Preparation

Runtime Context Assembly, the structured prompt pipeline, provider-independent adapter boundaries, provider registry/configuration data boundary, OllamaAdapter v1, controlled ChatRuntime, RuntimeSession, interactive CLI runtime, temporary in-memory conversation history, Runtime Configuration System v1, and local model switching verification are completed.

Completed:

- `RuntimeContext` data boundary.
- `RuntimeContextAssembler` for preparing runtime-ready context from active persona, memory, knowledge, skills, confidence, and fusion context.
- `PromptPackage` structured runtime prompt artifact.
- `PromptBuilder` deterministic formatting from `RuntimeContext`.
- `FinalPrompt` rendered prompt artifact.
- `PromptRenderer` deterministic prompt rendering from `PromptPackage`.
- `BaseLLMAdapter` provider-independent generation contract.
- `LLMResponse` standardized provider response boundary.
- `ProviderConfig` provider/model configuration data boundary.
- `AdapterRegistry` deterministic adapter registration and lookup.
- `OllamaAdapter` v1 provider transport boundary.
- Manual local Ollama smoke verification with `qwen3:14b`.
- `ChatRuntime` controlled generation boundary.
- `RuntimeSession` temporary in-memory conversation history.
- Interactive local CLI runtime.
- Local two-turn chat verification.
- CLI commands for `/help`, `/history`, `/status`, `/clear`, and `/exit`.
- Interactive `qwen3:14b` runtime verification.
- Runtime Configuration System v1.
- Configuration loading from `config/runtime.json`.
- Provider, model, endpoint, and options loading.
- Adapter selection through `AdapterRegistry`.
- Configuration-driven CLI and smoke scripts.
- Live configuration-only switching between `qwen3:14b` and `gemma4:12b`.
- Restoration of `qwen3:14b` as the current default.

Next item:

- SessionManager or Chat API boundary.

The next backend boundary should prepare PersonaOS for Web/API usage while preserving RuntimeSession temporary history, persona package selection, expression package loading, and provider boundaries.

Requirements:

- Model independent.
- Replaceable providers.
- No core engine modification.
- No automatic durable memory or persona mutation.

Current verified runtime flow:

```text
approved and active PersonaLibraryEntry
    -> PersonaSelector
    -> PersonaOSContext
    -> RuntimeContextAssembler
    -> ChatRuntime
    -> RuntimeSession
    -> PromptBuilder
    -> PromptRenderer
    -> runtime configuration loader
    -> ProviderConfig
    -> AdapterRegistry
    -> OllamaAdapter
    -> configured local model
    -> LLMResponse
```

`RuntimeSession` owns temporary in-memory conversation history only. This history is not durable `MemoryEngine` memory and does not update persona profile, version, or library records.

## Runtime Configuration System

Status: Completed

Completed:

- Configuration file boundary.
- Provider configuration loading.
- Adapter selection through `AdapterRegistry`.
- Default provider/model configuration.
- Configuration-driven CLI and smoke scripts.
- Validation for missing or invalid provider settings.
- No core engine changes required when switching models.
- Live switching verification between `qwen3:14b` and `gemma4:12b`.

The current local provider setting:

```text
provider: ollama
model: qwen3:14b
```

is loaded from `config/runtime.json`. `qwen3:14b` is the restored current
default. It remains a replaceable runtime setting, not persona identity.

## Persona Package v1

Status: Completed

Completed scope:

- Canonical persona package directory format.
- Package manifest.
- `PersonaPackageManifest`.
- `PersonaPackage`.
- `PersonaPackageValidationResult`.
- `PersonaPackageLoader`.
- `PersonaProfile` data.
- Speech patterns.
- Thinking patterns.
- Values.
- Boundaries.
- Examples.
- Source references.
- Optional knowledge references.
- Package validation.
- Package loading.
- Deterministic package validation.
- Deterministic package loading.
- Conversion into existing `PersonaProfile`, `PersonaVersion`, and
  `PersonaLibraryEntry` boundaries.
- Conversion to `PersonaProfile`.
- Conversion to `PersonaVersion`.
- Conversion to draft `PersonaLibraryEntry`.
- Human review remains required before approval and activation.

Explicitly deferred:

- LLM-based persona reconstruction.
- Automatic extraction from private conversations.
- Automatic approval.
- Automatic activation.
- Durable database persistence.
- Voice cloning.
- Avatar generation.
- Relationship state.
- Emotion state.
- Automatic review.
- Automatic activation.
- LLM calls.

## Sample Persona Package + CLI package loading

Status: Completed

Completed scope:

- Added the sample Architect package under `personas/architect`.
- Added `manifest.json`, `profile.json`, `examples.json`, `sources.json`, and `knowledge.json`.
- Loaded the sample package through deterministic package loading.
- Validated the sample package before use.
- Converted the loaded package into existing persona profile, version, and draft library entry boundaries.
- Added CLI package loading.
- Removed hard-coded runtime guide profile construction from the CLI.
- Preserved human review before approval through in-memory CLI startup review.
- Preserved explicit activation through in-memory CLI startup activation.
- Avoided LLM calls and persona reconstruction.
- Verified 235 tests passing.
- Verified 240 tests passing after CLI multi-persona package selection.

## CLI multi-persona package selection

Status: Completed

Completed scope:

- Discover available persona packages under `personas/`.
- Add `/persona list` to show loadable package IDs and names.
- Add `/persona use <package_id>` to switch the active in-memory persona during a CLI session.
- Validate the selected package before switching.
- Preserve review, versioning, library, activation, and selector boundaries.
- Keep package switching independent from provider/model configuration.
- Avoid durable writes, automatic approval persistence, and persona reconstruction.

## Second sample Persona Package

Status: Completed

Completed scope:

- Add a second sample persona package under `personas/`.
- Include manifest, profile, examples, sources, and optional knowledge files.
- Validate the second package through `PersonaPackageLoader`.
- Verify `/persona list` shows multiple package-derived personas.
- Verify `/persona use <package_id>` switches between package-derived personas.
- Preserve deterministic package validation and loading.
- Preserve review, versioning, library, activation, selector, runtime, and provider boundaries.
- Avoid durable writes, automatic approval persistence, persona reconstruction, relationship state, emotion state, voice, or avatar behavior.

## Persona package selection UX

Status: Completed

Completed scope:

- Added richer `/persona list` output with package id, name, version, and description.
- Added `/persona info <package_id>`.
- Added `default_persona` support in `config/runtime.json`.
- Added CLI startup override with `--persona <package_id>`.
- Preserved package files and durable PersonaOS state.

## Expression Package v1

Status: Completed

Completed scope:

- Added `ExpressionPackageManifest`.
- Added `ExpressionStyle`.
- Added `ExpressionPackage`.
- Added `ExpressionPackageValidationResult`.
- Added `ExpressionPackageLoader`.
- Added sample expression packages under `expressions/architect` and `expressions/strategist`.
- Modeled tone, rhythm, pacing, vocabulary, catchphrases, sentence patterns, pause patterns, emphasis patterns, and avoid rules.
- Preserved separation between Persona Core and Expression Layer.
- Explicitly avoided voice cloning, TTS, avatar, relationship, and emotion behavior.

## Expression Runtime Integration v1

Status: Completed

Completed scope:

- Runtime CLI loads optional expression packages by active persona id.
- Expression guidance is stored in `PersonaOSContext.metadata.expression`.
- `RuntimeContext` carries expression guidance through `expression`.
- `PromptPackage` includes an `expression` section.
- `PromptRenderer` renders expression guidance as `## Expression`.
- Persona switching also switches expression context.
- Missing expression packages do not block runtime use.

## SessionManager / Chat API preparation

Status: Current

Planned scope:

- Add an in-memory SessionManager or API-ready chat boundary.
- Manage multiple `session_id` values for future Web UI usage.
- Preserve `RuntimeSession` as temporary conversation history only.
- Expose persona list, persona info, active persona, send message, clear history, and switch persona through backend boundaries.
- Avoid frontend implementation until the backend API boundary is stable.
- Avoid durable memory writes, database persistence, voice, avatar, relationship, and emotion behavior.

### Step 2: Persona + Memory Fusion

This integration step makes Persona influence how Memory is interpreted after retrieval while preserving engine boundaries.

Completed:

- Added persona-aware memory interpretation.
- Weighted fusion relevance by persona traits and values.
- Supported different persona interpretations of the same memory.
- Added fusion results to PersonaOS context output.
- Preserve separation between PersonaEngine and MemoryEngine.

### Completed Phase: Persona Library Workflow

Persona Library workflow is complete at the lifecycle foundation level now that persona import and versioning boundaries exist.

Goals:

- Define persona library boundaries.
- Add PersonaLibrary lifecycle management.
- Add persona import review workflow.
- Validate persona profile data before library use.
- Preserve separation between persona identity, memory storage, and fusion interpretation.

Progress:

- Added `PersonaLibraryEntry` as the lifecycle owner for persona library records.
- Connected `PersonaProfile`, `PersonaVersion` records, source references, lifecycle state, and current version reference.
- Added lifecycle states for draft, reviewing, approved, and archived records.
- Added review submission, approval, and rejection workflow.
- Added activation workflow for approved personas with valid current version references.
- Added end-to-end integration verification for the import-to-activation lifecycle.
- Preserved PersonaEngine, LLM/Ollama, persistence, and runtime orchestration boundaries.

Current focus:

- SessionManager or Chat API boundary.

Next steps:

1. Add an in-memory SessionManager or API-ready chat boundary.
2. Support creating and clearing sessions.
3. Support sending a message through an existing `RuntimeSession`.
4. Support switching active persona package per session.
5. Preserve review, versioning, library, activation, selector, expression, runtime, and provider boundaries.

## Phase 2: Memory System

Status: Memory candidate review foundation complete

The current MemoryEngine stores `MemoryRecord` objects in a simple in-memory list. The next stage is to grow this into a structured memory system while keeping behavior small, testable, and modular.

Goals:

- Improve `MemoryEngine`.
- Add memory retrieval beyond returning every stored record.
- Add memory filtering by category, source, confidence, importance, and timestamp.
- Add importance and confidence ranking.
- Add read-only runtime memory retrieval.
- Add reviewable memory candidates between conversation and durable memory.
- Add deterministic candidate extraction.
- Add candidate review queue.
- Define clearer memory lifecycle operations:
  - Create
  - Retrieve
  - Update
  - Consolidate
  - Forget
- Add persistent storage.
- Expand tests for memory creation, retrieval, filtering, ranking, update, and persistence.

Memory should remain distinct from raw conversation history and external knowledge.

Completed:

- Memory Runtime Integration v1.
- `RuntimeMemoryRetriever` read path.
- `MemoryCandidate` model.
- Deterministic `CandidateExtractor`.
- `ReviewQueue` for pending, approved, and rejected candidates.
- RuntimeSession optional candidate production.
- No automatic memory writing from conversation.
- No LLM summarization or automatic approval.
- Memory Promotion Boundary v1.
- Approved-candidate-to-`MemoryRecord` conversion.
- Explicit promotion into `MemoryEngine`.
- Memory Candidate Review Controls v1.
- `MemoryReviewApiBoundary`.
- API Transport routes for candidate listing, approval, rejection, clearing, and explicit promotion.
- Stable JSON review-control responses.
- All durable writes remain routed through `MemoryPromotionBoundary`.

Next:

- Decide whether review controls should also be exposed through the interactive CLI.
- Prepare future persistent storage through repository boundaries without allowing RuntimeSession, SessionManager, CandidateExtractor, or ReviewQueue to write durable memory directly.
- Keep all durable memory writes routed through `MemoryPromotionBoundary`.

## Phase 3: Persona System

This phase turns persona from a placeholder engine into structured identity management.

Goals:

- Define persona models.
- Support multiple personas.
- Add identity management.
- Add behavior configuration.
- Define persona memory scope.
- Define persona skill permissions.
- Support personality consistency across interactions.
- Prepare for controlled persona evolution without personality drift.

Persona should remain an explicit architectural layer, not a hidden prompt fragment.

## Phase 4: Skill System

This phase introduces modular capabilities for digital minds.

Goals:

- Define skill descriptors.
- Add a skill registry.
- Add skill loading.
- Support persona-specific skills.
- Add permission management.
- Track skill outcomes.
- Support skill evolution over time.

Skills should remain capabilities, not personalities. A persona may have access to a skill, but the skill should not redefine the persona's identity.

## Phase 5: Knowledge System

This phase adds source-backed reference material.

Goals:

- Define knowledge records.
- Add source management.
- Add knowledge retrieval.
- Add indexing.
- Preserve source metadata and freshness.
- Integrate with the Confidence Engine.
- Keep knowledge distinct from memory.

Knowledge should represent external, referenceable information such as documents, files, APIs, standards, manuals, project notes, and structured records.

## Phase 6: Confidence System

This phase adds reliability awareness across PersonaOS.

Goals:

- Add reliability assessment.
- Add evidence evaluation.
- Add uncertainty detection.
- Add risk analysis.
- Add confidence calibration.
- Use confidence signals to prevent overconfident claims or unsafe actions.

Confidence should help the system distinguish verified information, remembered experience, inference, weak evidence, and missing context.

## Phase 7: Evolution System

This phase adds controlled long-term improvement.

Goals:

- Add controlled improvement workflows.
- Add change proposals.
- Add proposal evaluation.
- Add versioning.
- Add rollback.
- Preserve identity.
- Prevent uncontrolled personality changes.

Evolution should be deliberate, traceable, and reversible where possible. Durable changes should not happen as accidental side effects of ordinary interaction.

## Future Extensions: Expression Layer

PersonaOS should eventually support expression capabilities that allow a digital mind to communicate its identity through multiple modalities.

Possible future directions:

- Voice Layer
  - Give personas distinct voice characteristics.
  - Keep voice identity separate from persona core data.

- Speech Style Modeling
  - Model vocabulary preferences, sentence patterns, tone, and communication habits.
  - Preserve separation between personality identity and generated output style.

- Persona Expression Layer
  - Provide a dedicated layer for expressing persona traits through language, voice, and interaction style.
  - Avoid mixing expression behavior with memory, knowledge, or identity storage.

- TTS Integration
  - Support replaceable text-to-speech providers.
  - Keep audio generation independent from persona architecture.

- Multimodal Persona Interface
  - Support future visual, audio, and interactive interfaces.
  - Maintain the same architecture boundaries across different interfaces.

These capabilities belong to future expression and interface layers. They should be built after Runtime Intelligence and core architecture stabilization.

## User-Persona Relationship System

Relationship is a core PersonaOS system describing the interaction context between a user and a persona. It remains separate from Persona identity, Memory, and Emotion.

Completed:

- [x] Relationship Context Boundary v1.
- [x] `RelationshipContext` model for relationship type, interaction style, tone, permissions, lifecycle, and metadata.
- [x] Relationship context carried independently through session, runtime context, prompt package, and chat API boundaries.
- [x] Persona identity and durable memory remain unchanged by relationship context.

Planned:

- [ ] Relationship Selection through explicit session controls.
- [ ] Relationship Context presets or other reviewable selection sources.
- [ ] Relationship Evolution through governed, inspectable, and reversible changes.
- [ ] Relationship Memory through a dedicated relationship-scoped experience boundary.
- [ ] Separate relationship state for the same persona across different users.

Explicitly deferred:

- Emotion simulation.
- Automatic relationship generation.
- Automatic trust or familiarity progression.
- Durable relationship persistence.
- Silent mutation of Persona identity.

## Frontend Internationalization

Status: Planned

Frontend internationalization is a future productization direction and does not change Persona, Runtime, or provider architecture.

Planned:

- [ ] Chinese UI support.
- [ ] English UI support.
- [ ] A dedicated `frontend/i18n/` language-file boundary for user-facing interface text.
- [ ] Explicit language selection with a deterministic default and fallback.
- [ ] Keep UI language independent from active persona identity and model provider.

No frontend internationalization implementation is included in the current phase.

## Future Persona Experience Systems

These systems are long-term architectural directions, not implemented features. They remain separate from Persona core identity and Runtime Intelligence.

Persona Reconstruction Engine:

- Conversation import.
- Evidence extraction.
- Thinking pattern extraction.
- Speech pattern extraction.
- Relationship context.
- Reviewable persona profiles.
- Versioned persona library entries.
- Reconstruction remains unimplemented and must not bypass human review.

Expression Layer:

- Language style.
- Speech patterns.
- Vocabulary.
- Catchphrases.
- Multimodal expression.
- Expression remains independent from personality.

Voice Layer:

- Replaceable TTS adapters.
- Voice profiles.
- Speaking rhythm and tone.
- Voice remains independent from cognition and identity.

Avatar Layer:

- Visual persona representation.
- Replaceable avatar providers.
- Avatar state remains independent from core persona identity.

Relationship Layer:

- Relationship Context Boundary v1 is complete.
- Relationship Selection is the next planned interaction capability.
- Relationship-specific memory remains future work.
- Governed trust and familiarity progression belongs to future Relationship Evolution.
- Shared experiences and long-term goals remain future work.
- The same persona may maintain separate relationships with different users in a future durable relationship system.
- Emotion simulation and automatic relationship generation are not part of the current boundary.

Emotion Layer:

- Temporary emotional state.
- Emotional continuity.
- Emotion-aware expression.
- Emotional state must not silently rewrite durable persona identity.

Companion Engine:

- Relationship memory.
- Long-term goals.
- Initiative engine.
- Emotional continuity.
- Habit learning.
- Companion behavior remains unimplemented and separate from durable persona identity.

## Long-Term Vision

Future directions may include:

- Multiple digital minds operating in a shared environment.
- Persona-specific memory, knowledge, and skill boundaries.
- A reusable skill ecosystem.
- Human-AI collaboration workflows.
- Persistent AI companions.
- Persistent research assistants.
- Project-aware digital collaborators.
- Shared knowledge spaces between digital minds.
- Auditable evolution histories.
- Interfaces for inspecting memory, persona state, confidence, and skill use.

PersonaOS should grow into a platform where digital minds can remain coherent, useful, inspectable, and responsibly adaptable over time.

## Current Priority

The immediate next focus is Relationship Selection v1 through existing API and Web Experience boundaries. Frontend Chinese/English internationalization is recorded as a later productization milestone; it is not part of the current implementation scope.
