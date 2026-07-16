# PersonaOS Runtime Architecture

## 1. Purpose

Runtime Intelligence connects prepared PersonaOS context to replaceable
language models. It defines how internal structured context becomes model input
and how model output returns to PersonaOS without weakening engine ownership or
provider boundaries.

Runtime does not own persona identity, memory, knowledge, skills, confidence, or
evolution. Those responsibilities remain inside their owning engines and
lifecycle systems.

Runtime consumes prepared context and returns standardized model output.
Provider-specific behavior belongs behind adapters so PersonaOS can support
local and remote models without making any provider part of core identity or
engine logic.

## 2. Runtime Flow

The intended runtime flow is:

```text
User Input
    ->
PersonaOS Orchestrator
    ->
PersonaSelector
    ->
ContextBuilder
    ->
RuntimeContextAssembler
    ->
RuntimeContext
    ->
PromptBuilder
    ->
PromptPackage
    ->
PromptRenderer
    ->
FinalPrompt
    ->
BaseLLMAdapter
    ->
Provider Adapter
    ->
Language Model
    ->
LLMResponse
    ->
Response Processing
    ->
User Output
```

Some stages in this flow are current boundaries, while others are planned
boundaries. `RuntimeContext`, `RuntimeContextAssembler`, `PromptPackage`,
`PromptBuilder`, `FinalPrompt`, `PromptRenderer`, `BaseLLMAdapter`,
`LLMResponse`, `ProviderConfig`, `AdapterRegistry`, `OllamaAdapter` v1,
`ChatRuntime`, `RuntimeSession`, Runtime Configuration System v1, Expression Package v1, and Expression Runtime Integration v1 exist as implemented boundary components.
The interactive CLI is the first local user-facing runtime interface. Response
processing, streaming, tool calling, multimodal
requests, production API/frontend integration, automatic durable memory writes,
and production persistence remain unimplemented.

## 3. RuntimeContext

`RuntimeContext` is the provider-independent runtime input boundary. It carries
prepared data from PersonaOS orchestration toward future prompt and model
adapter layers.

It may contain:

- Active persona
- Current persona version
- Memories
- Knowledge
- Skills
- Confidence
- Fusion context
- Expression guidance
- Metadata

Rules:

- `RuntimeContext` is not durable storage.
- `RuntimeContext` should not mutate source records.
- `RuntimeContext` should preserve source boundaries.
- `RuntimeContext` should remain model-provider independent.
- Expression guidance should remain separate from persona identity, voice state, relationship state, and emotion state.

The runtime context exists to make prepared information available to the model
path. It is not the owner of any engine state.

## 4. RuntimeContextAssembler

`RuntimeContextAssembler` translates `PersonaOSContext` into runtime-ready
context. It prepares the boundary object used by later runtime layers without
performing generation, provider selection, or durable state changes.

Responsibilities:

- Translate `PersonaOSContext` into runtime-ready context.
- Include selected and activated persona information.
- Carry memory, knowledge, skills, confidence, and fusion output.
- Carry optional expression guidance from prepared metadata.
- Handle missing optional data safely.
- Preserve references and source boundaries.

Non-responsibilities:

- No prompt generation.
- No LLM calls.
- No provider selection.
- No durable state mutation.
- No engine-specific business logic.

`RuntimeContextAssembler` should remain a context assembly boundary. It must not
become a hidden owner of persona behavior, memory lifecycle, knowledge
retrieval, confidence policy, or evolution.

## 5. PromptBuilder

`PromptBuilder` is an implemented boundary for constructing model input. It
converts `RuntimeContext` and the current user input into a structured,
inspectable prompt package.

Responsibilities:

- Convert `RuntimeContext` and current user input into structured prompt
  sections.
- Preserve persona, memory, knowledge, skills, confidence, fusion, expression,
  conversation, user input, and metadata boundaries.
- Keep formatting separate from provider transport.

Rules:

- `PromptBuilder` must not call providers.
- `PromptBuilder` must not mutate persona or memory data.
- `PromptBuilder` should produce an inspectable prompt package.
- `PromptRenderer` converts the prompt package into `FinalPrompt` before a
  provider adapter sends it.

The prompt package should be understandable before it reaches any provider. This
keeps prompt construction separate from transport, authentication, endpoint
behavior, and provider-specific request formats.

`PromptPackage` is a structured runtime artifact, not a provider request.
`PromptRenderer` renders `PromptPackage` into a deterministic `FinalPrompt`
string while preserving section ordering and metadata.

Expression guidance is rendered as its own prompt section. It may include text
style such as tone, rhythm, pacing, vocabulary, catchphrases, sentence patterns,
pause patterns, emphasis patterns, and avoid rules. It is not persona identity,
voice cloning, TTS, avatar behavior, emotion state, or relationship state.

## 6. BaseLLMAdapter

