# PersonaOS Architecture Principles

## Purpose

This document defines the non-negotiable architectural boundaries of
PersonaOS. It is the architectural constitution used to evaluate future
features, pull requests, adapters, engines, integrations, and product
extensions.

This document is not an implementation guide. It is not a roadmap. It does not
claim that all described systems already exist. Instead, it defines durable
rules that future work should preserve unless an explicit architecture decision
changes them.

New features should be reviewed against these principles before they are
merged. If a feature weakens or changes one of these rules, the reason, impact,
migration plan, and affected boundaries must be documented through an explicit
architecture decision.

## Principle 1: Identity Is Independent From Models

A language model does not own a persona. Models may express, reason over, or
assist with persona data, but they must not become the source of truth for
identity.

Persona identity must survive model replacement. Changing from Qwen to another
model, or from any provider to another provider, must not erase, redefine, or
silently rewrite identity.

`PersonaProfile`, `PersonaVersion`, `PersonaLibraryEntry`, and related identity
data remain outside provider adapters. Provider adapters may consume prepared
identity context, but they must not own durable identity state.

## Principle 2: Memory Is Independent From Conversation History

Raw chat history is not automatically durable memory. Conversation history is a
record of interaction. Memory is curated, experience-derived context selected
because it may matter beyond the current exchange.

`MemoryEngine` owns the memory lifecycle. Creation, retrieval, update,
consolidation, suppression, and forgetting of durable memories must remain
inside controlled memory boundaries.

LLM adapters must not silently create, edit, or delete durable memories. Runtime
observations may become memory candidates only through explicit memory
workflows.

## Principle 3: Memory And Knowledge Remain Separate

Memory represents experience. Knowledge represents source-backed external
information.

Knowledge retrieval must not directly mutate memory. Retrieved knowledge may
inform reasoning or confidence evaluation, but it should not become memory
without a controlled memory process.

Memory records must not be treated as verified external knowledge without
evidence. A remembered experience may be useful, but it is not the same as a
source-backed fact.

## Principle 4: Skills Are Capabilities, Not Personalities

Skills describe what a persona can do. They represent capabilities, workflows,
tools, permissions, or procedures.

Skills must not redefine persona identity. Giving a persona access to a skill
should not change who the persona is.

Skill access should be governed independently through permissions and
configuration. A persona may be allowed, denied, or limited in skill usage
without rewriting its identity.

## Principle 5: Confidence Evaluates Reliability

`ConfidenceEngine` evaluates evidence and uncertainty. Its role is to help
PersonaOS distinguish verified information, remembered experience, inference,
weak evidence, missing context, and risk.

`ConfidenceEngine` must not own memory, knowledge, or persona state. It may
evaluate signals from those systems, but ownership remains with the appropriate
engine.

Fluent model output must not be treated as evidence by default. Generated text
can be useful, but confidence should depend on sources, memory quality,
evidence, uncertainty, and verification boundaries.

## Principle 6: Evolution Is Controlled And Traceable

Runtime interactions must not silently rewrite identity. A conversation may
produce signals, suggestions, or candidates for change, but durable changes
require controlled workflows.

Durable persona changes require explicit proposals, review, versioning, and
traceability. The system should be able to explain what changed, why it changed,
who or what approved it, and which sources or observations supported it.

Evolution should support rejection, supersession, or rollback where possible.
Controlled growth is part of PersonaOS, but uncontrolled drift is not.

## Principle 7: Import Does Not Equal Activation

Importers create structured candidates. They may transform source material into
reviewable persona data, but they do not decide that a persona is ready for
runtime use.

Imported data must pass review and lifecycle validation. Import should preserve
source traceability, uncertainty, and review status.

Importers must not automatically activate personas. Persona activation must
remain a separate controlled operation with clear lifecycle rules.

## Principle 8: PersonaVersion Is Immutable

`PersonaVersion` represents a historical snapshot. Existing snapshots must not
be edited in place.

Changes create a new version. Version history should remain inspectable and
traceable to sources so future reviewers can understand how a persona changed
over time.

Immutable versions protect identity continuity. They also make review,
rollback, supersession, and comparison possible.

## Principle 9: Runtime Is Read-Only Toward Durable Identity

`RuntimeContext` and model adapters consume prepared persona data. They may use
that data to support a current interaction, but runtime generation must not
directly mutate `PersonaProfile`, `PersonaVersion`, or `PersonaLibraryEntry`.

Runtime observations may create proposals, candidates, or review items, but they
must not silently apply durable identity changes.

