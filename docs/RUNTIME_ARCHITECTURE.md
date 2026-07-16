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
boundaries. `RuntimeContext`, `RuntimeContextAssembler`, `BaseLLMAdapter`, and
`LLMResponse` exist as implemented boundary components. `PromptBuilder`, model
configuration, provider adapters, provider calls, and response processing are
planned runtime boundaries and should not be treated as implemented until code
and tests exist.

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
- Metadata

Rules:

- `RuntimeContext` is not durable storage.
- `RuntimeContext` should not mutate source records.
- `RuntimeContext` should preserve source boundaries.
- `RuntimeContext` should remain model-provider independent.

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

`PromptBuilder` is a planned boundary for constructing model input. It should
convert `RuntimeContext` and the current user input into a structured,
inspectable prompt package.

Responsibilities:

- Convert `RuntimeContext` and current user input into structured model input.
- Express persona traits, values, thinking patterns, speech patterns,
  boundaries, examples, memory, knowledge, confidence, and relevant runtime
  metadata.
- Keep formatting separate from provider transport.

Rules:

- `PromptBuilder` must not call providers.
- `PromptBuilder` must not mutate persona or memory data.
- `PromptBuilder` should produce an inspectable prompt package.
- Provider adapters may translate the prompt package into provider-specific
  request payloads.

The prompt package should be understandable before it reaches any provider. This
keeps prompt construction separate from transport, authentication, endpoint
behavior, and provider-specific request formats.

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

Future provider adapters may include:

- `OllamaAdapter`
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

## 9. Model Configuration

Model configuration is a planned boundary for selecting providers and model
settings without editing core engines.

Possible fields:

- Provider
- Model
- Endpoint
- Timeout
- Generation parameters
- Credentials reference

Future model switching should allow a configuration such as:

```text
provider: ollama
model: qwen3:14b
```

to change to another configured provider and model without modifying PersonaOS
core engines.

Configuration should select adapters through a controlled factory or registry
boundary. Core engines should remain unaware of provider SDKs, credentials,
transport details, and endpoint-specific request structures.

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

The first planned provider integration path is:

```text
RuntimeContext
    ->
PromptBuilder
    ->
OllamaAdapter
    ->
local Ollama endpoint
    ->
qwen3:14b
    ->
LLMResponse
```

This is the first planned provider integration. Ollama and `qwen3:14b` are not
part of PersonaOS core identity. Another provider should be replaceable later
through the same adapter and configuration boundaries.

Streaming, tools, multimodal input, and advanced provider features are deferred.
They should be added only after the core prompt, adapter, configuration, and
response boundaries are clear and tested.

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
- `BaseLLMAdapter`
- `LLMResponse`

Not yet implemented:

- `PromptBuilder`
- Model configuration layer
- Adapter registry or factory
- `OllamaAdapter`
- `qwen3:14b` runtime calls
- Response processing
- Streaming
- Tools
- Persistence

This status reflects runtime architecture boundaries only. It should not be
read as a claim that provider-specific generation or response processing exists.

## 16. Next Recommended Step

The next coding step should be the `PromptBuilder` boundary or model
configuration boundary before provider-specific Ollama integration.

Ollama integration does not exist yet. `qwen3:14b` runtime calls do not exist
yet. Provider-specific work should begin only after the provider-independent
runtime boundaries are clear, inspectable, and tested.