`BaseLLMAdapter` is the current provider-independent adapter interface. It
defines the common generation contract for future provider implementations.

Input:

- `RuntimeContext`
- User input or a future prompt package

Output:

- `LLMResponse`

`BaseLLMAdapter` defines the common generation contract. Core engines must not
depend on Ollama, OpenAI, Claude, Gemini, or other provider SDKs. Provider
implementations should inherit from or follow the base interface so runtime code
can call adapters through a stable boundary.

## 7. Provider Adapters

Provider adapters include:

- `OllamaAdapter`

Future provider adapters may include:

- `OpenAIAdapter`
- `ClaudeAdapter`
- `GeminiAdapter`
- OpenAI-compatible adapter
- Other local or remote providers

Each adapter owns:

- Endpoint communication
- Authentication where required
- Provider request formatting
- Timeout and error handling
- Provider response parsing
- Mapping output into `LLMResponse`

Each adapter does not own:

- Persona identity
- Memory
- Knowledge
- Skill state
- Confidence policy
- Evolution
- Prompt semantics beyond provider translation

Provider adapters are integration boundaries. They may translate PersonaOS
runtime input into provider-specific requests, but they must not become owners
of PersonaOS identity, memory, reasoning policy, or long-term state.

## 8. LLMResponse

`LLMResponse` is the standardized model output returned by LLM adapters.

Possible fields:

- `content`
- `provider`
- `model`
- `metadata`
- `usage`

Rules:

- PersonaOS should consume `LLMResponse` instead of raw provider responses.
- Provider-specific response objects must not leak into core runtime.
- Usage and metadata should remain optional.
- A model response is not automatically durable memory or verified knowledge.

`LLMResponse` normalizes provider output into a stable PersonaOS boundary. It
does not imply that the response is true, durable, or approved for storage.

## 8.1 ChatRuntime And RuntimeSession

`ChatRuntime` is the controlled runtime generation boundary. It connects
approved active persona selection, `PersonaOSContext`, `RuntimeContextAssembler`,
prompt construction, prompt rendering, and the configured adapter boundary.

`RuntimeSession` owns temporary in-memory conversation history for an active
interactive session. This history can support multi-turn generation, but it is
not durable `MemoryEngine` memory and must not silently update memory, persona
profile, persona version, or persona library state.

The first interactive CLI uses these boundaries to provide local conversation
with a configured in-memory persona. That CLI persona is not yet a complete
imported persona package.

## 9. Model Configuration

Model configuration is implemented through `config/runtime.json`, the runtime
configuration loader, `ProviderConfig`, and `AdapterRegistry` for selecting
providers and model settings without editing core engines.

Possible fields:

- Provider
- Model
- Endpoint
- Timeout
- Generation parameters
- Credentials reference

The current default configuration is:

```text
provider: ollama
model: qwen3:14b
endpoint: http://localhost:11434
```

These are replaceable runtime settings, not persona identity. Live switching
between `qwen3:14b` and `gemma4:12b` has been verified by changing
configuration only, and `qwen3:14b` has been restored as the current default.

Configuration selects adapters through the registry boundary. Core engines
should remain unaware of provider SDKs, credentials, transport details, and
endpoint-specific request structures.

## 10. Runtime Ownership Rules

Runtime ownership must remain explicit:

- `PersonaEngine` owns identity behavior.
- `MemoryEngine` owns memory lifecycle.
- `KnowledgeEngine` owns source-backed knowledge.
- `SkillEngine` owns capability records.
- `ConfidenceEngine` owns reliability evaluation.
- `EvolutionEngine` owns controlled change proposals.
- `PersonaSelector` owns runtime persona selection.
- `RuntimeContextAssembler` owns runtime context assembly.
- `PromptBuilder` owns model-input construction.
- Provider adapters own transport and provider translation.
- PersonaOS orchestrates these components without absorbing their logic.

These ownership rules protect PersonaOS from becoming a monolithic model wrapper
or a provider-specific runtime.

## 11. Runtime Mutation Rules

Runtime generation must not directly mutate:

- `PersonaProfile`
- `PersonaVersion`
- `PersonaLibraryEntry`
- `MemoryRecord`
- `KnowledgeRecord`
- `SkillRecord`

Future runtime observations may create:

- Memory candidates
- Evolution proposals
- Confidence signals
- Review candidates

Durable changes require their owning workflows and explicit validation. Runtime
generation may produce suggestions or observations, but applying those changes
belongs to the relevant engine, review process, lifecycle boundary, or evolution
workflow.

## 12. Error Handling

Future runtime error handling should normalize failures from provider adapters
and runtime layers.

Expected failure cases include:

- Adapter unavailable
- Endpoint unreachable
- Timeout
- Invalid provider response
- Empty response
- Context too large
- Unsupported model