Durable identity belongs to explicit persona, versioning, review, lifecycle, and
evolution boundaries, not to the model call path.

## Principle 10: Expression Is Independent From Personality

Speech style, vocabulary, catchphrases, voice, TTS, avatar, and visual
presentation belong to expression layers.

Changing expression must not rewrite persona identity. A persona may alter how
it communicates without changing who it is.

The same persona may use multiple voices or interfaces. Likewise, multiple
personas may share an interface while preserving distinct identities.

## Principle 11: Voice Is Independent From Cognition

Voice generation is an adapter-layer responsibility. TTS and voice providers
must not own reasoning, memory, or identity.

Voice replacement must not require core persona changes. A persona's voice,
speech renderer, or audio provider may change while preserving the same
underlying identity and cognitive context.

Voice systems may express a persona, but they must not become the persona.

## Principle 12: Every External Provider Requires An Adapter

Ollama, OpenAI, Claude, Gemini, Qwen endpoints, TTS services, messaging
platforms, and storage systems must connect through adapters.

Provider-specific dependencies must not appear inside core engines. Core engines
should remain provider-independent so providers can be replaced, removed, or
combined without rewriting PersonaOS identity, memory, knowledge, skill,
confidence, or evolution logic.

Providers must remain replaceable. Integration convenience must not become
architectural lock-in.

## Principle 13: Engines Own Their Internal Logic

PersonaOS orchestrates engines but does not absorb engine-specific business
logic. The orchestrator coordinates, passes data through boundaries, and
combines prepared outputs.

`ContextBuilder` and `RuntimeContextAssembler` assemble outputs only. They must
not become hidden owners of persona behavior, memory retrieval, knowledge
ranking, confidence evaluation, or evolution decisions.

Fusion interprets relationships between engine outputs without taking ownership
of them. It may describe how persona and memory relate, but it must not become
PersonaEngine or MemoryEngine.

## Principle 14: Frontend Does Not Own Core State

Frontends are interfaces, not sources of truth. Web, mobile, WeChat, Discord,
Telegram, and future clients must call controlled backend boundaries.

UI code must not directly mutate core models or bypass lifecycle rules. The
frontend may present, request, confirm, or review changes, but durable state
changes belong to the appropriate backend engine or lifecycle boundary.

Core state must remain portable across interfaces. A persona should not depend
on one frontend to remain coherent.

## Principle 15: Sensitive Data Requires Consent And Governance

Persona reconstruction may involve private conversations, voice, images, and
relationship history. These materials require careful consent, provenance,
review, and deletion controls.

Import should preserve where data came from, what it was used for, and whether
the user has permission to use it. Sensitive material should not be transformed
into durable persona state without appropriate review.

The system should clearly distinguish a simulated persona from the real person.
PersonaOS should not be used to impersonate a real person deceptively.

## Principle 16: Local-First And User-Controlled

Local storage and local model execution should remain first-class options.
Cloud providers may be supported, but they must remain optional and replaceable.

Users should be able to inspect, export, deactivate, and delete persona data
where technically possible. User control should apply to identity data, memory,
imported sources, versions, and runtime configuration.

Local-first does not forbid cloud integrations. It means cloud services should
not become mandatory owners of PersonaOS state.

## Principle 17: Tests And Documentation Are Part Of Architecture

Every implemented boundary should have tests. Tests help protect architectural
separation from accidental regression.

Architecture-changing work requires documentation synchronization. When code
changes the structure, ownership, or behavior of PersonaOS, the relevant
documents should be updated in the same development flow unless explicitly
deferred.

Do not record features as completed before implementation and verification.
Keep test status and current phase consistent across project documents.

## Architectural Review Checklist

Before merging a feature, ask:

- Does it preserve engine ownership?
- Does it introduce provider-specific code into core modules?
- Does it mutate durable identity during runtime?
- Does it bypass review or lifecycle validation?
- Does it edit historical versions?
- Does it confuse memory with knowledge?
- Does it confuse expression with personality?
- Does it preserve local-first operation?
- Does it include tests?
- Are project documents synchronized?

## Amendment Rule

These principles are durable but not unchangeable. PersonaOS may evolve, and its
architecture may need to change as the system becomes more capable.

A change to these principles requires an explicit architecture decision. The
decision must document the reason for the change, the expected impact, the
migration plan, and the affected boundaries.

Principles must not be weakened casually for implementation convenience. If a
feature is difficult to build within these boundaries, that difficulty should
trigger design review before the boundaries are changed.