Errors should be normalized into runtime-level exceptions or structured failure
results. Provider-specific exceptions should not leak into core engines. This
keeps provider behavior replaceable and prevents core PersonaOS systems from
depending on provider SDK error types.

## 13. Initial Ollama Path

The first provider integration path has been verified locally:

```text
RuntimeContext
    ->
PromptBuilder
    ->
PromptPackage
    ->
PromptRenderer
    ->
FinalPrompt
    ->
OllamaAdapter
    ->
local Ollama endpoint
    ->
qwen3:14b
    ->
LLMResponse
```

This is the first verified provider integration. Ollama and `qwen3:14b` are not
part of PersonaOS core identity. `qwen3:14b` is the current default runtime
model, not persona identity. Another provider should be replaceable later
through the same adapter and configuration boundaries.

The manual live smoke test confirmed that local Ollama was reachable at the
configured endpoint, `qwen3:14b` returned a valid response, usage metadata was
returned, and no durable persona or memory state was modified.

Streaming, tools, multimodal input, and advanced provider features are deferred.
They should be added only after the core prompt, adapter, configuration, and
response boundaries are clear and tested.

## 13.1 Interactive Runtime Path

The first full controlled interactive path has been verified locally:

```text
approved active PersonaLibraryEntry
    ->
PersonaSelector
    ->
PersonaOSContext
    ->
RuntimeContextAssembler
    ->
ChatRuntime
    ->
RuntimeSession
    ->
PromptBuilder
    ->
PromptRenderer
    ->
OllamaAdapter
    ->
local Ollama endpoint
    ->
qwen3:14b
    ->
LLMResponse
```

The verification confirmed that PersonaSelector accepted an approved active
persona, ChatRuntime completed, Ollama was reachable, `qwen3:14b` responded,
temporary two-turn conversation history was used, and durable persona state
remained unchanged.

## 13.2 Runtime Configuration Path

Runtime Configuration System v1 has been verified through this flow:

```text
config/runtime.json
    ->
runtime configuration loader
    ->
ProviderConfig
    ->
AdapterRegistry
    ->
OllamaAdapter
    ->
configured local model
    ->
LLMResponse
```

The CLI and smoke scripts now resolve the configured adapter through
`AdapterRegistry` instead of hard-coding a model or endpoint. Live switching
between `qwen3:14b` and `gemma4:12b` was verified through configuration only.
`qwen3:14b` is restored as the current default configuration.

Switching the configured model changes runtime execution only. It must not
rewrite persona identity, memory, knowledge, persona versions, library records,
or session history semantics.

## 14. Testing Strategy

Future runtime tests should cover:

- `RuntimeContext` creation
- `RuntimeContextAssembler` behavior
- Prompt package construction
- Adapter interface compatibility
- Provider adapter request mapping
- Standardized `LLMResponse` parsing
- Provider switching
- Missing optional context
- Failure normalization
- No mutation of durable source data

Tests should verify both behavior and boundary preservation. Runtime tests
should make sure provider integration does not leak provider-specific code into
core engines or mutate durable PersonaOS state during generation.

## 15. Current Implementation Status

Completed:

- `RuntimeContext`
- `RuntimeContextAssembler`
- `PromptPackage`
- `PromptBuilder`
- `FinalPrompt`
- `PromptRenderer`
- `BaseLLMAdapter`
- `LLMResponse`
- `ProviderConfig`
- `AdapterRegistry`
- `OllamaAdapter` v1
- Initial local `qwen3:14b` path verification
- `ChatRuntime`
- `RuntimeSession`
- Interactive CLI runtime
- Temporary conversation history
- Local multi-turn `qwen3:14b` path verification
- Runtime configuration file boundary
- Runtime configuration loader
- `ProviderConfig` construction from configuration
- `AdapterRegistry` provider resolution
- Configuration-driven CLI
- Live switching between two local Ollama models

Not yet implemented:

- Production API
- Response processing
- Streaming
- Tool calling
- Multimodal requests
- Frontend integration
- Automatic durable memory writes
- Context compression
- Automatic memory extraction
- Persistence
- Cloud provider adapters
- Relationship state
- Emotion state
- Voice
- Avatar

This status reflects runtime architecture boundaries only. It should not be
read as a claim that production chat orchestration, streaming, tool calling,
frontend integration, automatic memory persistence, relationship state, emotion
state, voice, avatar, or response processing exists.

## 16. Next Recommended Step

The next coding step should be Persona Package v1.

The next step should define a file-backed, reviewable persona package format
with deterministic validation and loading, then convert valid packages into the
existing `PersonaProfile`, `PersonaVersion`, and `PersonaLibraryEntry`
boundaries for human review before approval and activation.

Provider-specific work should continue only through replaceable adapter and
configuration boundaries. Runtime integration must not silently mutate durable
persona, version, memory, knowledge, skill, or library state.
